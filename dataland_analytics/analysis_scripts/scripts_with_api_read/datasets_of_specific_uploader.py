import dataland_datasets
from dataland_analytics.config import *

user = ""

configuration = dataland_datasets.Configuration(
	host = DATALAND_SERVER + "api",
	access_token=PERSONAL_USER_API_KEY
)

with dataland_datasets.ApiClient(configuration) as api_client:
	meta_data_api_instance = dataland_datasets.MetaDataControllerApi(api_client)
	sfdr_data_sets = meta_data_api_instance.get_list_of_data_meta_info(data_type='sfdr', show_only_active=True)
	uploader_data_sets = []
	for data_set in sfdr_data_sets:
		if data_set.uploader_user_id==user:
			uploader_data_sets.append(data_set)

	uploader_data_sets.sort(key=lambda x: x.upload_time, reverse=True)
print(uploader_data_sets)