"""
This module allows to export datasets to excel.
"""

import dataland_datasets
import dataland_qa
import pandas as pd
from dataland_datasets import DataMetaInformation, StoredCompany
from dataland_qa import ReviewQueueResponse

from dataland_analytics.config import *


def get_pending_datasets() -> list[ReviewQueueResponse]:
    qa_api_configuration = dataland_qa.Configuration(host=DATALAND_SERVER + "qa", access_token=PERSONAL_USER_API_KEY)
    with dataland_qa.ApiClient(qa_api_configuration) as qa_api_client:
        qa_controller_api_instance = dataland_qa.QaControllerApi(api_client=qa_api_client)

        return qa_controller_api_instance.get_info_on_unreviewed_datasets()


def get_metadata_for_dataset(*dataset_ids) -> list[DataMetaInformation]:
    dataset_api_configuration = dataland_datasets.Configuration(host=DATALAND_SERVER + "api",
                                                                access_token=PERSONAL_USER_API_KEY)

    with dataland_datasets.ApiClient(dataset_api_configuration) as dataset_api_client:
        metadata_controller_api_instance = dataland_datasets.MetaDataControllerApi(api_client=dataset_api_client)

        return [metadata_controller_api_instance.get_data_meta_info(dataset_id) for dataset_id in dataset_ids]


def get_company_data_by_company_id(*company_ids: str) -> list[StoredCompany]:
    dataset_api_configuration = dataland_datasets.Configuration(host=DATALAND_SERVER + "api",
                                                                access_token=PERSONAL_USER_API_KEY)
    with (dataland_datasets.ApiClient(dataset_api_configuration) as dataset_api_client):
        company_data_controller_api_instance = dataland_datasets.CompanyDataControllerApi(api_client=dataset_api_client)

        return [company_data_controller_api_instance.get_company_by_id(company_id) for company_id in company_ids]


def replace_enum_entries_with_value(entry):
    """
    Effectively: if entry is of enum type, return entry.value, else keep entry as is
    :param entry:
    :return:
    """
    return entry.value if entry is not None and hasattr(entry, 'value') and entry.value else entry


def sanitize_dataframe(dataframe: pd.DataFrame, str_pattern='') -> pd.DataFrame:
    """
    Sanitizes dataframe, i.e. delete irrelevant and empty columns, columns containing empty lists, and replace enum type
    entries with their corresponding value
    :param dataframe:
    :param str_pattern:
    :return:
    """
    # deletes columns with name matching pattern
    sanitized = dataframe.loc[:, ~dataframe.columns.str.contains(str_pattern)]
    # deletes columns with empty rows
    sanitized.dropna(axis=1, how='all')
    # deletes columns with entry '[]' (empty list)
    sanitized = sanitized.loc[:, ~sanitized.apply(lambda rows: (all(isinstance(entry, list)
                                                                    and len(entry) == 0 for entry in rows)))]
    sanitized = sanitized.map(replace_enum_entries_with_value)
    return sanitized


def merge_connected_value_currency_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Merge value-currency pairs of columns. Only works for prettified column headers
    :param dataframe:
    :return:
    """
    for col in dataframe.columns:
        if col.endswith('value'):
            currency_col_name = col.replace('value', 'currency')

            if currency_col_name in dataframe.columns:
                dataframe[col.replace('value', '')] = dataframe[col].astype(str) + ' ' + dataframe[currency_col_name]
                dataframe.drop(columns=[currency_col_name, col], inplace=True)
    return dataframe


def merge_connected_amount_currency_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Merge value-currency pairs of columns. Only works for prettified column headers
    :param dataframe:
    :return:
    """
    for col in dataframe.columns:
        if col.endswith('amount'):
            currency_col_name = col.replace('amount', 'currency')

            if currency_col_name in dataframe.columns:
                dataframe[col] = dataframe[col].astype(str) + ' ' + dataframe[currency_col_name]
                dataframe.drop(columns=[currency_col_name], inplace=True)
    return dataframe


def prettify_header_strings(input_string):
    """
    prettify the column header strings
    :param input_string:
    :return:
    """
    parts = input_string.split('.')
    titled_parts = []
    for part in parts:
        if part != 'value':
            spaced_part = ''.join([char if char.islower() else ' ' + char for char in part])
            titled_parts.append(spaced_part.title())

    return ' '.join(titled_parts)
