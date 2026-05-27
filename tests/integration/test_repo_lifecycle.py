import pytest
from src.validation.schemas.schema_validator import assert_valid_schema
from src.api.endpoints import USER_REPOS, REPO
from src.utils.config import GITHUB_USERNAME, GITHUB_REPO, PERFORMANCE_THRESHOLD


@pytest.mark.usefixtures("managed_repo")
class TestRepoLifecycle:

    def test_create_repo(self, client, repo_schema):
        """
        POST /user/repos — creates a new public repository.
        201 Created confirms the repo was created and the token has repo scope.
        Schema validation catches any structural changes to the creation response.
        """
        response = client.post(USER_REPOS, body={
            "name": GITHUB_REPO,
            "description": "Created by API automation framework",
            "private": False,   # Public repo — no private repo quota consumed
            "auto_init": True   # Initializes with a README so the repo is non-empty
        })

        assert response["status_code"] == 201, (
            f"Expected 201 Created, got {response['status_code']}"
        )

        # Contract check — if GitHub changes the repo creation response structure,
        # this fails immediately with a clear field-level error message
        assert_valid_schema(response["json"], repo_schema, "POST /user/repos")

        body = response["json"]
        assert body["name"] == GITHUB_REPO, "Repo name mismatch"
        assert body["private"] is False,    "Repo should be public"

    def test_get_repo(self, client, repo_schema):
        """
        GET /repos/{owner}/{repo} — fetches repo metadata after creation.
        200 confirms the repo exists and the token has read access.
        Owner assertion guards against the API returning a different repo.
        """
        # REPO is a template string: "/repos/{owner}/{repo}"
        # .format() injects the real values from .env at test time
        endpoint = REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO)
        response = client.get(endpoint)

        assert response["status_code"] == 200, (
            f"Expected 200, got {response['status_code']}"
        )

        # Schema contract — catches if GitHub renames or removes a field
        assert_valid_schema(response["json"], repo_schema, "GET /repos")

        body = response["json"]
        assert body["name"] == GITHUB_REPO, "Repo name mismatch"
        assert body["owner"]["login"] == GITHUB_USERNAME, (
            "Owner mismatch — wrong repo returned or token scoped to wrong account"
        )

    def test_update_repo(self, client, repo_schema):
        """
        PATCH /repos/{owner}/{repo} — updates the repo description.
        200 confirms the update was accepted.
        Payload assertion confirms the change was actually persisted,
        not just acknowledged.
        """
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
            "Description was not updated — PATCH may have been ignored"
        )

    def test_repo_performance(self, client):
        """
        GET /repos/{owner}/{repo} — asserts response time is within threshold.
        Slow API responses are a test failure, not a silent degradation.
        PERFORMANCE_THRESHOLD is configured in .env (default: 1.5s).
        """
        endpoint = REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO)
        response = client.get(endpoint)

        assert response["response_time"] < PERFORMANCE_THRESHOLD, (
            f"Response too slow: {response['response_time']:.3f}s "
            f"(threshold: {PERFORMANCE_THRESHOLD}s)"
        )