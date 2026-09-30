from src.validation.schemas.schema_validator import assert_valid_schema

# Negatives tests:
from src.utils.config import GITHUB_REPO
from src.api.api_client import APIClient


class TestNegative():

    def test_get_user_with_invalid_token(self):
        bad_client = APIClient(token="ghp_thisisafaketoken")
        response = bad_client.get("/user")
        assert response["status_code"] == 401

    def test_create_duplicate_repo(self, client, managed_repo):
        # managed_repo fixture creates GITHUB_REPO before this runs,
        # guaranteeing the POST below hits an already-existing repo name
        response = client.post("/user/repos", body={"name": GITHUB_REPO})
        assert response["status_code"] == 422


    def test_get_nonexistent_repo(self, client):
        response = client.get("/repos/Aferuza/this-repo-does-not-exist-xyz")
        assert response["status_code"] == 404

    # 4. Missing required field in request body
    def test_create_repo_without_name(self, client):
        response = client.post("/user/repos", body={"description": "no name"})
        assert response["status_code"] == 422