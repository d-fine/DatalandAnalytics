import dataland_datasets
import dataland_datasets.configuration
from dataland_analytics.config import *
from dataland_datasets.models.data_type_enum import DataTypeEnum

configuration = dataland_datasets.Configuration(
    host=DATALAND_SERVER + "api", access_token=PERSONAL_USER_API_KEY
)

sfdr_companies = []
eu_taxonomy_companies = []
other_companies = []

with dataland_datasets.ApiClient(configuration) as api_client:
    meta_data_api_instance = dataland_datasets.MetaDataControllerApi(api_client)
    datasets = meta_data_api_instance.get_list_of_data_meta_info(show_only_active=True)
    company_data_api_instance = dataland_datasets.CompanyDataControllerApi(api_client)
    for dataset in datasets:
        company = company_data_api_instance.get_company_by_id(dataset.company_id)
        if company.company_information.sector:
            continue
        company_repr = {'id':company.company_id,
                        'name':company.company_information.company_name,
                        'Lei':company.company_information.identifiers['Lei']}
        match dataset.data_type:
            case DataTypeEnum.SFDR:
                sfdr_companies.append(company_repr)
            case DataTypeEnum.EUTAXONOMY_MINUS_NON_MINUS_FINANCIALS:
                eu_taxonomy_companies.append(company_repr)
            case _:
                other_companies.append(company_repr)
print(sfdr_companies)
print(eu_taxonomy_companies)
print(other_companies)