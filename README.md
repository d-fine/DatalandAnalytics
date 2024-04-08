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
3. Generate your api key at https://dataland.com/api-key and put it into [the config file](dataland_analytics/config.py) as `PERSONAL_USER_API_KEY`

4. Execute the analytics scripts found in [this folder](dataland_analytics/analysis_scripts/). Some of them might require additional setup for succesful execution which is described in the script itself

## License
This project is free and open-source software licensed under the [GNU Affero General Public License v3](LICENSE) (AGPL-3.0). Commercial use of this software is allowed. If derivative works are distributed, you need to be published the derivative work under the same license. Here, derivative works includes web publications. That means, if you build a web service using this software, you need to publish your source code under the same license (AGPL-3.0)

In case this does not work for you, please contact dataland@d-fine.de for individual license agreements.

## Contributions
Contributions are highly welcome. Please refer to our [contribution guideline](contribution/contribution.md).
To allow for individual licenses and eventual future license changes, we require a contributor license agreement from any contributor that allows us to re-license the software including the contribution.
