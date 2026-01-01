import json
from http.client import responses
from src.api.api_client import APIClient
from src.auth.endpoints import AUTH_USER
from src.validation.schemas.schema_validator import validate_schema


def load_schema():
    with open('src/validatiom/schemas/user_schema.json')as f:
        return json.load(f)


def test_authenticated_user_api():
    client=APIClient()
    schema = load_schema()

    response= client.get(AUTH_USER)
    assert response["status_code"]==200
    assert response['responce_time']<1.0
    assert validate_schema(response["json"],schema)

