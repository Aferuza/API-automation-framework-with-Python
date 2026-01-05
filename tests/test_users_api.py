import json
import pytest
from src.api.api_client import APIClient
from src.auth.endpoints import AUTH_USER, USER_REPOS, REPO
from src.validation.schemas.schema_validator import validate_schema
from src.utils.config import API_BASE_URL

'''
Purpose:
1.Validates authentication + contract of the GitHub API (/user)
2. Executes a full CRUD workflow on GitHub repositorie
3. Executed through a reusable API client, under pytest control'''

# Load JSON schema once-contract testing
def load_user_schema():
    with open("src/validation/schemas/user_schema.json") as f:
        return json.load(f)

# This fixture creates the APIClient instance.
@pytest.fixture(scope="module")
def client():
    """Reusable API client for GitHub API tests."""
    return APIClient()


@pytest.fixture(scope="module")
def user_schema():
    """Load user JSON schema for validation."""
    return load_user_schema()


def test_authenticated_user_api(client, user_schema):
    """Validate authenticated user endpoint. Pytest injects:
- `client` → APIClient instance
- `user_schema` → JSON schema dict"""
    response = client.get(AUTH_USER)

    assert response["status_code"] == 200
    assert response["response_time"] < 1.0
    assert validate_schema(response["json"], user_schema)


def test_github_repo_crud(client):
    """Full CRUD workflow for a GitHub repo."""

    # 1️. Create a repo
    create_resp = client.post(USER_REPOS, {"name": "qa-demo-repo", "private": False})
    assert create_resp["status_code"] == 201
    owner = create_resp["json"]["owner"]["login"]

    # 2.Get repo metadata
    repo_info = client.get(REPO.format(owner=owner, repo="qa-demo-repo"))
    assert repo_info["status_code"] == 200
    assert repo_info["json"]["name"] == "qa-demo-repo"

    # 3. Update repo description
    update_resp = client.patch(REPO.format(owner=owner, repo="qa-demo-repo"),
                               {"description": "Updated via automation"})
    assert update_resp["status_code"] == 200
    assert update_resp["json"]["description"] == "Updated via automation"

    # 4️. Delete repo
    delete_resp = client.delete(REPO.format(owner=owner, repo="qa-demo-repo"))
    assert delete_resp["status_code"] == 204
