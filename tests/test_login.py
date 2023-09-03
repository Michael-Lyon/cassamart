from pprint import pprint

import requests

url = "http://localhost:8000/api/accounts/login/"

data = {
    "username": "first-buyer",
    "password": "1234rewqasdf"
}


response = requests.post(url=url, json=data)
pprint(response.json(), indent=4)
