import dataland_datasets
import pandas as pd

from dataland_analytics.config import *

configuration = dataland_datasets.Configuration(
    host=DATALAND_SERVER + "api", access_token=PERSONAL_USER_API_KEY
)

company_ids = [
    "74abf1b6-6512-4afc-9609-2493180bfb69",
    "a76394c8-013e-44b1-b328-3b8740d51c14",
    "aae8ed94-fd88-422b-b573-ed2427cefecd",
]

with dataland_datasets.ApiClient(configuration) as api_client:
    company_controller_api_instance = dataland_datasets.CompanyDataControllerApi(
        api_client
    )
    list_of_dicts = []
    for company_id in company_ids:
        company_info = company_controller_api_instance.get_company_by_id(company_id)
        list_of_dicts.append(
            {
                "LEI": company_info.company_information.identifiers["Lei"][0],
                "company_id": company_id,
                "company_name": company_info.company_information.company_name,
            }
        )

df = pd.DataFrame.from_records(list_of_dicts)
df.to_csv("result.csv", index=False, header=True)
