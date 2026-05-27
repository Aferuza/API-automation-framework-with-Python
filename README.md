
Why I Built This?
I've been in QA automation for three years. I've seen "automation frameworks" that are really just a single test file hitting a mock server, wrapped in a pytest class and do not support separation of concerns creating Spaghetti-code.
This isn't that.
I wanted to build something I could be asked about in a technical interview and defend every
single decision — why the APIClient is a separate layer, why config validates at import time,
why schema validation is different from payload assertions, why the auth header is fetched per
request instead of once at client initialization.
This framework hits the real GitHub API. It runs a real CRUD lifecycle — creates an actual
repository, reads it, updates it, deletes it — and validates status codes, response payloads,
JSON schema contracts, and performance thresholds at every step.
If you're a hiring manager reading this: every line of code here is something I can explain
on a whiteboard. That's the standard I held myself to.



<div align="left">

```text
RUNNER
│
├── run_tests.py
│
├── pytest
│ ├── collect
│ ├── execute
│ └── report
│
├── TEST LAYER
│ ├── schema contract
│ ├── payload fields
│ ├── response time
│ └── CRUD lifecycle
│
├── FIXTURE LAYER
│ └── conftest.py
│
├── CLIENT LAYER
│ ├── api_client.py
│ ├── auth headers
│ ├── JSON parsing
│ └── logging
│
└── CONFIG / AUTH / VALIDATION
    ├── .env
    ├── auth_client.py
    ├── config.py
    └── schema_validator.py
```

</div>


What This Framework Actually Does?
```
┌─────────────────────────────────────────────────────────┐
│                     TEST RUNNER                         │
│                    run_tests.py                         │
│         pytest → collect → execute → report             │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │        TEST LAYER           │
          │   tests/test_users_api.py   │
          │                             │
          │  TestAuthenticatedUser      │
          │  ├── status code (200)      │
          │  ├── schema contract        │
          │  ├── payload fields         │
          │  └── response time < 1.5s  │
          │                             │
          │  TestRepoLifecycle          │
          │  ├── CREATE → 201           │
          │  ├── READ   → 200           │
          │  ├── UPDATE → 200           │
          │  ├── DELETE → 204           │
          │  └── PERF   → < threshold  │
          └──────────────┬──────────────┘
                         │ uses
          ┌──────────────▼──────────────┐
          │      FIXTURE LAYER          │
          │       conftest.py           │
          │  module-scoped APIClient    │
          │  user_schema injected       │
          │  repo_schema injected       │
          └──────────────┬──────────────┘
                         │ injects
          ┌──────────────▼──────────────┐
          │       CLIENT LAYER          │
          │      api_client.py          │
          │  builds URL                 │
          │  fetches auth headers       │
          │  records response time      │
          │  logs every request         │
          │  safe JSON parsing          │
          │  returns standard dict      │
          └──────────────┬──────────────┘
                         │ reads from
     ┌────────────────────┼────────────────────┐
     │                    │                    │
┌────▼──────┐    ┌────────▼───────┐   ┌───────▼──────┐
│ CONFIG    │    │  AUTH CLIENT   │   │  VALIDATION  │
│ config.py │    │ auth_client.py │   │ schema_      │
│           │    │                │   │ validator.py │
│ .env      │    │ Bearer token   │   │              │
│ os.environ│    │ per-request    │   │ user_schema  │
│ validates │    │ header build   │   │ .json        │
│ at import │    └────────────────┘   └──────────────┘
└───────────┘
```
The Test Lifecycle — What Happens When You Run This?
Here's the exact sequence of events when you run python run_tests.py:
Step 1 — Config loads
  └── python-dotenv reads .env
  └── config.py validates ALL required vars at import time
  └── If AUTH_TOKEN is missing → RuntimeError immediately
      (not a cryptic 401 three tests in)

Step 2 — Fixtures initialize
  └── conftest.py creates module-scoped APIClient
  └── APIClient connects to https://api.github.com
  └── auth_client.py builds Bearer token header
  └── Schemas loaded: user_schema.json, repo_schema

Step 3 — TestAuthenticatedUser runs
  └── GET /user
      ├── status_code == 200 ✓
      ├── response body matches user_schema.json ✓
      ├── body contains "login" and "id" fields ✓
      └── response_time < PERFORMANCE_THRESHOLD ✓

Step 4 — TestRepoLifecycle runs
  └── POST /user/repos        → 201 Created
      └── GET  /repos/{owner}/{repo}  → 200 OK
          └── PATCH /repos/{owner}/{repo} → 200 OK
              └── DELETE /repos/{owner}/{repo} → 204 No Content
                  └── GET /repos/{owner}/{repo} → perf check

