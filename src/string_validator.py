import re
import time
import requests



# 1.REPO_COLLABORATORS = "/repos/{owner}/{repo}/collaborators/{username}"  # PUT / DELETE
# normalized lower() and strip()


def validate_collaborators_url(owner: str, repo:str, username: str)->str:
    return f"/repos/{owner.strip().lower()}/{repo.strip().lower()}/collaborators/{username.strip().lower()}"

print(validate_collaborators_url("Aferuza","My_test_repo", "octocat" ))

#2. if GH returns not the same repo that we expect but with whitespaces or lower/uppercase
def validate_repo_name(response_repo_name:str, expected_repo_name:str)->bool:
    return response_repo_name.strip().lower() == expected_repo_name.strip().lower()
print(validate_repo_name("test-repo", "my-test-repo"))

#3. Validate GH repo name
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

# 4.Validate repo owner
def extract_repo_owner_from_full_name(repo_name:str)->str:
    parts = repo_name.split("/")
    if len(parts)!=2:
        raise ValueError(f"Unexpected full_name format: '{repo_name}'. Expected 'owner/repo'.")
    return parts[0]
print(extract_repo_owner_from_full_name("Aferuza/My_test_repo"))

# 5. Format logs
def format_request_log(method:str, path:str, status_code:int, elapsed:float)->str:
    method = method.upper().ljust(6)
    return f"[{method}]{path}->{status_code}({elapsed:.3f}s)"

def send_request(method, url, **kwargs):
    start = time.perf_counter()
    response = requests.request(method, url, **kwargs)
    elapsed = time.perf_counter() - start

    log_line = format_request_log(method, response.request.path_url, response.status_code, elapsed)
    print(log_line)

    return response

#6. format assertion error- when schema or payload assertion fails
def format_assertion_error(field:str, expected, actual)->str:
    return f"Field {field!r}:expected{expected!r}, got {actual!r}"

# 7.To mask the access token
def mask_token(token:str, visible_chars:int=4)->str:
    if len(token) > visible_chars*2:
        return "*"* len(token)
    # define middle - is the len of the token minus the 4 chars in the begining and end
    # the remaining length, i.e. how many characters are in the "hidden" middle section
    masked_middle_part = "*"* len(token) -visible_chars*2
    # take the 4 in the begining, the masked part and the 4 from the end of the token.
    # if token is 18 chars = 18-(4*2)= 18-8= masked 10
    return token[:visible_chars] +  masked_middle_part + token[-visible_chars:]

#8. Check if Auth token Bearer is appended correctly, not double
def build_auth_token(token:str)->str:
    token= token.strip()
    if token.lower().startswith("Bearer "):
        token = token[7:]
        return f"Bearer {token}"

#9. For dynamic contetent assertion- in test_update_repo- i can check if after the update a keyword is contains
def assert_descrption_update(response_descr:str, expected_keyword:str)->bool:
    assert response_descr["json"]["description"] == ("Updated")
    return expected_keyword.lower() in response_descr["json"]["description"].lower()

# Normalize GH visibility before aseerting
def normalize_visib(visibility:str)->str:
    normalized_visib = visibility.strip().lower()
    allowed_visibility = ["public", "private", "rinternal"]
    if normalized_visib not in allowed_visibility:
        raise ValueError(f"Invalid visibility value: '{normalized_visib}'. Expected one of {allowed_visibility}")
    return normalized_visib
