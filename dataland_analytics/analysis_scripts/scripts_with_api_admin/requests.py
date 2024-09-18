"""
This module provides helper functions to search for requests and find corresponding pending datasets.
"""
from datetime import datetime

import dataland_community
import pandas as pd
from dataland_community import RequestStatus
from dataland_datasets import DataMetaInformation, StoredCompany

from api_clients.community_api.dataland_community.models.extended_stored_data_request import ExtendedStoredDataRequest
from dataland_analytics.config import *
from datasets import get_pending_datasets, get_metadata_for_dataset, get_company_data_by_company_id
from export_nonfinancial_dataset_to_excel import adjust_excel_column_widths
from formatting_utils import get_readable_datatype_string_from_input, get_enum_value, timestamp_in_ms_to_datetime


def search_requests(criteria: dict) -> list[ExtendedStoredDataRequest]:
    """
    Search data requests according to search criteria via the community service's admin endpoint. For more information
    regarding the search criteria, see the API description at
    https://dataland.com/community/swagger-ui/index.html#/request-controller/getDataRequests
    :param criteria: A dictionary of search criteria.
    :return: a list of data requests
    """
    community_api_configuration = dataland_community.Configuration(host=DATALAND_SERVER + "community",
                                                                   access_token=PERSONAL_USER_API_KEY)

    # GET REQUEST BY FILTER
    with dataland_community.ApiClient(community_api_configuration) as community_api_client:
        request_controller_api_instance = dataland_community.RequestControllerApi(
            api_client=community_api_client
        )

        requests_by_criteria = request_controller_api_instance.get_data_requests(**criteria)

    return [req for req in requests_by_criteria]


def get_pending_datasets_for_requests(requests: list[ExtendedStoredDataRequest]) -> list[DataMetaInformation]:
    """
    This function filters out from the list of pending datasets all those which match a request of the input
    :param requests: requests to find the pending datasets for
    :return: list of matching datasets
    """
    pending_dataset_ids = get_pending_datasets()
    pending_datasets_metadata = get_metadata_for_dataset(*pending_dataset_ids)

    matching_datasets = []
    for dataset_metadata in pending_datasets_metadata:
        for req in requests:
            if is_match(dataset_metadata, req):
                matching_datasets.append(dataset_metadata)

    return matching_datasets


def find_pending_datasets_for_requests(requests: list[ExtendedStoredDataRequest]) -> list[DataMetaInformation]:
    """
    This function filters out from the list of pending datasets all those which match a request of the input
    :param requests: requests to find the pending datasets for
    :return: list of matching datasets
    """
    pending_dataset_ids = get_pending_datasets()
    pending_datasets_metadata = get_metadata_for_dataset(*pending_dataset_ids)

    matching_datasets = []
    for dataset_metadata in pending_datasets_metadata:
        for req in requests:
            if is_match(dataset_metadata, req):
                matching_datasets.append(dataset_metadata)

    return matching_datasets


def filter_requests_updated_later_than_threshold(requests: list[ExtendedStoredDataRequest], timestamp: datetime)\
        -> list[ExtendedStoredDataRequest]:
    """
    Filter list of requests by timestamp
    :param requests: list of requests
    :param timestamp: datetime threshold
    :return: list of matching ExtendedStoredDataRequests
    """
    return list(filter(lambda req: timestamp_in_ms_to_datetime(req.last_modified_date) > timestamp, requests))


def is_match(data: DataMetaInformation, req: ExtendedStoredDataRequest) -> bool:
    """
    Returns true if dataset matches the request
    :param data: dataset
    :param req: request
    :return: bool
    """
    return (data.data_type == req.data_type and data.reporting_period == req.reporting_period
            and data.company_id == req.dataland_company_id)


def format_request_for_export(*requests: ExtendedStoredDataRequest) -> list[dict]:
    keys_map = {
        'dataRequestId': 'Request ID',
        'userEmailAddress': 'Requester',
        'creationTimestamp': 'Date of Request',
        'dataType': 'Framework',
        'reportingPeriod': 'Reporting Period',
        'datalandCompanyId': 'Company ID',
        'companyName': 'Company',
        'lastModifiedDate': 'Last Update of Request',
        'requestStatus': 'Status',
    }
    values_map = {
        'dataType': get_readable_datatype_string_from_input,
        'creationTimestamp': timestamp_in_ms_to_datetime,
        'lastModifiedDate': timestamp_in_ms_to_datetime,
        'requestStatus': get_enum_value,
    }

    return [{keys_map[key]: values_map[key](value) if key in values_map else value
            for key, value in req.to_dict().items() if key in keys_map} for req in requests]


def export_requests_to_excel(requests: list[dict], path: str, exclude_columns=None):
    if len(requests) > 0:
        requests_dataframe = pd.DataFrame.from_records(requests, exclude=exclude_columns)
        with pd.ExcelWriter(path=path, engine="openpyxl",
                            mode='w', datetime_format='YYYY-MM-DD HH:MM:SS') as excel_writer:
            requests_dataframe.to_excel(excel_writer, sheet_name="Overview")
        adjust_excel_column_widths(file_name)
        print("Export finished.")
    else:
        print("No requests matching the filters found")


if __name__ == "__main__":
    # DEFINE FILTER PARAMETERS
    search_parameters = {
        "data_type": ["eutaxonomy-financials", "eutaxonomy-non-financials"],
        "email_address": "enter_substring_here",
        "chunk_size": 500,
        "chunk_index": 0,
    }

    # GET REQUESTS AND MATCHING PENDING DATASETS
    requests_for_search: list[ExtendedStoredDataRequest] = search_requests(search_parameters)
    matching_pending_datasets: list[DataMetaInformation] = get_pending_datasets_for_requests(requests_for_search)
    answered_requests_for_search: list[ExtendedStoredDataRequest] = \
        list(filter(lambda req: getattr(req, 'request_status') == RequestStatus.ANSWERED, requests_for_search))
    newest_answered_requests_for_search: list[ExtendedStoredDataRequest] = \
        filter_requests_updated_later_than_threshold(answered_requests_for_search,
                                                     datetime.strptime("2024-09-17", '%Y-%m-%d'))

    # GET DATASET_IDS FOR ANSWERED REQUESTS
    dataset_ids_for_answered_requests = []
    for request in answered_requests_for_search:
        company_id = request.dataland_company_id
        company_data: StoredCompany = get_company_data_by_company_id(company_id)[0]
        for dataset in company_data.data_registered_by_dataland:
            if (dataset.data_type == request.data_type and dataset.reporting_period == request.reporting_period
                    and dataset.currently_active):
                dataset_ids_for_answered_requests.append(dataset.data_id)

    # PREPARE REQUESTS FOR OUTPUT
    formatted_requests = []

    for request in requests_for_search:
        formatted_request = format_request_for_export(request)[0]
        if any([is_match(dataset, request) for dataset in matching_pending_datasets]):
            formatted_request['Status'] = 'Pending'
        formatted_requests.append(formatted_request)

    print(f"Total number of requests: {len(requests_for_search)}")
    print(f"Total number of matching pending datasets: {len(matching_pending_datasets)}")
    print(f"Total number of answered requests: {len(answered_requests_for_search)}")
    print(f"Number of newest answered requests: {len(newest_answered_requests_for_search)}")
    print(f"Dataset Ids for answered requests {[dataset_id for dataset_id in dataset_ids_for_answered_requests]}")

    # EXPORT
    file_name = f"./NordLB_Data_Requests_Overview_{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    export_requests_to_excel(requests=formatted_requests, path=file_name, exclude_columns=["Request ID", "Company ID"])
