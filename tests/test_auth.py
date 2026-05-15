from api.endpoints import USER
from tests.test_repo_lifecycle import assert_valid_schema
import utils.config
from src.utils.config import PERFORMANCE_THRESHOLD


class TestAuthenticatedUser:

#Validate the /user endpoint. Confirms token is valid, scopes are correct, and response matches schema.
    def test_get_authenticated_user_status(self, client):
        """GET /user returns 200 for a valid token."""
        response = client.get(USER)
        assert response["status_code"] == 200, (
            f"Expected 200, got {response['status_code']}"
        )

# Validate response matches the defined JSON schema contract.
    def test_get_authenticated_user_schema(self, client, user_schema):
        response = client.get(USER)
        assert_valid_schema(response["json"], user_schema, "/user")

#  response contains required identity fields.
    def test_get_authenticated_user_payload(self, client):
        response = client.get(USER)
        body = response["json"]
        assert "login" in body, "Missing 'login' field"
        assert "id" in body,    "Missing 'id' field"

# Validate GET /user responds within acceptable performance threshold.
    def test_get_authenticated_user_response_time(self, client):
        response = client.get(USER)
        assert response["response_time"] < PERFORMANCE_THRESHOLD, (
            f"Response too slow: {response['response_time']:.3f}s"
        )
