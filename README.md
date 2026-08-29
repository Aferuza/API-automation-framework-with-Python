![CI](https://github.com/Aferuza/API-automation-framework-with-Python/actions/workflows/ci.yml/badge.svg)

# API Automation Framework — Python + pytest + GitHub Actions
<img width="1490" height="858" alt="Screenshot 2026-08-28 at 8 07 51 PM" src="https://github.com/user-attachments/assets/f2e4afe2-cb47-4fe1-b44a-2c5518d74b8e" />
*Full suite passing — 32 tests across unit, mocked, and live integration layers, run against the real GitHub API.*

## Why I Built This

I've been in QA automation for six years. I've seen "automation frameworks" that are really just a single test file hitting a mock server, wrapped in a pytest class, with no separation of concerns — spaghetti code dressed up as architecture.

This isn't that.

I wanted to build something I could be asked about in a technical interview and defend every single decision:

- Why the `APIClient` is a separate injectable layer, not a hardcoded singleton
- Why config validates at import time in integration mode but fails gracefully in mocked mode
- Why schema validation is fundamentally different from payload assertions
- Why the auth header is fetched per request instead of once at client initialization
- Why mocked tests and integration tests run in separate CI jobs with different trigger conditions
- Why `base_url` is injected into `APIClient` rather than hardcoded from config

This framework hits the real GitHub API. It runs a real CRUD lifecycle — creates an actual repository, reads it, updates it, deletes it — and validates status codes, response payloads, JSON schema contracts, and performance thresholds at every step.

It also runs a full mocked test suite in CI on every push and pull request, with zero real API calls and zero credentials required.

> **If you're a hiring manager reading this:** every line of code here is something I can explain on a whiteboard. That's the standard I held myself to.

---

## What This Framework Actually Does

```
┌─────────────────────────────────────────────────────────┐
│                     TEST RUNNER                         │
│                    run_tests.py                         │
│         pytest → collect → execute → report             │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │        TEST LAYER           │
          │                             │
          │  tests/mocked/              │
          │  ├── test_users_api_mocked  │
          │  └── responses intercepted  │
          │      by requests-mock       │
          │                             │
          │  tests/unit/                │
          │  └── test_auth_client.py    │
          │                             │
          │  tests/integration/         │
          │  ├── TestAuthenticatedUser  │
          │  │   ├── status code (200)  │
          │  │   ├── schema contract    │
          │  │   ├── payload fields     │
          │  │   └── response time      │
          │  └── TestRepoLifecycle      │
          │      ├── CREATE → 201       │
          │      ├── READ   → 200       │
          │      ├── UPDATE → 200       │
          │      ├── DELETE → 204       │
          │      └── PERF   < 1.5s     │
          └──────────────┬──────────────┘
                         │ uses
          ┌──────────────▼──────────────┐
          │      FIXTURE LAYER          │
          │       conftest.py           │
          │  module-scoped APIClient    │
          │  skips live tests if no     │
          │  credentials configured     │
          │  user_schema injected       │
          │  repo_schema injected       │
          └──────────────┬──────────────┘
                         │ injects
          ┌──────────────▼──────────────┐
          │       CLIENT LAYER          │
          │      api_client.py          │
          │  base_url injected          │
          │  builds full URL            │
          │  fetches auth headers       │
          │  records response time      │
          │  logs every request         │
          │  safe JSON parsing          │
          │  returns standard dict      │
          └──────────────┬──────────────┘
                         │ reads from
     ┌────────────────────┼────────────────────┐
     │                    │                    │
┌────▼──────┐    ┌────────▼───────┐   ┌───────▼──────────┐
│ CONFIG    │    │  AUTH CLIENT   │   │   VALIDATION     │
│ config.py │    │ auth_client.py │   │ schema_          │
│           │    │                │   │ validator.py     │
│ lazy load │    │ Bearer token   │   │                  │
│ for mocked│    │ per-request    │   │ user_schema.json │
│ fail-fast │    │ header build   │   │ repo_schema.json │
│ for live  │    └────────────────┘   └──────────────────┘
└───────────┘
```

---

## Project Structure

```
API-automation-framework-with-Python/
│
├── .github/
│   └── workflows/
│       └── ci.yml                     # Three-job CI pipeline: lint → mocked → integration
│
├── src/
│   ├── api/
│   │   ├── api_client.py              # Injectable HTTP adapter (GET/POST/PATCH/DELETE)
│   │   └── endpoints.py               # All GitHub API path constants
│   ├── auth/
│   │   └── auth_client.py             # Builds Bearer token header per request
│   ├── utils/
│   │   ├── config.py                  # Lazy env loading — validates only when needed
│   │   └── logger.py                  # Shared structured logger
│   ├── validation/
│   │   └── schemas/
│   │       ├── schema_validator.py    # jsonschema wrapper with structured error output
│   │       ├── user_schema.json       # JSON Schema contract for GET /user
│   │       └── repo_schema.json       # JSON Schema contract for GET /repos/{owner}/{repo}
│   └── reporting/
│       └── report_generator.py        # HTML report builder
│
├── tests/
│   ├── mocked/
│   │   ├── conftest.py                # mock_client fixture — no real credentials needed
│   │   └── test_users_api_mocked.py  # 200, 401, 403, 500 scenarios via requests-mock
│   ├── unit/
│   │   └── test_auth_client.py        # Unit tests for auth header construction
│   ├── integration/
│   │   └── test_repo_lifecycle.py     # Full CRUD lifecycle against real GitHub API
│   │   └── test_repo_negative.py      # Error paths: invalid auth, duplicates, 404s, missing fields

**`TestNegative` — Error handling and edge cases**

| Test                              | HTTP Call                      | Expected | What's Validated                          |
| ---------------------------------- | ------------------------------- | -------- | ------------------------------------------ |
| `test_get_user_with_invalid_token` | `GET /user`                     | 401      | Invalid credentials rejected cleanly       |
| `test_create_duplicate_repo`       | `POST /user/repos`              | 422      | Duplicate repo name correctly rejected     |
| `test_get_nonexistent_repo`        | `GET /repos/{owner}/{repo}`     | 404      | Missing resource returns proper error      |
| `test_create_repo_without_name`    | `POST /user/repos`              | 422      | Missing required field caught by API       |
│   └── conftest.py                    # Global fixtures — skips live tests if no creds
│
├── reports/                           # Generated HTML test reports
├── results/                           # Raw JSON results
├── get_jwt_token.py                   # GitHub Apps JWT generator (enterprise auth)
├── run_tests.py                       # Entry point — runs pytest + generates report
├── pytest.ini                         # Markers, log config, report defaults
├── pyproject.toml                     # Package metadata
├── requirements.txt                   # All dependencies
└── .env                               # Local secrets — never committed
```

---

## The APIClient — Injectable, Not Hardcoded

Every HTTP call in this framework goes through `api_client.py`. No test ever imports `requests` directly.

The key design decision: `base_url` is an injected parameter with a sensible default, not hardcoded inside the class. This is dependency injection — the same class can point at the real GitHub API in integration tests, or be constructed with a fake token in mocked tests, with no source code changes.

```python
# Production use — picks up base_url from config by default
client = APIClient()

# Mocked test use — full control, no credentials required
client = APIClient(base_url="https://api.github.com", token="fake-token")
```

What happens on every request:

```python
# What a test looks like — clean, zero boilerplate
def test_get_authenticated_user_status(self, client):
    response = client.get(USER)
    assert response["status_code"] == 200

# What APIClient does behind the scenes:
# 1. Builds full URL:  https://api.github.com + /user
# 2. Calls auth_client.get_auth_headers() — fresh on every call
#    → {"Authorization": "Bearer ghp_xxx", "Accept": "application/vnd.github+json"}
# 3. Records start time
# 4. Sends request with configured timeout (default: 10s)
# 5. Records end time
# 6. Logs: "GET /user | Status: 200 | Duration: 0.312s"
# 7. Safely parses JSON — returns {} on empty body (e.g. 204 DELETE)
# 8. Returns standardised dict:
{
    "status_code": 200,
    "json": { "login": "Aferuza", "id": 45316760, ... },
    "headers": { "X-RateLimit-Remaining": "4998", ... },
    "response_time": 0.312
}
```

> The auth header is fetched **per request**, not at client initialization. This is intentional — token rotation works in long-running CI pipelines without restarting the session.

---

## Configuration — Lazy Loading for Testability

Earlier versions of `config.py` called `_require()` at module import time. This caused every test — including mocked tests that never touch the real API — to crash immediately if credentials weren't present.

The fix: config values are loaded lazily. Validation happens only inside the `client` fixture, which mocked tests never call:

```python
# conftest.py — validation happens here, not at import time
@pytest.fixture(scope="module")
def client():
    if not API_BASE_URL or not AUTH_TOKEN:
        pytest.skip("Live credentials not configured — skipping live tests")
    return APIClient(token=AUTH_TOKEN)
```

This means:

- Mocked tests import the module fine, never request the `client` fixture, and never trigger the credential check
- Integration tests request `client`, which validates and skips cleanly if credentials are absent
- The same test suite runs in all three environments without changing a line of code

```
LOCAL DEVELOPMENT          CI (GitHub Actions)        STAGING (future)
─────────────────          ───────────────────        ────────────────
.env file                  GitHub Secrets             Env-specific secrets
     │                          │                           │
     └──────────────────────────┴───────────────────────────┘
                                │
                          os.environ.get()
                                │
                           config.py
                    ┌──────────────────────┐
                    │ API_BASE_URL          │
                    │ AUTH_TOKEN            │
                    │ GITHUB_USERNAME       │
                    │ GITHUB_REPO           │
                    │ TIMEOUT (def: 10s)    │
                    │ PERF_THRESHOLD (1.5s) │
                    └──────────────────────┘
```

> `PERFORMANCE_THRESHOLD` being environment-variable driven matters: a stricter threshold locally (1.0s) and a more lenient one in CI (2.0s) accounts for GitHub Actions runner latency — without touching test code.

---

## Schema Validation vs Payload Assertions — Why Both Matter

These catch completely different categories of bugs.

| Assertion Type | Catches | Misses |
|---|---|---|
| Payload assertion | Wrong value returned, data regression | GitHub renames `login` to `username` |
| Schema validation | Renamed fields, type changes (`int` → `string`), removed required fields | Correct structure but wrong value |

**Example — GitHub silently changes `id` from integer to string:**

```
Payload assertion:   PASSES  (value is present, loose equality holds)

Schema validation:   FAILS immediately
  jsonschema.ValidationError: '45316760' is not of type 'integer'
  Path: id
```

The `user_schema.json` in this framework was built from a **live `GET /user` response**, not a generic template. Every nullable field (`email`, `hireable`, `twitter_username`) and every templated URL field (which cannot use `format: uri` because they contain `{/other_user}` tokens) was validated against a real response before being committed.

```json
{
  "type": "object",
  "required": ["login", "id", "type", "site_admin", "created_at", "updated_at"],
  "properties": {
    "login":      { "type": "string",          "minLength": 1 },
    "id":         { "type": "integer",         "minimum": 1 },
    "email":      { "type": ["string", "null"] },
    "type":       { "type": "string",          "enum": ["User", "Organization", "Bot"] },
    "created_at": { "type": "string",          "format": "date-time" }
  },
  "additionalProperties": true
}
```

> `additionalProperties: true` is intentional — GitHub adds new fields over time. This schema protects against **removals and type changes**, not additions.

## Catching a Real Contract Break

[#catching-a-real-contract-break](#catching-a-real-contract-break)

Schema validation only matters if it actually catches something. So I broke it on purpose.

I changed the `user_schema.json` contract to expect `id` as a `string` instead of an `integer` — simulating what happens when an API's data type silently changes. The live GitHub API still returned `id` as an integer (`45316760`), exactly as before.

A simple payload assertion like `assert response["json"]["id"] is not None` would have **passed** — the field is present, so the test is happy. It's blind to the type change.

Schema validation caught it immediately:

<img width="649" height="664" alt="Screenshot 2026-08-28 at 8 15 12 PM" src="https://github.com/user-attachments/assets/4559eb91-895c-4387-9d3a-05d263a87f5d" />

*Schema said `id` should be a string. GitHub returned an integer. The framework failed loudly instead of shipping the mismatch downstream.*

This is the failure mode schema validation exists to catch — and payload assertions can't.


---

## CI/CD Pipeline — GitHub Actions

Three jobs run in sequence: `lint → mocked-tests → integration-tests`.

```yaml
lint:
  # flake8 on src/ and tests/
  # blocks everything downstream if it fails

mocked-tests:
  needs: lint
  # every push and pull request
  # no secrets, no real API calls
  # tests/mocked/ + tests/unit/
  # completes in ~5 seconds

integration-tests:
  needs: lint
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  # merge to main only
  # uses GitHub Secrets for live credentials
  # tests/integration/
  # uploads HTML report as downloadable artifact
```

**Why split mocked and integration into separate jobs:**

Live API tests have failure modes that have nothing to do with your code — rate limiting, network flakiness, GitHub outages. Flaky tests that fail for infrastructure reasons destroy team trust in a test suite faster than anything else. Mocked tests on every push stay fast and reliable. Integration tests run only on merge to main, protecting the main branch without blocking PR feedback.

**Two implementation details worth noting:**

- `PYTHONPATH: .` is set as an environment variable instead of `pip install -e .` — this makes `from src.api.api_client import APIClient` resolve correctly without requiring `pyproject.toml` to be fully configured for editable installs
- `mkdir -p reports` runs before pytest in both jobs — on a fresh CI runner the directory doesn't exist, and `pytest-html` will error trying to write the report file without it

---

## The Test Lifecycle

```
Step 1 — Config loads (lazy)
  └── python-dotenv reads .env locally, or GitHub Actions injects secrets
  └── Values available as os.environ — no validation yet

Step 2 — Fixtures initialise
  └── client fixture checks API_BASE_URL and AUTH_TOKEN
  └── Missing? → pytest.skip() — clean yellow skip, not a red error
  └── Present? → APIClient(token=AUTH_TOKEN) constructed
  └── Schemas loaded from src/validation/schemas/

Step 3 — Mocked tests (every push/PR)
  └── mock_client constructed with fake token and real base_url
  └── requests-mock intercepts all HTTP at the session layer
  └── No network calls made
  └── Tests validate APIClient behaviour, not GitHub's API

Step 4 — Integration tests (main branch only)
  └── GET /user           → 200, schema, payload, performance
  └── POST /user/repos    → 201 Created
  └── GET /repos/{o}/{r}  → 200 OK
  └── PATCH /repos/{o}/{r}→ 200 OK
  └── DELETE /repos/{o}/{r}→ 204 No Content

Step 5 — Reports
  └── HTML report written to reports/
  └── Uploaded as GitHub Actions artifact
  └── Available for download from the Actions run summary
```

---

## Test Coverage

### Mocked Tests — `tests/mocked/`

| Test | Mock | What's Validated |
|---|---|---|
| `test_get_user_returns_200` | 200 + user payload | APIClient parses status and JSON correctly |
| `test_invalid_token_returns_401` | 401 + error body | Client handles auth failure without crashing |
| `test_rate_limit_returns_403` | 403 + rate limit body | Client handles forbidden response correctly |
| `test_github_server_error_returns_500` | 500 + error body | Client handles server errors gracefully |

### Integration Tests — `tests/integration/`

**`TestAuthenticatedUser` — `GET /user`**

| Test | Expected | What's Validated |
|---|---|---|
| `test_get_authenticated_user_status` | 200 | Token is valid and correctly scoped |
| `test_get_authenticated_user_schema` | 200 | Body matches `user_schema.json` contract |
| `test_get_authenticated_user_fields` | 200 | `login` and `id` present in response |
| `test_get_authenticated_user_performance` | < 1.5s | Response time within threshold |

**`TestRepoLifecycle` — Full CRUD on a real repository**

| Test | HTTP Call | Expected | What's Validated |
|---|---|---|---|
| `test_create_repo` | `POST /user/repos` | 201 | Repo name, visibility, schema contract |
| `test_get_repo` | `GET /repos/{owner}/{repo}` | 200 | Name, owner login, schema valid |
| `test_update_repo` | `PATCH /repos/{owner}/{repo}` | 200 | Updated description persisted |
| `test_delete_repo` | `DELETE /repos/{owner}/{repo}` | 204 | Empty body, repo removed |
| `test_repo_performance` | `GET /repos/{owner}/{repo}` | < 1.5s | Response within threshold |

---

## Setup

**1. Clone and install**

```bash
git clone https://github.com/Aferuza/API-automation-framework-with-Python.git
cd API-automation-framework-with-Python
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
```

**2. Create your `.env` file**

```env
API_BASE_URL=https://api.github.com
AUTH_TOKEN=ghp_yourPersonalAccessTokenHere
GITHUB_USERNAME=your_github_username
GITHUB_REPO=your_test_repo_name
TIMEOUT=10
PERFORMANCE_THRESHOLD=1.5
```

> Your token needs these scopes: `repo`, `delete_repo`, `read:user`

**3. Run the tests**

```bash
# Full suite + HTML report
python run_tests.py

# Mocked tests only — no credentials needed
pytest tests/mocked/ tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# With HTML report
pytest tests/ -v --html=reports/report.html --self-contained-html
```

---

## About Me

[#about-me](#about-me)

Six years in QA, based in the Bay Area. I care about backend quality, API contract testing, and the intersection of DevOps and test automation. I built this framework because I wanted a portfolio project I could actually be proud of — one that reflects how I think about engineering, not just how I write tests.

I build this kind of test coverage for early-stage SaaS and AI startups who have a working product but no dedicated QA yet. If that's you, feel free to reach out.

And if f you have questions about any architectural decision in this repo, I would genuinely enjoy that conversation.
