import pytest
import utils.string_validator
from src.utils.string_validator import build_repo_endpoint, build_collaborators_url

from run_tests import result
from utils.string_validator import validate_collaborators_url


class TestStringValidator:

    def test_build_repo_endpoint(self):
        result = build_repo_endpoint("Aferuza", "my-test-repo")
        assert result == "/repos/Aferuza/my-test-repo"

    def strip_leading__and_trailing_whitespaces(self):
        result = build_repo_endpoint("Aferuza", "my-test-repo")
        assert result == "/repos/Aferuza/my-test-repo"

    def strip_whitespace_owner(self):
        result == build_repo_endpoint("Aferuza", "my-test-repo")
        assert result == "repos/Aferuza/my-test-repo"

    def strip_whitespace_repo(self):
        result = build_repo_endpoint("Aferuza", "my-test-repo")
        assert result == "repos/Aferuza/my-test-repo"

    def test_returns_string_type(self):
        result = build_repo_endpoint("Aferuza", "my-test-repo")
        assert isinstance(result, str)

    def test_no_double_slashes(self):
        result = build_repo_endpoint("Aferuza", "my-test-repo")
        assert "//" not in result

    def strats_with_repo(self):
        result = build_repo_endpoint("Aferuza", "my-test-repo")
        assert result.startswith("/repos/")

    @pytest.mark.parametrize("owner, repo, expected", [
        ("Aferuza", "my-test-repo", "/repos/Aferuza/my-test-repo"),
        ("aferuzat", "Hello-World", "/repos/aferuza/Hello-World"),
        (" octocat ", " Hello-World ", "/repos/octocat/Hello-World"),
        ("user123", "repo_with_underscores", "/repos/user123/repo_with_underscores"),
    ])
    def test_various_owner_repo_combinations(self, owner, repo, expected):
        assert build_repo_endpoint(owner, repo) == expected

     def test_validate_collaborators_url(self, owner, repo):
         result=validate_collaborators_url("Magicat", "My-tet-repo")
         assert result == "/repos/Magicat/My-tet-repo"

    def test_build_collaborators_url(self):
        result = build_collaborators_url("Magicat", "My-tet-repo", "octocat")
        assert result == "/repos/magicat/my-tet-repo/collaborators/octocat"

    @pytest.mark.parametrize("owner, repo, username, expected", [
        ("Magicat", "My-tet-repo", "octocat", "/repos/magicat/my-tet-repo/collaborators/octocat"),
        (" Aferuza ", " My_test_repo ", " OctoCat ", "/repos/aferuza/my_test_repo/collaborators/octocat"),
    ])
    def test_build_collaborators_url(self, owner, repo, username, expected):
        result = build_collaborators_url(owner, repo, username)
        assert result == expected



