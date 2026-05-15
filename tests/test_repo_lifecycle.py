import json
import pytest
from jsonschema import ValidationError

from src.validation.schemas.schema_validator import validate_schema, validate
from src.api.api_client import APIClient
from src.api.endpoints import USER, USER_REPOS, REPO
from src.utils.config import GITHUB_USERNAME, GITHUB_REPO, PERFORMANCE_THRESHOLD

'''Purpose:
1. Validates authentication + contract of the GitHub API (/user)
2. Executes a full CRUD workflow on GitHub repositories
3. Executed through a reusable API client, under pytest control'''

# Load JSON schemas once per test session — used for contract testing.
def load_user_schema():
#Read and parse the user schema from disk."""
    with open("src/validation/schemas/user_schema.json") as f:
        return json.load(f)

# Read and parse the repo schema from disk.
def load_repo_schema():
    with open("src/validation/schemas/repo_schema.json") as f:
        return json.load(f)



# Validates a response payload against a JSON schema.
#     Wraps jsonschema.validate() with a clear failure message.
def assert_valid_schema(data: dict, schema: dict, label: str):
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed for [{label}]: {e.message}")


#Tests


# Full CRUD lifecycle test against a real GitHub repo. Tests run: Create → Read → Update → Delete.
# Each step validates status code, payload, schema, and response time.
class TestRepoLifecycle:

#Validate POST /user/repos creates a new repository and returns 201."""
    def test_create_repo(self, client, repo_schema):
        response = client.post(USER_REPOS, body={
            "name": GITHUB_REPO,
            "description": "Created by API automation framework",
            "private": False,
            "auto_init": True
        })
        assert response["status_code"] == 201, (
            f"Expected 201, got {response['status_code']}"
        )
        # Validate the created repo matches the schema contract
        assert_valid_schema(response["json"], repo_schema, "POST /user/repos")

        body = response["json"]
        assert body["name"] == GITHUB_REPO, "Repo name mismatch"
        assert body["private"] is False,    "Repo should be public"

# Validate GET /repos/{owner}/{repo} returns repo metadata and matches schema."""
        # Step 1 — Build the endpoint URL: Fill {owner} and {repo} placeholders with real values from .env
    def test_get_repo(self, client, repo_schema):
        endpoint = REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO)

        # Step 2 — Send GET request to the repo endpoint: APIClient handles auth headers, timeout, logging, and response parsing
        response = client.get(endpoint)

        # Step 3 — Validate HTTP status code: 200 confirms the repo exists and the token has read access
        assert response["status_code"] == 200, (
            f"Expected 200, got {response['status_code']}"
        )

        # Step 4 — Validate response structure against JSON schema:Catches any breaking changes to the API contract
        # e.g. if GitHub renames or removes a field this will fail immediately
        assert_valid_schema(response["json"], repo_schema, "GET /repos")

        # Step 5 — Extract response body for payload assertions
        body = response["json"]

        # Step 6 — Confirm the correct repo was returned: Guards against the API returning a different repo than requested
        assert body["name"] == GITHUB_REPO, "Repo name mismatch"

        # Step 7 — Confirm the repo belongs to the correct owner: Validates authorization scope — wrong owner means a permissions issue
        assert body["owner"]["login"] == GITHUB_USERNAME, "Owner mismatch"

#Validate PATCH /repos/{owner}/{repo} updates description of the repo and returns 200."""
    def test_update_repo(self, client, repo_schema):
        endpoint = REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO)
        response = client.patch(endpoint, body={
            "description": "Updated by API automation framework"
        })

        assert response["status_code"] == 200, (
            f"Expected 200, got {response['status_code']}"
        )
        assert_valid_schema(response["json"], repo_schema, "PATCH /repos")

        body = response["json"]
        assert body["description"] == "Updated by API automation framework", (
            "Description was not updated"
        )

# Validate GET /repos/{owner}/{repo} responds within performance threshold.

    def test_repo_performance(self, client):
        endpoint = REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO)
        response = client.get(endpoint)
        assert response["response_time"] < PERFORMANCE_THRESHOLD, (
            f"Response too slow: {response['response_time']:.3f}s"
        )
# Validate DELETE /repos/{owner}/{repo} removes the repo and returns 204."""
    def test_delete_repo(self, client):
        endpoint = REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO)
        response = client.delete(endpoint)

        # 204 No Content — successful delete returns no body
        assert response["status_code"] == 204, (
            f"Expected 204, got {response['status_code']}"
        )
        assert response["json"] == {}, "DELETE response body should be empty"
