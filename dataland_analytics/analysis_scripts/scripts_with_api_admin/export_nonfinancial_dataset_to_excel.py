import dataland_community
import dataland_datasets
import dataland_qa
import numpy as np
import openpyxl
import pandas as pd
from openpyxl.styles import Alignment

from dataland_analytics.config import *
from datasets import create_link_to_dataset, get_metadata_for_dataset

"""
Export all provided datasets to excel sheets
"""
# ## CONFIGURATION
dataset_api_configuration = dataland_datasets.Configuration(
    host=DATALAND_SERVER + "api", access_token=PERSONAL_USER_API_KEY
)

community_api_configuration = dataland_community.Configuration(
    host=DATALAND_SERVER + "community", access_token=PERSONAL_USER_API_KEY
)

qa_api_configuration = dataland_qa.Configuration(
    host=DATALAND_SERVER + "qa", access_token=PERSONAL_USER_API_KEY,
)


def update_entries(entry):
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
    sanitized = sanitized.map(update_entries)
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


def adjust_excel_column_widths(path):
    workbook = openpyxl.load_workbook(path)
    for sheet in workbook:
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter  # Get the column letter

            for cell in column:
                cell.alignment = Alignment(horizontal='left')
                if getattr(cell, "value") is not None:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))

            adjusted_width = (max_length + 2)  # Add some padding
            sheet.column_dimensions[column_letter].width = adjusted_width

    workbook.save(path)


# ## SET DATASET IDS TO BE EXPORTED
dataset_ids = ['b62df13d-6c74-48ca-9a12-f798ccbe65f7', '34ed549a-5d76-44a6-9072-0bc055ecec34']

substrings_to_be_filtered_out = ['file', 'quality', 'comment', 'dataSource', 'referencedReports',]
regex_pattern = '|'.join(substrings_to_be_filtered_out)

pd.set_option("display.max_rows", 20)
pd.set_option("display.max_columns", 30)

with (dataland_datasets.ApiClient(dataset_api_configuration) as dataset_api_client):
    non_financials_controller_api_instance = dataland_datasets.EutaxonomyNonFinancialsDataControllerApi(
        api_client=dataset_api_client
    )

    company_data_controller_api_instance = dataland_datasets.CompanyDataControllerApi(
        api_client=dataset_api_client
    )

    for dataset_id in dataset_ids:
        dataset = non_financials_controller_api_instance.get_company_associated_eutaxonomy_non_financials_data(
            dataset_id
        )

        metadata = get_metadata_for_dataset(dataset_id)

        flat_dataframe = pd.json_normalize(dataset.data.to_dict())
        sanitized_dataframe = sanitize_dataframe(flat_dataframe, regex_pattern)
        merge_connected_value_currency_columns(sanitized_dataframe)
        sanitized_dataframe.columns = [prettify_header_strings(col) for col in sanitized_dataframe.columns]

        # Write general data
        company_data = company_data_controller_api_instance.get_company_by_id(dataset.company_id)

        file_name = (f"EU-Taxonomy-Non-Financial_{company_data.company_information.company_name}"
                     f"_{dataset.reporting_period}.xlsx")

        with pd.ExcelWriter(path=file_name, engine="openpyxl", datetime_format='YYYY-MM-DD HH:MM:SS',
                            mode='w') as excel_writer:
            columns_to_export = sanitized_dataframe.columns[~sanitized_dataframe.columns.str.contains('Activities')]
            dataframe_to_export = sanitized_dataframe[columns_to_export]
            hyperlink_to_data = create_link_to_dataset(metadata[0])
            dataframe_to_export.insert(0, "Link to Dataset", hyperlink_to_data)
            dataframe_to_export.insert(1, "", np.NaN)

            dataframe_to_export.transpose().to_excel(excel_writer, sheet_name="General Data", header=False)

            sheet = excel_writer.book.active
            sheet['B1'].hyperlink = hyperlink_to_data
            sheet['B1'].style = 'Hyperlink'

        # Create Activity sheets
        activities_col = [col for col in sanitized_dataframe.columns if 'Activities' in col]

        if len(activities_col) == 0:
            continue

        for col in activities_col:
            activity_series = sanitized_dataframe[col]
            sheet_name = activity_series.name

            # create dataframe from only entry in activity series
            activity_dataframe = pd.DataFrame(activity_series.loc[0])
            # create dataframe from 'share' field in activity_dataframe and concat both to have a flattened dataframe
            share_dataframe = pd.json_normalize(activity_dataframe['share'])
            activity_dataframe = pd.concat([activity_dataframe.drop(columns='share'), share_dataframe], axis=1)
            merge_connected_amount_currency_columns(activity_dataframe)
            activity_dataframe = activity_dataframe.map(update_entries)
            activity_dataframe.columns = [prettify_header_strings(col) for col in activity_dataframe.columns]

            with pd.ExcelWriter(path=file_name, engine="openpyxl", datetime_format='YYYY-MM-DD HH:MM:SS',
                                mode='a') as excel_writer:
                activity_dataframe.to_excel(excel_writer, sheet_name=sheet_name,)

        adjust_excel_column_widths(file_name)
