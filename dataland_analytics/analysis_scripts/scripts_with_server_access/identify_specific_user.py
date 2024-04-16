# Script requires port 6789 from the dataland server to be forwarded to the executing machine
import requests
from dataland_analytics.config import *

#Set this id before running the script
KEYCLOAK_USER_ID = ''

# Setup for communication with Keycloak API
token_url='http://dataland-admin:6789/keycloak/realms/master/protocol/openid-connect/token'
body={'grant_type':'password','username':KEYCLOAK_USERNAME,'password':KEYCLOAK_PASSWORD,'client_id':'admin-cli','client_secret':''}
token_resp = requests.post(url=token_url, data=body).json()
token = token_resp['access_token']
headers = {"Authorization": "Bearer "+token}
url_stub = 'http://dataland-admin:6789/keycloak/admin/realms/datalandsecurity/'

# Get user ID
url = url_stub+'users/'+KEYCLOAK_USER_ID
resp = requests.get(url=url,headers=headers).json()
print(resp)