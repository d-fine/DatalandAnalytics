import dataland_datasets
from dataland_analytics.config import *
import pandas as pd
results = []

configuration = dataland_datasets.Configuration(
	host = "https://dataland.com/api",
	access_token = PERSONAL_USER_API_KEY
)

with dataland_datasets.ApiClient(configuration) as api_client:

	metadata_api_instance = dataland_datasets.MetaDataControllerApi(api_client)
	meta_data = metadata_api_instance.get_list_of_data_meta_info(show_only_active=True)
	company_api_instance = dataland_datasets.CompanyDataControllerApi(api_client)
	for item in meta_data:
		company_info = company_api_instance.get_company_by_id(item.company_id)
		if company_info.company_information.sector is None:
			results.append({'Company Name': company_info.company_information.company_name, 'LEI': company_info.company_information.identifiers['Lei']})

	df = pd.DataFrame(results)
	df.to_csv('results.csv', index=False)