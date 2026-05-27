import time                          # Used to measure response duration in request()
import requests                      # HTTP client — drives all API calls via Session
from src.utils.config import API_BASE_URL, AUTH_TOKEN, TIMEOUT  # Environment-loaded config
from src.utils.logger import logger  # Shared logger instance — writes to console and file


class APIClient:

    def __init__(self, token: str = AUTH_TOKEN):

        self.base_url = API_BASE_URL  # e.g. https://api.github.com — no trailing slash
        self.timeout = TIMEOUT        # Max seconds to wait for a response before Timeout
        self.logger = logger          # Shared logger — same instance across all modules

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",       # GitHub PAT auth
            "Accept": "application/vnd.github+json"   # Tells GitHub to return v3 JSON
        })

    def _safe_json(self, response: requests.Response) -> dict:
        """
        Parses the response body as JSON, returning an empty dict if there is no body.

        Why this exists:
            DELETE /repos/{owner}/{repo} returns 204 No Content — an empty body.
            Calling response.json() on an empty body raises JSONDecodeError.
            This method handles that case gracefully so tests can always do:
                assert response["json"] == {}
            instead of crashing on 204 responses.
        """
        try:
            return response.json()
        except Exception:
            return {}

    def request(self, method: str, endpoint: str, body=None) -> dict:
        url = f"{self.base_url}{endpoint}"  # Build full URL: base + path
        start = time.time()                 # Start timer before the request is sent

        try:
            response = self.session.request(
                method, url, json=body, timeout=self.timeout
                # json=body: serializes body dict to JSON and sets Content-Type automatically
                # timeout: raises Timeout if the server doesn't respond in time
            )
            elapsed = time.time() - start  # Capture round-trip duration

            # Log outcome — error level for 4xx/5xx, info for success
            # This appears in your terminal with -s and in log files in CI
            if response.status_code >= 400:
                self.logger.error(
                    f"HTTP ERROR {method} {endpoint} -> {response.status_code}"
                )
            else:
                self.logger.info(
                    f"{method} {endpoint} -> {response.status_code} ({elapsed:.3f}s)"
                )

            return {
                "status_code": response.status_code,
                "json": self._safe_json(response),  # Response body — NOT the request body
                "headers": dict(response.headers),  # Cast to plain dict for easy assertions
                "response_time": elapsed            # Used in performance threshold tests
            }

        except requests.exceptions.Timeout:
            # Server took longer than self.timeout seconds — log and re-raise
            # Re-raising lets pytest mark the test as ERROR (not FAILED) with a clear message
            self.logger.error(f"TIMEOUT {method} {endpoint}")
            raise

        except requests.exceptions.ConnectionError:
            # Network unreachable, DNS failure, refused connection
            # Raised when the request never reaches the server at all
            self.logger.error(f"CONNECTION ERROR {method} {endpoint}")
            raise

    # ── Convenience Methods ───────────────────────────────────────────────────
    # Thin wrappers around request() — give tests a clean, readable interface.
    # Tests call client.get("/user") instead of client.request("GET", "/user").

    def get(self, endpoint: str) -> dict:
        """Sends a GET request. Used to read/fetch resources."""
        return self.request("GET", endpoint)

    def post(self, endpoint: str, body: dict = None) -> dict:
        """Sends a POST request. Used to create new resources."""
        return self.request("POST", endpoint, body)

    def patch(self, endpoint: str, body: dict = None) -> dict:
        """Sends a PATCH request. Used to partially update existing resources."""
        return self.request("PATCH", endpoint, body)

    def delete(self, endpoint: str) -> dict:
        """Sends a DELETE request. Used to remove resources."""
        return self.request("DELETE", endpoint)