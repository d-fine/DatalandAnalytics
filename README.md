# DatalandAnalytics
This repository hosts scripts to perform data anlytics of Dataland.
For more information about Dataland refer to http://dataland.com and its repository at https://github.com/d-fine/dataland.

The different scripts require different access levels to the application with some only requiring read access to the API whereas others do need elevated rights. These elevated rights cannot be granted to open source collaborators.

## Installation and execution
1. Create a Python Virtual Environment, activate it and install the requirements:
```
python3 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```
2. Install the code base in editable state to ensure that imports are working as expected
```
pip install -e .
```

3. Create and install Python Clients of the Dataland APIs
   * Install [openapi-generator-cli](https://github.com/OpenAPITools/openapi-generator) on your machine
   * Navigate to the [datasets folder](api_clients/datasets_api/) and execute 

      ```
	  openapi-generator-cli generate -g python -i ./datasets_open_api.yaml --additional-properties=packageName=dataland-datasets
	  ```

   * After generation, change the package `NAME` in the [setup.py](api_clients/datasets_api/setup.py) file from `openapi-client` to `dataland_datasets_client`
   * Install die client to your python environment by running `pip install .` in the [datasets_api folder](api_clients/datasets_api/) after activating your virtual environment
   * Repeat process for the [documents_api](api_clients/documenta_api) and the [requests_api](api_clients/requests_api/).

4. Generate your api key at https://dataland.com/api-key and put it into [the config file](dataland_analytics/config.py) as `PERSONAL_USER_API_KEY`

5. Execute the analytics scripts found in [this folder](dataland_analytics/analysis_scripts/). Some of them might require additional setup for succesful execution which is described in the script itself

If the software stops working on your machine, this might be caused by an update of the 

## License
This project is free and open-source software licensed under the [GNU Affero General Public License v3](LICENSE) (AGPL-3.0). Commercial use of this software is allowed. If derivative works are distributed, you need to be published the derivative work under the same license. Here, derivative works includes web publications. That means, if you build a web service using this software, you need to publish your source code under the same license (AGPL-3.0)

In case this does not work for you, please contact dataland@d-fine.de for individual license agreements.

## Contributions
Contributions are highly welcome. Please refer to our [contribution guideline](contribution/contribution.md).
To allow for individual licenses and eventual future license changes, we require a contributor license agreement from any contributor that allows us to re-license the software including the contribution.
