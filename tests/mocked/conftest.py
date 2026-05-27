#function scoped mock fixture
import pytest

from src.api.api_client import APIClient


@pytest.fixture()
def mock_client():
    return APIClient()