import pytest
from address_api_client import AddressApiClient

def test_search_department_by_postcode():
  address_api_client = AddressApiClient()
  response = address_api_client.search_department_by_postcode('75012')
  assert response == "Paris (75)"

def test_search_region_by_postcode():
  address_api_client = AddressApiClient()
  response = address_api_client.search_region_by_postcode('75012')
  assert response == "Île-de-France"