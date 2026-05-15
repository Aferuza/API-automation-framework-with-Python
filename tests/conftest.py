import pytest

from api.api_client import APIClient
from tests.test_repo_lifecycle import load_user_schema, load_repo_schema


# PyTest Fixtures:
# Reusable API client for all GitHub API tests in this module.
@pytest.fixture(scope="module")
def client():

    return APIClient()

#     Used to validate response contract — detects breaking API changes.
@pytest.fixture(scope="module")
def user_schema():
    return load_user_schema()

#  Validates structure on create, read, and update responses.
@pytest.fixture(scope="module")
def repo_schema():
     return load_repo_schema()
