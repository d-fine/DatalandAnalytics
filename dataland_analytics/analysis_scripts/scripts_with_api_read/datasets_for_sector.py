import dataland_datasets
from dataland_analytics.config import *
from dataland_datasets.models.data_meta_information import DataMetaInformation
from dataland_datasets.models.data_type_enum import DataTypeEnum
from dataland_datasets.models.company_associated_data_sfdr_data import CompanyAssociatedDataSfdrData
from dataland_datasets.models.company_associated_data_eu_taxonomy_data_for_financials import CompanyAssociatedDataEuTaxonomyDataForFinancials
from typing import List
import os

SECTOR = 'Financials'
# Root folder of your choice to save results
RESULT_ROOT = 'C:/temp/dala_dump_dataset_script'

configuration = dataland_datasets.Configuration(
	host = "https://dataland.com/api",
	access_token=PERSONAL_USER_API_KEY
)

def dump_metainfo_and_dataset_to_txt(meta_info: DataMetaInformation, data_set, company_name):
	path = RESULT_ROOT+'/'+str(meta_info.data_type.name)+'_'+meta_info.reporting_period+'_'+company_name
	backup_path = RESULT_ROOT+'/'+str(meta_info.data_type.name)+'_'+meta_info.reporting_period+'_'+company_info.company_id
	if not os.path.exists(path):
		try:
			os.makedirs(path)
		except:
			path = backup_path
			os.makedirs(backup_path)
	with open(path+'/Metadata.json', 'w+', encoding='utf-8') as text_file:
		text_file.write(meta_info.to_str())
	with open(path+'/Dataset.json', 'w+', encoding='utf-8') as text_file:
		text_file.write(data_set.to_str())


with dataland_datasets.ApiClient(configuration) as api_client:
	
	# Get metadata of all datasets in SFDR and EU Taxonomy
	meta_data_api_instance = dataland_datasets.MetaDataControllerApi(api_client)
	sfdr_meta_data_info = meta_data_api_instance.get_list_of_data_meta_info(show_only_active=True, data_type='sfdr')
	eu_taxo_meta_data_info = meta_data_api_instance.get_list_of_data_meta_info(show_only_active=True, data_type='eutaxonomy-financials')
	all_meta_info = sfdr_meta_data_info + eu_taxo_meta_data_info
	
	# Filter for companies that are in the Financials sector
	# financials_meta_info = all_meta_info
	financials_meta_info: List[DataMetaInformation] = list()
	company_api_instance = dataland_datasets.CompanyDataControllerApi(api_client)
	for item in all_meta_info:
		company_info = company_api_instance.get_company_by_id(company_id=item.company_id)
		if company_info.company_information.sector==SECTOR:
			financials_meta_info.append(item)

	# Fetch the identified datasets and dump them to json text files
	sfdr_api_instance = dataland_datasets.SfdrDataControllerApi(api_client)
	eu_taxo_api_instance = dataland_datasets.EuTaxonomyDataForFinancialsControllerApi(api_client)
	sfdr_data_sets: List[CompanyAssociatedDataSfdrData] = list()
	eu_taxo_data_sets = []
	for item in financials_meta_info:
		if item.data_type == DataTypeEnum.SFDR:
			dataset = sfdr_api_instance.get_company_associated_sfdr_data(item.data_id)
			company_info = company_api_instance.get_company_by_id(company_id=item.company_id)
			sfdr_data_sets.append(dataset)
			dump_metainfo_and_dataset_to_txt(item, dataset, company_info.company_information.company_name)
		if item.data_type == DataTypeEnum.EUTAXONOMY_MINUS_FINANCIALS:
			dataset = eu_taxo_api_instance.get_company_associated_eu_taxonomy_data_for_financials(item.data_id)
			company_info = company_api_instance.get_company_by_id(company_id=item.company_id)
			eu_taxo_data_sets.append(dataset)
			dump_metainfo_and_dataset_to_txt(item, dataset, company_info.company_information.company_name)