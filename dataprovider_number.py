# Script requires port 6789 from the dataland server to be forwarded to the executing machine

from requests.auth import HTTPBasicAuth
import requests

from config import *

token_url='http://dataland-admin:6789/keycloak/realms/master/protocol/openid-connect/token'
body={'grant_type':'password','username':KEYCLOAK_USERNAME,'password':KEYCLOAK_PASSWORD,'client_id':'admin-cli','client_secret':''}
token_resp = requests.post(url=token_url, data=body).json()
token = token_resp['access_token']
url='http://dataland-admin:6789/keycloak/admin/realms/datalandsecurity/roles/ROLE_UPLOADER/users'
headers = {"Authorization": "Bearer "+token}
params = {"Enabled":"true", "emailVerified":"true", "max":"1000"}
resp = requests.get(url=url,headers=headers,params=params).json()
print("We have "+str(len(resp))+" uploaders. They are:")
for user in resp:
	try:
		print(user['firstName']+" "+user['lastName']+" "+user["email"])
	except:
		try: print(user["email"])
		except: print(user["username"])