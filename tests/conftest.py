import json
import pytest
from pathlib import Path
from src.utils.config import API_BASE_URL, AUTH_TOKEN
from src.api.api_client import APIClient
from src.api.endpoints import USER_REPOS, REPO
from src.utils.config import GITHUB_REPO, GITHUB_USERNAME

ROOT = Path(__file__).parent.parent


def load_user_schema() -> dict:
    with open(ROOT / "src" / "validation" / "schemas" / "user_schema.json") as f:
        return json.load(f)


def load_repo_schema() -> dict:
    with open(ROOT / "src" / "validation" / "schemas" / "repo_schema.json") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def client():
    # Only raise here — mocked tests never call this fixture
    if not API_BASE_URL or not AUTH_TOKEN:
        pytest.skip("Live credentials not configured — skipping live tests")
    return APIClient(base_url=API_BASE_URL, token=AUTH_TOKEN)


@pytest.fixture(scope="module")
def user_schema():
    return load_user_schema()


@pytest.fixture(scope="module")
def repo_schema():
    return load_repo_schema()


@pytest.fixture(scope="module")
# fixture depending on another fixture 
def managed_repo(client):
    repo_endpoint = REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO)

    # Defensive cleanup: if a prior run crashed mid-suite (CI timeout,
    # killed process, etc.), the yield-based teardown below never ran.
    # Delete first so create() below always starts from a clean slate.
    # A 404 here is expected and fine — nothing to clean up.
    client.delete(repo_endpoint)

    create_response = client.post(USER_REPOS, body={
        "name": GITHUB_REPO,
        "description": "Created by API automation framework",
        "private": False,
        "auto_init": True
    })
    assert create_response["status_code"] == 201, (
        f"Setup failed — could not create repo: {create_response['status_code']}"
    )

    yield create_response

    response = client.delete(repo_endpoint)
    assert response["status_code"] in (204, 404), (
        f"Unexpected status during teardown delete: {response['status_code']}"
    )