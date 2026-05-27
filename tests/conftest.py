import pytest

from src.api.endpoints import USER_REPOS, REPO
from src.api.api_client import APIClient
from tests.integration.test_repo_lifecycle import load_user_schema, load_repo_schema
from src.utils.config import GITHUB_REPO, GITHUB_USERNAME


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


@pytest.fixture(scope="module")
def managed_repo(client):
    """Creates the repo before tests, deletes it after — guaranteed."""
    client.post(USER_REPOS, body={
        "name": GITHUB_REPO,
        "private": False,
        "auto_init": True
    })
    yield  # tests run here
    client.delete(REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO))