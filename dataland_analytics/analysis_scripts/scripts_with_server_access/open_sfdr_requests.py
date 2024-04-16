# Script requires port 6789 from the dataland server to be forwarded to the executing machine
# Script requires USER_API_KEY with admin priviliges

import dataland_datasets
import dataland_requests
from dataland_analytics.config import *
from dataland_requests.models.request_status import RequestStatus
import requests
import pandas as pd

# Configuration for community API
requests_configuration = dataland_datasets.Configuration(
	host = "https://dataland.com/community",
	access_token=PERSONAL_USER_API_KEY
)

# Configuration for datasets API
datasets_configuration = dataland_datasets.Configuration(
	host = "https://dataland.com/api",
	access_token=PERSONAL_USER_API_KEY
)

# Setup for communication with Keycloak API
token_url='http://dataland-admin:6789/keycloak/realms/master/protocol/openid-connect/token'
body={'grant_type':'password','username':KEYCLOAK_USERNAME,'password':KEYCLOAK_PASSWORD,'client_id':'admin-cli','client_secret':''}
token_resp = requests.post(url=token_url, data=body).json()
token = token_resp['access_token']
headers = {"Authorization": "Bearer "+token}
url_stub = 'http://dataland-admin:6789/keycloak/admin/realms/datalandsecurity/'


# Get a list of all open SFDR requests with userId and companyId
with dataland_requests.ApiClient(requests_configuration) as api_client:
	api_instance = dataland_requests.RequestControllerApi(api_client)
	all_sfdr_requests = api_instance.get_data_requests(
		request_status=RequestStatus.OPEN,
		  data_type='sfdr')
	
#For each request replace company id with name for readability
with dataland_datasets.ApiClient(datasets_configuration) as api_client:
	api_instance = dataland_datasets.CompanyDataControllerApi(api_client)
	for request in all_sfdr_requests:
		company = api_instance.get_company_by_id(request.dataland_company_id)
		request.dataland_company_id=company.company_information.company_name

#For each request replace user id with name for readability
for request in all_sfdr_requests:
	url = url_stub+'users/'+request.user_id
	resp = requests.get(url=url,headers=headers).json()
	try:
		request.user_id =resp['firstName']+" "+resp['lastName']+" "+resp["email"]
	except:
		try: request.user_id =resp["email"]
		except: request.user_id =resp["username"]

result_list = []
for request in all_sfdr_requests:
	result_list.append({'Framework':request.data_type,'CompanyName':request.dataland_company_id,'ReportingPeriod':request.reporting_period,'Creator':request.user_id})

result_frame = pd.DataFrame.from_records(result_list).sort_values(by=['CompanyName','ReportingPeriod','Creator'])
print(result_frame)
result_frame.to_csv('sfdr_requests.csv',index=False)