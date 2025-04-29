import requests

# Swagger of the DataPass API: https://github.com/etalab/data_pass/blob/develop/config/openapi/v1.yaml
class AdressApiClient:
    BASE_URL = 'https://api-adresse.data.gouv.fr/'

    def search(self, q):
        url = f"{self.BASE_URL}/search"
        params = {
            'q': q
        }
        response = requests.get(url, params=params)
        return response
  
    def search_by_postcode(self, postcode):
        url = f"{self.BASE_URL}/search"
        params = {
            'q': f"postcode={postcode}"
        }
        response = requests.get(url, params=params)
        # TODO dig la réponse !
        return response