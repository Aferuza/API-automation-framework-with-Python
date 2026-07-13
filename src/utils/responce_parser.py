from src.utils.assertion_helpers import assert_fields_match


class ResponseParser:
    """
    Wraps the dict returned by APIClient.request() and provides a
    readable, chainable interface for interpreting API responses.

    Why this exists:
        APIClient's job is transport — send a request, hand back a plain
        dict of {status_code, json, headers, response_time}. That dict is
        deliberately dumb: it doesn't know what a "valid" response looks
        like for any given endpoint.

        ResponseParser is the layer that DOES know how to read that dict
        safely — nested field access without KeyError blowups, status
        code checks with clear messages, and field validation that reuses
        assert_fields_match instead of re-implementing it.

    This class does no I/O. It only ever operates on the dict it's given,
    which means it's fully unit-testable with plain dict fixtures — no
    `responses.activate`, no mocking, no network.
    """

    def __init__(self, response: dict):
        self._status_code = response.get("status_code")
        self._json = response.get("json", {}) or {}
        self._headers = response.get("headers", {}) or {}
        self._response_time = response.get("response_time")

    # ── Raw access ──────────────────────────────────────────────────────
    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def json(self) -> dict:
        return self._json

    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def response_time(self) -> float:
        return self._response_time

    # ── Safe nested field access ───────────────────────────────────────
    def get(self, path: str, default=None):
        """
        Dot-notation access into the response JSON.

        Example:
            parser.get("owner.login")
            parser.get("license.spdx_id", default="NONE")

        Returns `default` instead of raising if any key in the path
        is missing or if an intermediate value isn't a dict — this is
        the whole point: no KeyError mid-test.
        """
        value = self._json
        for key in path.split("."):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def get_header(self, name: str, default=None):
        """
        Case-insensitive header lookup.

        HTTP header names are case-insensitive by spec, but APIClient
        stores headers as a plain dict cast from requests' own
        CaseInsensitiveDict — so the original casing is preserved and a
        naive `self._headers[name]` lookup can miss. This normalizes it.
        """
        for key, value in self._headers.items():
            if key.lower() == name.lower():
                return value
        return default

    def rate_limit_remaining(self) -> int | None:
        """Convenience wrapper — GitHub's rate limit header, cast to int."""
        value = self.get_header("X-RateLimit-Remaining")
        return int(value) if value is not None else None

    # ── Assertions (chainable) ─────────────────────────────────────────
    def expect_status(self, expected_status: int) -> "ResponseParser":
        """
        Asserts the response status code matches, then returns self so
        calls can chain: parser.expect_status(201).validate_fields(...)
        """
        if self._status_code != expected_status:
            raise AssertionError(
                f"Expected status {expected_status}, got {self._status_code}. "
                f"Body: {self._json}"
            )
        return self

    def validate_fields(self, expected: dict, context: str = "") -> "ResponseParser":
        """
        Validates that every key/value in `expected` exists in the
        response JSON. Delegates to assert_fields_match rather than
        reimplementing comparison logic — this method's only job is
        knowing WHERE the fields live (self._json), not HOW to compare
        them.
        """
        assert_fields_match(self._json, expected, context=context or "response body")
        return self

    # ── TEMPORARY: repo-specific domain logic ──────────────────────────
    # TODO: everything below this line is repo domain logic, not generic
    # response parsing. It's here short-term because it was faster than
    # building a RepoService layer today. Move repo_summary() and
    # find_repo_by_name() into src/api/repo_service.py once that exists —
    # ResponseParser should only know how to read A response, not know
    # anything about what a "repo" specifically looks like.

    def repo_summary(self) -> dict:
        """
        Shapes this response's JSON into the subset of fields most repo
        tests care about. Repo-specific by design — this is why it does
        NOT belong in the generic part of this class long-term.
        """
        return {
            "name": self.get("name"),
            "owner": self.get("owner"),
            "private": self.get("private"),
            "description": self.get("description"),
        }


def find_repo_by_name(repos: list[dict], name: str) -> dict | None:
    """
    Searches a list of repo dicts (e.g. the JSON body of GET /user/repos,
    which returns a list, not a single object) for one matching `name`.

    Lives as a module-level function, not a ResponseParser method, because
    it operates on a *list* of repos, not a single response envelope.

    Bug fixed from the original draft: `return None` was previously inside
    the loop body, so the function exited after checking only the first
    element instead of exhausting the search. It also compared each repo
    to a hardcoded string instead of checking against the `name` argument.
    """
    for repo in repos:
        if repo.get("name") == name:
            return repo
    return None