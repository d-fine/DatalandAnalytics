from requests.auth import HTTPBasicAuth
import requests
from config import *

frameworks = {'sme','sfdr','p2p','lksg','heimathafen','eutaxonomy-non-financials','esg-questionnaire'}
headers = {"Authorization": "Bearer "+PERSONAL_USER_API_KEY}

for framework in frameworks:
	url='https://dataland.com/api/metadata'
	params = {'showOnlyActive':'true','dataType':framework}
	resp = requests.get(url=url, headers=headers, params=params).json()
	print("Framework "+framework+" has "+str(len(resp))+" active datasets.")