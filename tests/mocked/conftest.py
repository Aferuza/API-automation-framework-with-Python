import pytest
from src.api.api_client import APIClient


@pytest.fixture
def mock_client():
    return APIClient(base_url="https://api.github.com", token="fake-token")