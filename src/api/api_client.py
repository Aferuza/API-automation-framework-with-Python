from src.utils.config import API_BASE_URL, AUTH_TOKEN, TIMEOUT
from src.utils.logger import logger
import time
import requests
from src.auth.auth_client import get_auth_headers
from src.utils.config import API_BASE_URL, TIMEOUT
from src.utils.logger import logger


class APIClient:
    """test modules interact with the API through this class. wraps all HTTP requests with auth, logging, timing, and error handling."""

    def __init__(self):
        self.base_url = API_BASE_URL

    def request(self, method: str, endpoint: str, json_body=None) -> dict:
        """ executes all HTTP requests.  Called internally by get(), post(), patch(), delete()."""

        # Combine base URL + endpoint path into the full request URL
        url = f"{self.base_url}{endpoint}"

        # Fetch auth headers fresh on every request and supports token rotation/refresh without restarting the client
        headers = get_auth_headers()

        # Record start time before the request is sent
        start = time.time()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_body,  # automatically sets Content-Type: application/json
                timeout=TIMEOUT  # prevents tests hanging on unresponsive endpoints
            )

            # Raise immediately on 4xx/5xx so tests fail fast with a clear error
            response.raise_for_status()

        except requests.exceptions.Timeout:
            # Server did not respond within TIMEOUT seconds
            logger.error(f"TIMEOUT {method} {endpoint}")
            raise

        except requests.exceptions.HTTPError as e:
            # Non-2xx response — log status code for quick diagnosis
            logger.error(f"HTTP ERROR {method} {endpoint} -> {e.response.status_code}")
            raise

        except requests.exceptions.RequestException as e:
            # Catch-all for network errors: DNS failure, connection refused, etc.
            logger.error(f"REQUEST FAILED {method} {endpoint} -> {e}")
            raise

        # Calculate total round-trip time after a successful response
        elapsed = time.time() - start

        # Log method, path, status code, and duration for every successful call
        logger.info(f"{method} {endpoint} -> {response.status_code} ({elapsed:.3f}s)")

        # Safely parse JSON — returns empty dict if body is empty or not valid JSON
        # Prevents crashes on endpoints that return no content e.g. 204 DELETE
        try:
            body = response.json()
        except ValueError:
            body = {}

        # Return structured dict so tests can assert on any part of the response
        return {
            "status_code": response.status_code,  # e.g. 200, 201, 204
            "json": body,                          # parsed response payload
            "headers": dict(response.headers),     # cast to dict for easy assertions
            "response_time": elapsed               # used for performance threshold checks
        }

    # ── Convenience Methods ────────────────────────────────────────────────────
    # Wrap request() to give tests a clean, readable interface

    def get(self, endpoint: str) -> dict:
        """Sends a GET request. Used to read and fetch resources."""
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