# Script requires port 6789 from the dataland server to be forwarded to the executing machine

import requests
from time import strftime, localtime


from dataland_analytics.config import *

token_url = 'http://dataland-admin:6789/keycloak/realms/master/protocol/openid-connect/token'
body = {'grant_type': 'password', 'username': KEYCLOAK_USERNAME, 'password': KEYCLOAK_PASSWORD,
        'client_id': 'admin-cli', 'client_secret': ''}
token_resp = requests.post(url=token_url, data=body).json()
token = token_resp['access_token']
url = 'http://dataland-admin:6789/keycloak/admin/realms/datalandsecurity/users/'
headers = {"Authorization": "Bearer " + token}
params1 = {"Enabled": "true", "emailVerified": "false", "max": "10000"}
params2 = {"Enabled": "true", "emailVerified": "true", "max": "10000"}
params3 = {"Enabled": "true", "max": "10000"}

UnverifiedUsers = requests.get(url=url, headers=headers, params=params1).json()  # This request also lists 3 technical
# users which should not be included in the analytics
verifiedUsers = requests.get(url=url, headers=headers, params=params2).json()
totalUsers = requests.get(url=url, headers=headers, params=params3).json()  # This request does not include the 3
# technical users for unknown reasons. Anyway, this is the desired number

unverifiedIDs = [entry['id'] for entry in UnverifiedUsers]
verifiedIDs = [entry['id'] for entry in verifiedUsers]
totalIDs = [entry['id'] for entry in totalUsers]
technicalUsers = set(unverifiedIDs) - set(totalIDs)
# print(len(technicalUsers))
# print(technicalUsers)

for entry in technicalUsers:
    pass
    # print("duplicate index: " + str(list(unverifiedIDs).index(entry)))

numberOfTechnicalUsers = 3
print("We have " + str(len(UnverifiedUsers) - numberOfTechnicalUsers) + " enabled, but unverified users on Dataland")
print("We have " + str(len(verifiedUsers)) + " enabled and e-mail verified users on Dataland")
print("We have " + str(len(totalUsers)) + " total signed up users on Dataland")

beforeTimestamp = 1709251200000 #Desired cutoff timestamp in Epoch
datestring = strftime('%Y-%m-%d', localtime(beforeTimestamp/1000)) #Converting from millisecond epoch to second epoch
idsSquared = [UnverifiedUsers, verifiedUsers, totalUsers]
for ids in idsSquared:
    for id in ids:
        if id['createdTimestamp']>beforeTimestamp:
            ids.remove(id)

print("At "+datestring+" we had " + str(len(UnverifiedUsers) - numberOfTechnicalUsers) + " enabled, but unverified users on Dataland")
print("At "+datestring+" we had "+ str(len(verifiedUsers)) + " enabled and e-mail verified users on Dataland")
print("At "+datestring+" we had "+ str(len(totalUsers)) + " total signed up users on Dataland")
