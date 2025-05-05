import pytest
from address_api_client import AddressApiClient

def test_search_region_and_department_by_postcode_75012():
  address_api_client = AddressApiClient()
  response = address_api_client.search_region_and_department_by_postcode('75012')
  assert response ==  { "departement": "Paris (75)", "region": "Île-de-France" }

def test_search_region_and_department_by_postcode_91390():
  address_api_client = AddressApiClient()
  response = address_api_client.search_region_and_department_by_postcode('91390')
  assert response ==  {'departement': 'Essonne (91)', 'region': 'Île-de-France'}