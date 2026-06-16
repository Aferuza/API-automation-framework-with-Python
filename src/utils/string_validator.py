import re


def build_repo_endpoint(owner: str, repo: str) -> str:
    """
    REAL USE CASE: In endpoints.py I have:
        REPO = "/repos/{owner}/{repo}"
    Your APIClient needs to turn that template into a real path before
    sending the HTTP request.

        - str.strip()  -> remove accidental whitespace from env vars
        - f-strings    -> inject variables into the URL template

        If owner or repo has a trailing space (common when copying from a
        .env file), your request will hit "/repos/Aferuza /my-repo " -> 404.
        strip() is your safety net.
    """
    owner = owner.strip()
    repo = repo.strip()
    return f"/repos/{owner}/{repo}"


def build_collaborators_url(owner: str, repo: str, username: str) -> str:
    """
    REPO_COLLABORATORS = "/repos/{owner}/{repo}/collaborators/{username}"
    Normalized with strip() + lower() since GitHub usernames/repo names are
    case-insensitive for routing.
    """
    return (
        f"/repos/{owner.strip().lower()}/{repo.strip().lower()}"
        f"/collaborators/{username.strip().lower()}"
    )


def validate_repo_name(response_repo_name: str, expected_repo_name: str) -> bool:
    return response_repo_name.strip().lower() == expected_repo_name.strip().lower()


def is_valid_repo_name(repo_name: str) -> bool:

    if not repo_name or len(repo_name) < 1:
        return False
    if repo_name in (".", ".."):
        return False
    if repo_name.startswith(".") or repo_name.endswith("."):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", repo_name))


def extract_repo_owner_from_full_name(full_name: str) -> str:
    parts = full_name.split("/")
    if len(parts) != 2:
        raise ValueError(
            f"Unexpected full_name format: '{full_name}'. Expected 'owner/repo'."
        )
    return parts[0]