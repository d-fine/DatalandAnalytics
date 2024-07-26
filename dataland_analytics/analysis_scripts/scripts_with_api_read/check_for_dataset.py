# Check for a list of companies if SFDR data sets exists for reporting periods 2022 and 2023

import dataland_datasets
import pandas as pd

from dataland_analytics.config import *

configuration = dataland_datasets.Configuration(
    host=DATALAND_SERVER + "api", access_token=PERSONAL_USER_API_KEY
)

company_ids = [
    "a3b02fec-d9db-4af8-8698-3b2c7ec6e396",
    "61615c24-747b-431d-91b5-798a38f42a17",
    "58a603dc-f53c-4499-add1-1c463b129aba",
]

with dataland_datasets.ApiClient(configuration) as api_client:
    company_controller_api_instance = dataland_datasets.CompanyDataControllerApi(
        api_client
    )
    company_dicts = []
    for company_id in company_ids:
        company_info = company_controller_api_instance.get_company_by_id(company_id)
        company_dicts.append(
            {
                "company_name": company_info.company_information.company_name,
                "LEI": company_info.company_information.identifiers["Lei"][0],
                "company_id": company_id,
            }
        )

df = pd.DataFrame.from_records(company_dicts)
df.to_csv("list_of_companies.csv", index=False, header=True)

no_data = []
data_2022 = []
data_2023 = []

with dataland_datasets.ApiClient(configuration) as api_client:
    sfdr_data_api_instance = dataland_datasets.SfdrDataControllerApi(api_client)
    for company_dict in company_dicts:
        sfdr_data_sets = sfdr_data_api_instance.get_all_company_sfdr_data(
            company_id=company_dict["company_id"], show_only_active=True
        )
        if len(sfdr_data_sets) == 0:
            no_data.append(company_dict)
            continue
        for data_set in sfdr_data_sets:
            if data_set.meta_info.reporting_period == "2023":
                data_2023.append(company_dict)
                continue
            if data_set.meta_info.reporting_period == "2022":
                data_2022.append(company_dict)

df_no_data = pd.DataFrame.from_records(no_data)
df_no_data.to_csv("list_of_no_data_companies.csv", index=False, header=True)

data_2022 = pd.DataFrame.from_records(data_2022)
data_2022.to_csv("list_of_2022_data_companies.csv", index=False, header=True)

data_2023 = pd.DataFrame.from_records(data_2023)
data_2023.to_csv("list_of_2023_data_companies.csv", index=False, header=True)