Step 5 — Report generated
  └── HTML report written to reports/report.html
  └── All pass/fail outcomes, durations, and errors captured

Project Structure
```
API-automation-framework-with-Python/
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions pipeline
│
├── src/
│   ├── api/
│   │   ├── api_client.py           # Central HTTP adapter (GET/POST/PATCH/DELETE)
│   │   └── endpoints.py            # All GitHub API path constants
│   ├── auth/
│   │   └── auth_client.py          # Builds Bearer token header per request
│   ├── utils/
│   │   ├── config.py               # Loads .env, validates at import time
│   │   └── logger.py               # Shared structured logger
│   ├── validation/
│   │   └── schemas/
│   │       ├── schema_validator.py # jsonschema wrapper with clear error messages
│   │       └── repo_schema.json    # JSON Schema contract for GET /user
│   └── reporting/
│       └── report_generator.py     # HTML report builder
│
├── tests/
    ├── integration/
    │   └── test_repo_lifecycle.py     # End-to-end integration tests tracking actual                                            state lifecycles
    │
    ├── mocked/
    │   └── test_users_api_mocked.py   # Isolated API tests using mocked          responses/substitutes
    │
    ├── unit/
    │   └── test_auth_client.py        # Micro-level tests for validating individual client functions
    │
    ├── conftest.py                    # Global Pytest fixtures (e.g., shared clients,                                            schemas)
    │
├── reporting/                        # Generated HTML test reports land here
├── results/                        # Raw JSON results
├── get_jwt_token.py                # GitHub Apps JWT generator (enterprise auth)
├── run_tests.py                    # Entry point — runs pytest + report
├── pytest.ini                      # Markers, log config, report path
├── pyproject.toml                  # Package metadata
├── requirements.txt                # All dependencies pinned
└── .env                            # Local secrets — never committed
```

The APIClient — The Heart of the Framework
Every single HTTP call in this framework goes through api_client.py. No test ever imports
requests directly. Here's why that matters and what happens on every request:

```python
# What a test looks like — clean, zero boilerplate
def test_get_authenticated_user_status(self, client):
    response = client.get(USER)
    assert response["status_code"] == 200

# What APIClient does behind the scenes on that one line:
# 1. Builds full URL:  https://api.github.com + /user
# 2. Calls auth_client.get_auth_headers() — fresh on every call
#    → {"Authorization": "Bearer ghp_xxx", "Accept": "application/json"}
# 3. Records start time
# 4. Sends request with configured timeout (default: 10s)
# 5. Records end time
# 6. Logs: "GET /user | Status: 200 | Duration: 0.312s"
# 7. Safely parses JSON — returns {} on empty body (e.g. 204 DELETE)
# 8. Returns standardized dict:
```

```json
{
    "status_code": 200,
    "json": { "login": "Aferuza", "id": 45316760, ... },
    "headers": { "X-RateLimit-Remaining": "4998", ... },
    "response_time": 0.312
}
```

The auth header is fetched per request, not at client initialization. This is intentional —
it means token rotation works in long-running CI pipelines without restarting the session.

Schema Validation vs Payload Assertions — Why Both Matter
This is a distinction that matters in production and in interviews. They catch completely
different categories of bugs.

| Assertion Type | Catches | Misses |
|---|---|---|
| **Payload assertion** | Wrong user's data returned, value regression | GitHub renames "login" to "username" |
| **Schema validation** | Renamed fields, type changes (int → string), removed required fields | Correct structure but wrong value |

Example — GitHub silently changes "id" from integer to string:
- **Payload assertion**: PASSES (string "45316760" == string "45316760" in loose check)
- **Schema validation**: FAILS immediately
  ```
  jsonschema.ValidationError: 45316760 is not of type 'integer'
  Path: id
  ```

The schema contract enforced in this framework:

```json
{
  "type": "object",
  "required": ["login", "id", "type", "created_at"],
  "properties": {
    "login":      { "type": "string",  "minLength": 1 },
    "id":         { "type": "integer", "minimum": 1 },
    "type":       { "type": "string",  "enum": ["User", "Organization"] },
    "created_at": { "type": "string",  "format": "date-time" }
  }
}
```

Configuration — How Environment Portability Works
The same test suite runs in three different environments without changing a single line of code:

