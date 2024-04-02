import base64
import json


def convert_string_to_json(env_details):
    decoded_json = base64.b64decode(env_details)
    print(json.loads((decoded_json)))
    return json.loads((decoded_json))
