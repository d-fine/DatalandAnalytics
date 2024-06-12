import dataland_datasets
from dataland_analytics.config import *
import itertools
import pandas as pd

pd.options.display.max_columns = 20
pd.options.display.max_rows = 20

configuration = dataland_datasets.Configuration(
	host = "https://dataland.com/api",
	access_token=PERSONAL_USER_API_KEY
)

frameworks = ['sme', 'sfdr', 'p2p', 'lksg', 'heimathafen', 'eutaxonomy-non-financials', 'esg-questionnaire',
			  'eutaxonomy-financials']
reporting_periods = ['2020','2021','2022','2023','2024']
result = pd.DataFrame(columns=frameworks, index=reporting_periods)

with dataland_datasets.ApiClient(configuration) as api_client:
	api_instance = dataland_datasets.MetaDataControllerApi(api_client)
	for (framework, year) in list(itertools.product(frameworks,reporting_periods)):
		list_of_meta_data_info = api_instance.get_list_of_data_meta_info(show_only_active=True, data_type=framework, reporting_period=year)
		result.loc[year,framework]=len(list_of_meta_data_info)
		
print(result)
