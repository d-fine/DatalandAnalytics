from requests.auth import HTTPBasicAuth
import requests
from dataland_analytics.config import *
from collections import Counter


def extractNumnberOfDatasetsPerReportingPeriod(response: list):
	accessKey = 'reportingPeriod'
	reportingPeriods = []
	for entry in response:
		reportingPeriods.append(entry[accessKey])
	return dict(Counter(reportingPeriods))


frameworks = {'sme', 'sfdr', 'p2p', 'lksg', 'heimathafen', 'eutaxonomy-non-financials', 'esg-questionnaire',
			  'eutaxonomy-financials'}
headers = {"Authorization": "Bearer " + PERSONAL_USER_API_KEY}
datasetCountPerFramework = {}
for framework in frameworks:
	url = 'https://dataland.com/api/metadata'
	params = {'showOnlyActive': 'true', 'dataType': framework}
	resp = requests.get(url=url, headers=headers, params=params).json()
	datasetCountPerFramework[framework] = extractNumnberOfDatasetsPerReportingPeriod(resp)
	print("Framework " + framework + " has " + str(datasetCountPerFramework[framework]) + " dataset combinations for a "
																						  "total of " + str(
		len(resp)) + " active datasets.")
