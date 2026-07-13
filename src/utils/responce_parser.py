import json
from src.api.endpoints import USER
from src.api.endpoints import REPO, USER_REPOS
from src.api.api_client import APIClient

#ke access with key defaults
# return dict with 6 keys
client = APIClient()

response_json = client.get(USER)
# print(response_json)


# print(extract_repo_summary(response_json))
body = response_json["json"]
for key, value in body.items():
    print(key,value)
    if "owner" in body:
        print("Owner exists")

# def extract_repo_key(resp_json:dict)->dict:
    # return resp_json["json"].get("login")


# print(extract_repo_key(response_json))

def extract_repo_summary(resp_json:dict)->dict:
    body = resp_json['json']
    return{
        "name": body.get("name"),
        "owner": body.get("owner"),
        "private": body.get("private"),
        "description":body.get("description")

    }
print(extract_repo_summary(response_json))

print(json.dumps(response_json, indent=4))

# Given a list of repo list->find and  return the matching one
def find_repo_by_name(repos:list, name:str)-> dict | None:
    for single_repo in repos:
        if repo == "test":
            return single_repo
        return None

list_of_repos= ["auto", "test", "automation"]
print(find_repo_by_name(list_of_repos, "test"))


# 3. Compare 2 dicts and produce an error message- check that every key/value in expected exists in actual
def assert_fields_match(actual: dict, expected: dict, context: str = "") -> None:
    for key, expected_value in expected.items():

        if key not in actual:
            raise AssertionError(
                f"{context}: Missing key '{key}'"
            )

        actual_value = actual[key]

        if actual_value != expected_value:
            raise AssertionError(
                f"{context}: Key '{key}' "
                f"expected={expected_value!r}, actual={actual_value!r}"
            )




