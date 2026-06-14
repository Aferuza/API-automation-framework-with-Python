import re


# REPO_COLLABORATORS = "/repos/{owner}/{repo}/collaborators/{username}"  # PUT / DELETE
# normalized lower() and strip()


def validate_collaborators_url(owner: str, repo:str, username: str)->str:
    return f"/repos/{owner.strip().lower()}/{repo.strip().lower()}/collaborators/{username.strip().lower()}"

print(validate_collaborators_url("Aferuza","My_test_repo", "octocat" ))

# if GH returns not the same repo that we expect but with whitespaces or lower/uppercase
def validate_repo_name(response_repo_name:str, expected_repo_name:str)->bool:
    return response_repo_name.strip().lower() == expected_repo_name.strip().lower()
print(validate_repo_name("test-repo", "my-test-repo"))

def is_valid_repo_name(repo_name:str)-> bool:
    if not repo_name or len(repo_name) < 1:
        return False
    if repo_name in (".",".."):
        return False
    if repo_name.startswith(".") or repo_name.endswith("."):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", repo_name))

print(is_valid_repo_name("test----repo"))  # True  — valid, repeated hyphens allowed
print(is_valid_repo_name("my repo"))  # False — contains a space
print(is_valid_repo_name(".gitignore"))  # False — starts with "."
print(is_valid_repo_name("repo."))  # False — ends with "."
print(is_valid_repo_name("."))  # False — exactly "."
print(is_valid_repo_name(""))  # False — empty
print(is_valid_repo_name("my-test-repo"))  # True


def extract_repo_owner_from_full_name(repo_name:str)->str:
    parts = repo_name.split("/")
    if len(parts)!=2:
        raise ValueError(f"Unexpected full_name format: '{repo_name}'. Expected 'owner/repo'.")
    return parts[0]
print(extract_repo_owner_from_full_name("Aferuza/My_test_repo"))


