import dataland_community
import dataland_datasets
import pandas as pd

from dataland_analytics.config import *

user_id = ""

# If only requests of specific time are desired set start and end epoch variables
start_epoch = 1714521600000
end_epoch = 1717200000000

# noinspection PyInterpreter
datasets_configuration = dataland_datasets.Configuration(
    host=DATALAND_SERVER + "api", access_token=PERSONAL_USER_API_KEY
)

requests_configuration = dataland_community.Configuration(
    host=DATALAND_SERVER + "community", access_token=PERSONAL_USER_API_KEY
)

result_dicts = []

with dataland_community.ApiClient(requests_configuration) as api_client:
    api_instance = dataland_community.RequestControllerApi(api_client)
    request_list = api_instance.get_data_requests()
    if "start_epoch" in locals():
        request_list = [
            r
            for r in request_list
            if (start_epoch < r.creation_timestamp < end_epoch)
        ]

with dataland_datasets.ApiClient(datasets_configuration) as api_client:
    company_api_instance = dataland_datasets.CompanyDataControllerApi(
        api_client=api_client
    )
    metadata_api_instance = dataland_datasets.MetaDataControllerApi(
        api_client=api_client
    )
    for request in request_list:
        company = company_api_instance.get_company_by_id(
            company_id=request.dataland_company_id
        )
        matching_dataset = metadata_api_instance.get_list_of_data_meta_info(
            company_id=request.dataland_company_id,
            data_type=request.data_type,
            show_only_active=True,
            reporting_period=request.reporting_period,
        )
        exists = True if matching_dataset else False
        result_dicts.append(
            {
                "Company_name": company.company_information.company_name,
                "LEI": company.company_information.identifiers["Lei"][0],
                "Framework": request.data_type,
                "Year": request.reporting_period,
                "Exists": exists,
            }
        )

result = pd.DataFrame.from_records(result_dicts)
result.to_csv("specific_user_requests.csv", index=False)
