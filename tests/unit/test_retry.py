# tests/unit/test_retry.py
import pytest
import requests
import responses
from src.api.api_client import APIClient


@responses.activate
def test_retries_on_503_then_succeeds():
    """
    Confirms the Retry policy actually retries on a 503 and eventually
    succeeds, instead of failing on the first attempt.
    """
    url = "https://api.github.com/user"

    # Simulate: server fails twice, then recovers on the third attempt
    responses.add(responses.GET, url, status=503)
    responses.add(responses.GET, url, status=503)
    responses.add(responses.GET, url, status=200, json={"login": "testuser"})

    client = APIClient(token="fake-token", base_url="https://api.github.com")
    result = client.get("/user")

    assert result["status_code"] == 200
    assert result["json"]["login"] == "testuser"
    # The real proof: 3 calls happened, not 1 — meaning it actually retried twice
    assert len(responses.calls) == 3


@responses.activate
def test_retries_on_429_rate_limit():
    """
    Confirms rate-limit responses (429) are also retried, not just server errors.
    """
    url = "https://api.github.com/user"

    responses.add(responses.GET, url, status=429)
    responses.add(responses.GET, url, status=200, json={"login": "testuser"})

    client = APIClient(token="fake-token", base_url="https://api.github.com")
    result = client.get("/user")

    assert result["status_code"] == 200
    assert len(responses.calls) == 2


@responses.activate
def test_does_not_retry_on_404():
    """
    Confirms retries do NOT fire on client errors that retrying can't fix —
    a 404 means the resource doesn't exist; trying again won't change that.
    """
    url = "https://api.github.com/user"
    responses.add(responses.GET, url, status=404)

    client = APIClient(token="fake-token", base_url="https://api.github.com")
    result = client.get("/user")

    assert result["status_code"] == 404
    # Only 1 call — proves no wasted retries on a non-retryable error
    assert len(responses.calls) == 1

@responses.activate
def test_gives_up_after_max_retries():
    """
    Confirms the client raises RetryError once retries are exhausted,
    rather than returning a normal response.
    """
    url = "https://api.github.com/user"
    for _ in range(4):
        responses.add(responses.GET, url, status=503)

    client = APIClient(token="fake-token", base_url="https://api.github.com")

    with pytest.raises(requests.exceptions.RetryError):
        client.get("/user")

    assert len(responses.calls) == 4