import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Doc of the Address API: https://adresse.data.gouv.fr/outils/api-doc/adresse
class AddressApiClient:
    BASE_URL = 'https://api-adresse.data.gouv.fr/search/?q='

    def proxies(self):
        if os.getenv("PROXY_URL"):
            return {
                'http': os.getenv("PROXY_URL"),
                'https': os.getenv("PROXY_URL"),
            }
        else:
            return None

    def search_department_by_postcode(self, postcode):
        url = f"{self.BASE_URL}postcode={postcode}"
        response = requests.get(url, proxies=self.proxies())
        json_data = json.loads(str(response.text))
        if 'features' in json_data and len(json_data['features']) != 0 :
            departement = json_data['features'][0]['properties']['context']
            departement = departement.split(", ")
            departement = departement[1] + " ""(" + departement[0] + ")"
        else:
            departement = None
        return departement
    
    def search_region_by_postcode(self, postcode):
        url = f"{self.BASE_URL}postcode={postcode}"
        response = requests.get(url, proxies=self.proxies())
        json_data = json.loads(str(response.text))
        if 'features' in json_data and len(json_data['features']) != 0 :
            region = json_data['features'][0]['properties']['context']
            region = region.split(", ")
            if len(region) == 3:
                region = region[2]
            else:
                region = region[1]
        else:
            region = None
        return region    