```
LOCAL DEVELOPMENT          CI (GitHub Actions)        STAGING (future)
─────────────────          ───────────────────        ────────────────
.env file                  GitHub Secrets             Environment-specific
    │                           │                     secrets injection
    │                           │                          │
    └──────────┬────────────────┘──────────────────────────┘
               │
               ▼
          os.environ.get("AUTH_TOKEN")
               │
               ▼
            config.py
     ┌──────────────────────┐
     │ Validates at import: │
     │ • API_BASE_URL ✓     │
     │ • AUTH_TOKEN ✓       │
     │ • GITHUB_USERNAME ✓  │
     │ • GITHUB_REPO ✓      │
     │ • TIMEOUT (def: 10)  │
     │ • PERF_THRESHOLD     │
     │   (def: 1.5s)        │
     └──────────────────────┘
     Missing variable?
     → RuntimeError("AUTH_TOKEN is required")
     → Test run stops in 0.1s with a clear message
     → Not a cryptic 401 failure 5 tests in
```

The PERFORMANCE_THRESHOLD being environment-variable driven is important: you can set a
stricter threshold locally (1.0s) and a more lenient one in CI (2.0s) to account for
GitHub Actions runner latency — without touching the test code.

CI/CD Pipeline — GitHub Actions
The pipeline runs in two tiers:

**Every push / pull request:**
```
┌─────────────────────────────────────┐
│  mocked-tests job                   │
│  ─────────────────                  │
│  No real API calls                  │
│  No secrets needed                  │
│  Runs in ~5 seconds                 │
│  pytest -m "not live"               │
└─────────────────────────────────────┘
```

**Nightly at 2am UTC (scheduled):**
```
┌─────────────────────────────────────┐
│  live-integration-tests job         │
│  ──────────────────────────────     │
│  Hits real GitHub API               │
│  Uses GitHub Secrets                │
│  Validates live API contract        │
│  pytest -m "live"                   │
│  Uploads HTML report as artifact    │
└─────────────────────────────────────┘
```

**Why split?**

Because live API tests have failure modes that have nothing to do with your code —
rate limiting, network flakiness, GitHub outages. Flaky tests destroy team trust in a test suite
faster than anything else. Mocked tests on every push stay fast and reliable. Live tests run
nightly to validate the real contract.

Setup:

**1. Clone and install**
```bash
git clone https://github.com/Aferuza/API-automation-framework-with-Python.git
cd API-automation-framework-with-Python
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
```

**2. Create your .env file**
```env
API_BASE_URL=https://api.github.com
AUTH_TOKEN=ghp_yourPersonalAccessTokenHere
GITHUB_USERNAME=your_github_username
GITHUB_REPO=your_test_repo_name
TIMEOUT=10
PERFORMANCE_THRESHOLD=1.5
```

Your token needs these scopes: `repo`, `delete_repo`, `read:user`

**3. Run the tests**
```bash
# Full suite + HTML report
python run_tests.py

# Pytest directly
pytest tests/ -v

# One class only
pytest tests/test_users_api.py::TestAuthenticatedUser -v
pytest tests/test_users_api.py::TestRepoLifecycle -v

# With HTML report
pytest tests/ -v --html=reports/report.html --self-contained-html

# By marker
pytest tests/ -m "smoke" -v
pytest tests/ -m "not live" -v
```

Test Coverage:

**TestAuthenticatedUser — Validates GET /user**

| Test | HTTP Call | Expected | What's Validated |
|---|---|---|---|
| `test_get_authenticated_user_status` | GET /user | 200 | Status code confirms token is valid and correctly scoped |
| `test_get_authenticated_user_schema` | GET /user | 200 | Body matches user_schema.json, catches contract changes |
| `test_get_authenticated_user_fields` | GET /user | 200 | Required fields (login, id, type) present in response |
| `test_get_authenticated_user_performance` | GET /user | 200 | Response time < PERFORMANCE_THRESHOLD |

**TestRepoLifecycle — Full CRUD on a real repository**

| Test | HTTP Call | Expected | What's Validated |
|---|---|---|---|
| `test_create_repo` | POST /user/repos | 201 | Repo name, visibility, schema contract |
| `test_get_repo` | GET /repos/{owner}/{repo} | 200 | Name, owner login, schema matches expected |
| `test_update_repo` | PATCH /repos/{owner}/{repo} | 200 | Updated description persisted, schema valid |
| `test_delete_repo` | DELETE /repos/{owner}/{repo} | 204 | No content returned, repo actually deleted |
| `test_repo_lifecycle_performance` | All above | < 2.0s | Full CRUD cycle completes within threshold |




About Me:

Six years in QA, based in the Bay Area. I care about backend quality, API contract testing,
and the intersection of DevOps and test automation. I built this framework because I wanted
a portfolio project I could actually be proud of — one that reflects how I think about
engineering, not just how I write tests.
If you have questions about any architectural decision in this repo, I'd genuinely enjoy
that conversation.

· [Feruza Askar GitHub](https://github.com/Aferuza) · [Feruza Askar LinkedIn](https://www.linkedin.com/in/feruza-askar/)
