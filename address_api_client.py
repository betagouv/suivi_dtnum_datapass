import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Doc of the Address API: https://adresse.data.gouv.fr/outils/api-doc/adresse
class AddressApiClient:
    BASE_URL = 'https://api-adresse.data.gouv.fr/search/?q='

    def search_region_and_department_by_postcode(self, postcode):
        proxies = {
            'http': os.getenv("PROXY_URL"),
            'https': os.getenv("PROXY_URL"),
        }
        url = f"{self.BASE_URL}postcode={postcode}"
        response = requests.get(url, proxies=proxies)
        json_data =  response.json()

        if 'features' in json_data and len(json_data['features']) != 0 :
            departement = json_data['features'][0]['properties']['context']
            departement = departement.split(", ")
            departement = f"{departement[1]} ({departement[0]})"

            region = json_data['features'][0]['properties']['context']
            region = region.split(", ")
            if len(region) == 3:
                region = region[2]
            else:
                region = region[1]
        else:
            departement = None
            region = None
            
        return { "departement": departement, "region": region }
    