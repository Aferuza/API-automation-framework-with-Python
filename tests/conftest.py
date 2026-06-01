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
def managed_repo(client):
    client.post(USER_REPOS, body={
        "name": GITHUB_REPO,
        "private": False,
        "auto_init": True
    })
    yield
    response = client.delete(REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO))
    assert response["status_code"] in (204, 404), (
        f"Unexpected status during teardown delete: {response['status_code']}"
    )