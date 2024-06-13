import dataland_requests
from dataland_analytics.config import *
from dataland_requests.models.request_status import RequestStatus

OBSERVATION_PERIOD_START_EPOCH = 1714588322000

configuration = dataland_requests.Configuration(
    host="https://dataland.com/community", access_token=PERSONAL_USER_API_KEY
)

with dataland_requests.ApiClient(configuration) as api_client:

    # Get all requests
    requests_api_instance = dataland_requests.RequestControllerApi(api_client)
    requests = requests_api_instance.get_data_requests()

    # Categorize and count requests
    open_requests = 0
    closed_requests = 0
    newly_closed_requests = 0
    newly_opened_requests = 0
    for request in requests:
        if request.creation_timestamp > OBSERVATION_PERIOD_START_EPOCH:
            newly_opened_requests += 1
        if request.request_status == RequestStatus.OPEN:
            open_requests += 1
        if request.request_status in [
            RequestStatus.RESOLVED,
            RequestStatus.CLOSED,
            RequestStatus.ANSWERED,
        ]:
            closed_requests += 1
        if (
            request.request_status
            in [RequestStatus.RESOLVED, RequestStatus.CLOSED, RequestStatus.ANSWERED]
            and request.last_modified_date >= OBSERVATION_PERIOD_START_EPOCH
        ):
            newly_closed_requests += 1

    print(
        f"{open_requests=}\n{closed_requests=}\n{newly_closed_requests=}\n{newly_opened_requests=}"
    )
