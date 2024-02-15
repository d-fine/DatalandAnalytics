### How to get the information how many companies have company owners on Dataland

* Forward port 6789 and login to PG Admin (See PG Admin page on the internal wiki)
* Navigate to table BackendDb -> Databases -> backend -> Schemas -> Tables -> company_data_owners_entity_data_owners ; data_owner_for_companies
* Check content and length of these tables to figure out how many company owners Dataland has.