import time
import requests
from src.utils.config import API_BASE_URL, AUTH_TOKEN, TIMEOUT
from src.utils.logger import logger


class APIClient:

    def __init__(self, token: str = AUTH_TOKEN, base_url: str = API_BASE_URL):
        self.base_url = base_url  # Injected — defaults to config value
        self.timeout = TIMEOUT
        self.logger = logger

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        })

    def _safe_json(self, response: requests.Response) -> dict:
        """
        Parses the response body as JSON, returning an empty dict if
        there is no body.

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

    def _format_log_line(
        self, method: str, endpoint: str, status_code: int, elapsed: float
    ) -> str:
        """
        Produces a consistent, aligned log line for every request outcome.

        Same format for success and error paths so CI logs are greppable
        and tools like Datadog/Kibana can parse them with one pattern.

        Example:
            [GET   ] /user -> 200 (0.312s)
            [POST  ] /user/repos -> 422 (0.196s)
            [DELETE] /repos/Aferuza/my-test-repo -> 204 (0.360s)
        """
        method_padded = method.upper().ljust(6)
        return f"[{method_padded}] {endpoint} -> {status_code} ({elapsed:.3f}s)"

    def request(self, method: str, endpoint: str, body=None) -> dict:
        url = f"{self.base_url}{endpoint}"  # Build full URL: base + path

        # perf_counter: monotonic clock — correct for measuring elapsed duration.
        # time.time() measures wall-clock time and can jump backward or forward
        # due to NTP sync or DST, producing incorrect elapsed values.
        start = time.perf_counter()

        try:
            response = self.session.request(
                method, url, json=body, timeout=self.timeout
                # json=body: serializes body dict to JSON and sets
                #            Content-Type: application/json automatically
                # timeout:   raises Timeout if server doesn't respond in time
            )
            elapsed = time.perf_counter() - start

            log_line = self._format_log_line(
                method, endpoint, response.status_code, elapsed
            )

            # Error level for 4xx/5xx so CI log scanners can filter failures
            # without reading every INFO line
            if response.status_code >= 400:
                self.logger.error(log_line)
            else:
                self.logger.info(log_line)

            return {
                # int — HTTP status code, used in every test assertion
                "status_code": response.status_code,

                # dict — response body parsed from JSON.
                # NOT the request body. _safe_json returns {} for
                # empty bodies (e.g. 204 DELETE) instead of crashing.
                "json": self._safe_json(response),

                # dict — cast from CaseInsensitiveDict to plain dict.
                # Used for rate limit assertions and header contract checks.
                "headers": dict(response.headers),

                # float — round-trip duration in seconds.
                # Used in performance threshold tests:
                #   assert response["response_time"] < PERFORMANCE_THRESHOLD
                "response_time": elapsed
            }

        except requests.exceptions.Timeout:
            # Server took longer than self.timeout seconds.
            # Re-raising lets pytest mark the test as ERROR (not FAILED)
            # with a clear traceback rather than swallowing the exception.
            self.logger.error(
                f"[{'TIMEOUT'.ljust(6)}] {endpoint} -> TIMEOUT"
            )
            raise

        except requests.exceptions.ConnectionError:
            # Network unreachable, DNS failure, or refused connection.
            # Raised when the request never reaches the server at all.
            self.logger.error(
                f"[{'CONN ERR'.ljust(6)}] {endpoint} -> CONNECTION ERROR"
            )
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