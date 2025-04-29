import pytest
from adress_api_client import AdressApiClient

def test_serch_adress():
  adress_api_client = AdressApiClient()
  response = adress_api_client.search("Paris")
  assert response.status_code == 200
  assert response.json()["features"][0]["properties"]["postcode"] == "75001"

def test_search_by_postcode():
  adress_api_client = AdressApiClient()
  response = adress_api_client.search_by_postcode("postcode=75001")
  assert response == { "region": "Île-de-France", "department": "Paris 1er" }
