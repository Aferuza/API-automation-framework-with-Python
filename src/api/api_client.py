import time
import requests
from src.utils.config import API_BASE_URL, AUTH_TOKEN, TIMEOUT
from src.utils.logger import logger

class RequestLogEntry:
    """One recorded API call — built directly from data already computed in request(), no parsing."""

    def __init__(self, method, endpoint, status_code, elapsed):
        self.method = method.upper()
        self.endpoint = endpoint
        self.status_code = status_code
        self.elapsed = elapsed
        self.level = self._derive_level(status_code)

    @staticmethod
    def _derive_level(status_code):
        if status_code < 300:
            return "INFO"
        elif status_code < 400:
            return "WARNING"
        else:
            return "ERROR"   # 4xx and 5xx both — CRITICAL is not for HTTP status

    def is_error(self):
        return self.status_code >= 400

    def __repr__(self):
        return f"[{self.level}] {self.method} {self.endpoint} -> {self.status_code} ({self.elapsed:.3f}s)"


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

    def request(self, method: str, endpoint: str, body=None, quiet_statuses: tuple = ()) -> dict:
        url = f"{self.base_url}{endpoint}"
        start = time.perf_counter()

        try:
            response = self.session.request(
                method, url, json=body, timeout=self.timeout
            )
            elapsed = time.perf_counter() - start

            log_line = self._format_log_line(
                method, endpoint, response.status_code, elapsed
            )

            if response.status_code >= 400 and response.status_code not in quiet_statuses:
                self.logger.error(log_line)
            else:
                self.logger.info(log_line)

            return {
                "status_code": response.status_code,
                "json": self._safe_json(response),
                "headers": dict(response.headers),
                "response_time": elapsed
            }

        except requests.exceptions.Timeout:
            self.logger.error(
                f"[{'TIMEOUT'.ljust(6)}] {endpoint} -> TIMEOUT"
            )
            raise

        except requests.exceptions.ConnectionError:
            self.logger.error(
                f"[{'CONN ERR'.ljust(6)}] {endpoint} -> CONNECTION ERROR"
            )
            raise

    # ── Convenience Methods ───────────────────────────────────────────────────


    def get(self, endpoint: str) -> dict:
        """Sends a GET request. Used to read/fetch resources."""
        return self.request("GET", endpoint)

    def post(self, endpoint: str, body: dict = None) -> dict:
        """Sends a POST request. Used to create new resources."""
        return self.request("POST", endpoint, body)

    def patch(self, endpoint: str, body: dict = None) -> dict:
        """Sends a PATCH request. Used to partially update existing resources."""
        return self.request("PATCH", endpoint, body)

    def delete(self, endpoint: str, quiet_statuses: tuple = ()) -> dict:
        """Sends a DELETE request. Used to remove resources."""
        return self.request("DELETE", endpoint, quiet_statuses=quiet_statuses)