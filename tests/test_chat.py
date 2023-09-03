import time
from pprint import pprint

import requests
from dump import headers

url = "http://localhost:8000/api/chat/2/"
response = requests.get(url=url, headers=headers)
data = response.json()
pprint(data, indent=4)


print("Please wait for post request")
time.sleep(10)

raw = {
    'current_room': {
        'name': 'first-sellerfirst-buyer', 'slug': 'cdnywickwygr'
        },
    'message': "Hello World",
}

response = requests.post(url=url, headers=headers, json=raw)
data = response.json()
pprint(data, indent=4)
