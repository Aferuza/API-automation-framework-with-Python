import pytest

from src.api.endpoints import USER
from tests.integration.test_repo_lifecycle import assert_valid_schema
import src.utils.config
from src.utils.config import PERFORMANCE_THRESHOLD


class TestAuthenticatedUser:
    """
    Validates GET /user — confirms token is valid, identity fields are present,
    response matches the schema contract, and performance is within threshold.
    """

    @pytest.fixture(autouse=True)
    def user_response(self, client):
        """Fetch GET /user once. All tests in this class assert against this response."""
        self._response = client.get(USER)

    def test_status_is_200(self):
        assert self._response["status_code"] == 200, (
            f"Expected 200, got {self._response['status_code']}"
        )

    def test_schema_contract(self, user_schema):
        assert_valid_schema(self._response["json"], user_schema, "GET /user")

    def test_payload_contains_identity_fields(self):
        body = self._response["json"]
        assert "login" in body, "Missing 'login' field"
        assert "id" in body,    "Missing 'id' field"

    def test_response_time_within_threshold(self):
        assert self._response["response_time"] < PERFORMANCE_THRESHOLD, (
            f"Response too slow: {self._response['response_time']:.3f}s"
        )