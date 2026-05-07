
This project is a Python-based API automation framework that could display how QA and DevOps teams build scalable,
 maintainable, and CI/CD-ready automated testing solutions for backend systems.
It validates GitHub REST APIs (uses live APIs rather than mocks) with focus on backend quality, API contracts, authentication, performance,
and DevOps practices.

## Key Objectives:
Based on reading your actual framework code, here are the key objectives of the project:

**1. Validate GitHub API Authentication**
Confirm that a Bearer token is valid, correctly scoped, and returns expected user identity fields (`login`, `id`) via `GET /user`.

**2. Enforce API Contract Testing**
Use JSON schema validation (`jsonschema`) to catch any breaking changes to the GitHub API response structure — if GitHub renames or removes a field, tests fail immediately with a clear message rather than silently passing with bad data.

**3. Automate the Full CRUD Repository Lifecycle**
Execute a real end-to-end workflow — Create → Read → Update → Delete — against an actual GitHub repository, verifying correct HTTP status codes (`201`, `200`, `204`) and payload accuracy at every step.

**4. Enforce Performance Thresholds**
Assert that API responses return within a configurable time limit (`PERFORMANCE_THRESHOLD`, defaulting to 1.5s), making slow API responses a test failure rather than a silent degradation.

**5. Provide a Reusable, Maintainable HTTP Layer**
Centralise all API interaction in a single `APIClient` class that handles auth headers, request timing, structured response parsing, logging, and error handling — so individual tests stay clean and focused on assertions only.

**6. Fail Fast on Misconfiguration**
Validate all required environment variables at import time (`API_BASE_URL`, `AUTH_TOKEN`, `GITHUB_USERNAME`, `GITHUB_REPO`) and raise a `RuntimeError` immediately, preventing cryptic mid-test failures from a missing `.env`.

**7. Generate Test Reports**
Produce HTML test reports automatically via `pytest-html` and a custom `report_generator`, giving visibility into pass/fail outcomes and execution history.

## Tech Stack:
* Language: Python 3
* Testing Framework: Pytest
* HTTP Client: Requests
* Schema Validation: jsonschema
* Configuration Management: python-dotenv
* Authentication: OAuth2 Bearer Token
* Reporting: HTML reports (pytest-html / Jinja2 ready)


Overview
This framework automates end-to-end testing of the GitHub API through a reusable APIClient class. Tests validate HTTP status codes, response payloads, JSON schema contracts, and response time performance thresholds. Authentication is handled via a Bearer token loaded from a .env file.

📁 Project Structure
API-automation-framework-with-Python-main/
│
├── src/
│   ├── api/
│   │   ├── api_client.py          # Central HTTP client (GET, POST, PATCH, DELETE)
│   │   └── endpoints.py           # GitHub API endpoint constants
│   ├── auth/
│   │   └── auth_client.py         # Builds Bearer token auth headers
│   ├── utils/
│   │   ├── config.py              # Loads and validates .env config
│   │   └── logger.py              # Shared logger instance
│   ├── validation/
│   │   └── schemas/
│   │       ├── schema_validator.py  # jsonschema wrapper utility
│   │       └── user_schema.json     # JSON schema for /user response contract
│   └── reporting/
│       └── report_generator.py    # HTML report generation
│
├── tests/
│   ├── conftest.py                # Pytest fixture reference (commented)
│   └── test_users_api.py         # Main test file — all test classes live here
│
├── run_tests.py                   # Entry point: runs pytest + generates report
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Package config (setuptools)
└── .env                           # Secret config (not committed)

🧩 Test Classes
Both test classes live in tests/test_users_api.py and share module-scoped fixtures: an APIClient instance, a user_schema, and a repo_schema.

TestAuthenticatedUser
Validates the GET /user endpoint to confirm the Bearer token is valid, the response contract is intact, and the API performs within the configured threshold.
Test MethodWhat It Validatestest_get_authenticated_user_statusResponse status is 200 OKtest_get_authenticated_user_schemaResponse body matches user_schema.json contracttest_get_authenticated_user_payloadResponse body contains required login and id fieldstest_get_authenticated_user_response_timeRound-trip time is below PERFORMANCE_THRESHOLD
Example:
pythonclass TestAuthenticatedUser:
    def test_get_authenticated_user_status(self, client):
        response = client.get(USER)
        assert response["status_code"] == 200

TestRepoLifecycle
Executes a full Create → Read → Update → Delete lifecycle against a real GitHub repository. Each step validates status code, response payload, and JSON schema contract.
Test MethodHTTP CallWhat It Validatestest_create_repoPOST /user/repos201 status, correct repo name and visibility in body, schema matchtest_get_repoGET /repos/{owner}/{repo}200 status, correct repo name, correct owner login, schema matchtest_update_repoPATCH /repos/{owner}/{repo}200 status, updated description reflected in response, schema matchtest_delete_repoDELETE /repos/{owner}/{repo}204 status, empty response bodytest_repo_performanceGET /repos/{owner}/{repo}Response time is below PERFORMANCE_THRESHOLD
Example:
pythonclass TestRepoLifecycle:
    def test_create_repo(self, client, repo_schema):
        response = client.post(USER_REPOS, body={
            "name": GITHUB_REPO,
            "description": "Created by API automation framework",
            "private": False,
            "auto_init": True
        })
        assert response["status_code"] == 201
        assert response["json"]["name"] == GITHUB_REPO

