import base64
import json


def convert_string_to_json(env_details):
    decoded_json = base64.b64decode(env_details)
    return json.loads((decoded_json))


def create_response(data=None, errors=None, status="failed", message="Resolve successful", pagination=None):
    if pagination is None:
        pagination = {
            "count": None,
            "next": None,
            "previous": None,
        }

    response_data = {
        "data": data,
        "errors": errors,
        "status": status,
        "message": message,
        "pagination": pagination,
    }

    return response_data
