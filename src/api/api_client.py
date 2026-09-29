from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
            return "ERROR"  # 4xx and 5xx both — CRITICAL is not for HTTP status

    def is_error(self):
        return self.status_code >= 400

    def as_log_fields(self) -> dict:
        """Structured fields for the JSON logger's extra= — individually queryable in Loki/jq."""
        return {
            "method": self.method,
            "endpoint": self.endpoint,
            "status_code": self.status_code,
            "elapsed": round(self.elapsed, 3),
        }

    def __repr__(self):
        return f"[{self.level}] {self.method} {self.endpoint} -> {self.status_code} ({self.elapsed:.3f}s)"


class APIClient:

    def __init__(self, token: str = AUTH_TOKEN, base_url: str = API_BASE_URL):
        self.base_url = base_url  # Injected — defaults to config value
        self.timeout = TIMEOUT
        self.logger = logger

        self.session = requests.Session()

        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

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

    def request(self, method: str, endpoint: str, body=None, quiet_statuses: tuple = ()) -> dict:
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

            entry = RequestLogEntry(method, endpoint, response.status_code, elapsed)
            log_fields = entry.as_log_fields()

            # quiet_statuses lets callers suppress expected "errors" from logging as
            # ERROR — e.g. a 404 on cleanup-delete that's expected and fine.
            if entry.is_error() and response.status_code not in quiet_statuses:
                self.logger.error(str(entry), extra=log_fields)
            else:
                self.logger.info(str(entry), extra=log_fields)

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

        except requests.exceptions.RetryError:
            # urllib3's Retry policy exhausted all attempts (default
            # raise_on_status=True) — surfaces as an exception rather than
            # a normal response, same treatment as Timeout/ConnectionError.
            self.logger.error(
                f"[{'MAX RETRY'.ljust(6)}] {endpoint} -> RETRIES EXHAUSTED"
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

    def delete(self, endpoint: str, quiet_statuses: tuple = ()) -> dict:
        """Sends a DELETE request. Used to remove resources."""
        return self.request("DELETE", endpoint, quiet_statuses=quiet_statuses)