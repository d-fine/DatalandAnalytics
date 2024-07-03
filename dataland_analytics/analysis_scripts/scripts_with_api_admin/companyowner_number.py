import dataland_requests
from dataland_requests.models.company_role import CompanyRole
from dataland_analytics.config import *
import pandas as pd

pd.options.display.max_columns = 20
pd.options.display.max_rows = 20

requests_configuration = dataland_requests.Configuration(
    host=DATALAND_SERVER + "community",
    access_token=PERSONAL_USER_API_KEY
)

with dataland_requests.ApiClient(requests_configuration) as api_client:
    api_instance = dataland_requests.CompanyRolesControllerApi(api_client)
    request_list = api_instance.get_company_role_assignments(role=CompanyRole.COMPANYOWNER)
    company_owner_df = pd.DataFrame([entry.to_dict() for entry in request_list])

    print(f"\nWe have currently {len(company_owner_df)} Company Owners.\n")
    print(f"Overview over all company owners.\n {company_owner_df[['companyId', 'userId']]}")
