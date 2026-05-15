import responses
import pytest
from src.api.endpoints import USER, USER_REPOS

BASE = "https://api.github.com"


class TestAuthMocked:

    @responses.activate
    def test_get_user_returns_200(self, mock_client):
        responses.add(
            method=responses.GET,
            url=f"{BASE}/user",
            json={"login": "Aferuza", "id": 45316760, "type": "User"},
            status=200,
            headers={"X-RateLimit-Remaining": "4999"}
        )
        response = mock_client.get("/user")
        assert response["status_code"] == 200
        assert response["json"]["login"] == "Aferuza"

    @responses.activate
    def test_invalid_token_returns_401(self, mock_client):
        """
        This is the test you asked about earlier.
        Mock lets you test auth failure WITHOUT a real bad token.
        """
        responses.add(
            method=responses.GET,
            url=f"{BASE}/user",
            json={"message": "Bad credentials"},
            status=401
        )
        response = mock_client.get("/user")
        assert response["status_code"] == 401
        assert response["json"]["message"] == "Bad credentials"

    @responses.activate
    def test_rate_limit_returns_403(self, mock_client):
        """
        You can NEVER reliably test this against the real API.
        Mocking is the ONLY correct approach here.
        """
        responses.add(
            method=responses.GET,
            url=f"{BASE}/user",
            json={"message": "API rate limit exceeded"},
            status=403,
            headers={"X-RateLimit-Remaining": "0"}
        )
        response = mock_client.get("/user")
        assert response["status_code"] == 403

    @responses.activate
    def test_github_server_error_returns_500(self, mock_client):
        """
        What does your APIClient do when GitHub is down?
        You can only test this with a mock.
        """
        responses.add(
            method=responses.GET,
            url=f"{BASE}/user",
            json={"message": "Internal Server Error"},
            status=500
        )
        response = mock_client.get("/user")
        assert response["status_code"] == 500