⚙️ Core Modules
APIClient — src/api/api_client.py
The central HTTP wrapper used by all test methods. Every request is automatically enriched with:

Auth headers — fetched fresh on every call via get_auth_headers() to support token rotation
Timing — records round-trip elapsed time for performance assertions
Logging — logs method, path, status code, and duration for every request
Error handling — raises on timeouts, HTTP 4xx/5xx errors, and network failures with descriptive log output
Safe JSON parsing — returns {} on empty bodies (e.g. 204 DELETE) to prevent crashes

Every call returns a structured dict:
python{
    "status_code": 201,
    "json": { ... },           # parsed response body
    "headers": { ... },        # response headers as a plain dict
    "response_time": 0.312     # seconds — used in performance threshold tests
}
endpoints.py — src/api/endpoints.py

Defines all GitHub API path constants. Template strings use .format() to inject owner, repo, and username at test time:
pythonUSER               = "/user"
USER_REPOS         = "/user/repos"
REPO               = "/repos/{owner}/{repo}"
REPO_BRANCHES      = "/repos/{owner}/{repo}/branches"
REPO_ISSUES        = "/repos/{owner}/{repo}/issues"
REPO_COLLABORATORS = "/repos/{owner}/{repo}/collaborators/{username}"
REPO_TOPICS        = "/repos/{owner}/{repo}/topics"
auth_client.py — src/auth/auth_client.py
Returns the auth header dict injected into every API request:
python{
    "Authorization": "Bearer <AUTH_TOKEN>",
    "Accept": "application/json"
}
config.py — src/utils/config.py
Loads all configuration from .env using python-dotenv. Raises a RuntimeError at import time if any required variable is missing — this means a misconfigured environment fails immediately with a clear message rather than a cryptic 401 mid-test.
VariableDescriptionDefaultAPI_BASE_URLGitHub API base URLrequiredAUTH_TOKENGitHub Personal Access TokenrequiredGITHUB_USERNAMEGitHub username (fills {owner})requiredGITHUB_REPOTarget repo name (fills {repo})requiredTIMEOUTRequest timeout in seconds10PERFORMANCE_THRESHOLDMax acceptable response time (seconds)1.5
schema_validator.py — src/validation/schemas/schema_validator.py
Wraps jsonschema.validate() and logs any schema validation errors. Tests also use assert_valid_schema() defined in the test file itself, which wraps the same library with a clear pytest.fail() message on contract violations.


Setup:
bash# 1. Clone the repository
git clone https://github.com/your-org/API-automation-framework-with-Python.git
cd API-automation-framework-with-Python

# 2. Create and activate a virtual environment
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt


Configuration:
Create a .env file in the project root:
envAPI_BASE_URL=https://api.github.com
AUTH_TOKEN=ghp_yourPersonalAccessTokenHere
GITHUB_USERNAME=your_github_username
GITHUB_REPO=your_test_repo_name
TIMEOUT=10
PERFORMANCE_THRESHOLD=1.5
Required GitHub Personal Access Token scopes:

repo — full repository access (create, read, update, delete)
delete_repo — required for the test_delete_repo test
read:user — required for the TestAuthenticatedUser tests


Running the Tests:
Run all tests via the entry point (also generates an HTML report):
bashpython run_tests.py
Run directly with pytest:
bashpytest tests/ -v
Run a specific test class:
bashpytest tests/test_users_api.py::TestAuthenticatedUser -v
pytest tests/test_users_api.py::TestRepoLifecycle -v
Run with an HTML report:
bashpytest tests/ -v --html=reports/report.html --self-contained-html

Test Lifecycle Flow:
[Setup]
  └── .env loaded → config validated → APIClient initialized
         │
         ▼
[TestAuthenticatedUser]
  └── GET /user
      ├── Status:      200 OK
      ├── Schema:      matches user_schema.json
      ├── Payload:     contains login + id fields
      └── Performance: < PERFORMANCE_THRESHOLD seconds
         │
         ▼
[TestRepoLifecycle]
  ├── CREATE   POST   /user/repos               → 201 Created
  ├── READ     GET    /repos/{owner}/{repo}      → 200 OK
  ├── UPDATE   PATCH  /repos/{owner}/{repo}      → 200 OK
  ├── DELETE   DELETE /repos/{owner}/{repo}      → 204 No Content
  └── PERF     GET    /repos/{owner}/{repo}      → < threshold
         │
         ▼
[Report]
  └── HTML report written to reports/report.html

Dependencies:
PackageVersionPurposerequestslatestHTTP client for all API callspytestlatestTest runner and fixture managementpytest-htmllatestHTML test report generationjsonschema(via pytest deps)JSON schema contract validationpython-dotenvlatest.env configuration loadinghttpxlatestAsync-capable HTTP client (available for extension)pydanticlatestData validation (available for extension)
Install all dependencies with:
bashpip install -r requirements.txt