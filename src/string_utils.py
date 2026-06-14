'''As a QA engineer I deal with str when:
  - Building API endpoint URLs
  - Parsing and asserting response body fields
  - Normalizing data before comparison
  - Formatting log and error messages
  - Validating field formats (email, repo name, etc.)

# 1. URL / ENDPOINT BUILDING
def build_repo_endpoint(owner: str, repo: str) -> str:
    owner = owner.strip()
    repo = repo.strip()
    classic = REPO.format(owner=owner, repo=repo)   # uses the template constant
    modern = f"/repos/{owner}/{repo}"                # direct f-string
    assert classic == modern, "Both styles must produce the same result"
    return modern


def build_collaborator_endpoint(owner: str, repo: str, username: str) -> str:
"""
REAL USE CASE:
Your endpoints.py defines:
REPO_COLLABORATORS = "/repos/{owner}/{repo}/collaborators/{username}"
This builds that path safely.

```
STRING CONCEPTS USED:
    - f-string with multiple variables
    - str.lower()  → GitHub usernames are case-insensitive; normalise before use
"""
return f"/repos/{owner.strip().lower()}/{ repo.strip()}/collaborators/{username.strip().lower()}"
```

# ─────────────────────────────────────────────────────────────────────────────

# 2. RESPONSE FIELD VALIDATION

# ─────────────────────────────────────────────────────────────────────────────

def assert_repo_name_matches(response_name: str, expected_name: str) -> bool:
"""
REAL USE CASE:
In your test_create_repo you assert:
assert response["json"]["name"] == GITHUB_REPO
But what if GitHub returns the name with different casing, or with
leading/trailing whitespace? This function handles it robustly.

```
STRING CONCEPTS USED:
    - str.strip()    → remove whitespace
    - str.lower()    → case-insensitive comparison
    - ==             → exact string equality

WHY IT MATTERS:
    "My-Repo" != "my-repo" in a plain == check.
    Some APIs normalise casing; yours should too.
"""
return response_name.strip().lower() == expected_name.strip().lower()
```

def is_valid_repo_name(name: str) -> bool:
"""
REAL USE CASE:
Before POSTing to /user/repos, validate that the repo name
follows GitHub's rules: only letters, digits, hyphens, underscores, dots.
This prevents sending a bad request and getting a confusing 422 error.

```
STRING CONCEPTS USED:
    - str.isalnum()          → True if all chars are letters or digits
    - str.replace()          → temporarily strip allowed special chars to test the rest
    - len()                  → enforce minimum length
    - in                     → membership check for forbidden characters

WHY IT MATTERS:
    Catching invalid data BEFORE the request is better QA than catching a 422 after.
"""
if not name or len(name) < 1:
    return False
# GitHub allows: a-z A-Z 0-9 - _ .
# Strategy: replace the allowed special chars, then check the rest is alphanumeric
cleaned = name.replace("-", "").replace("_", "").replace(".", "")
return cleaned.isalnum()
```

def extract_repo_owner_from_full_name(full_name: str) -> str:
"""
REAL USE CASE:
GitHub's GET /repos/{owner}/{repo} response includes:
"full_name": "Aferuza/API-automation-framework-with-Python"
You often need just the owner part for assertions or to build the next URL.

```
STRING CONCEPTS USED:
    - str.split(delimiter)   → split on "/" → ["Aferuza", "API-automation-..."]
    - indexing [0]           → get the first element

WHY IT MATTERS:
    Direct string parsing of API response fields is a daily QA task.
    Knowing split() saves you from writing clunky loops.
"""
parts = full_name.split("/")
if len(parts) != 2:
    raise ValueError(f"Unexpected full_name format: '{full_name}'. Expected 'owner/repo'.")
return parts[0]
```

def extract_repo_name_from_full_name(full_name: str) -> str:
"""Same as above but returns the repo portion."""
parts = full_name.split("/")
if len(parts) != 2:
raise ValueError(f"Unexpected full_name format: '{full_name}'.")
return parts[1]

# ─────────────────────────────────────────────────────────────────────────────

# 3. LOGGING & ERROR MESSAGE FORMATTING

# ─────────────────────────────────────────────────────────────────────────────

def format_request_log(method: str, path: str, status_code: int, elapsed: float) -> str:
"""
REAL USE CASE:
Your APIClient logs every request. Right now your log line might look like:
logger.info(f"GET /user → 200 (0.312s)")
This function produces that string consistently across all methods.

```
STRING CONCEPTS USED:
    - str.upper()            → normalise HTTP method ("get" → "GET")
    - f-string               → embed variables
    - :.3f format spec       → format float to 3 decimal places
    - str.ljust(width)       → left-justify for aligned log columns

WHY IT MATTERS:
    Consistent log formatting makes debugging CI failures dramatically faster.
    A recruiter reviewing your GitHub Actions logs will see clean output.
"""
method = method.upper().ljust(6)   # "GET   " — padded to 6 chars for alignment
return f"[{method}] {path} → {status_code} ({elapsed:.3f}s)"
```

def format_assertion_error(field: str, expected, actual) -> str:
"""
REAL USE CASE:
When your schema or payload assertion fails, pytest shows a generic AssertionError.
This builds a clear, human-readable failure message:
"Field 'login': expected 'Aferuza', got 'aferuza'"

```
STRING CONCEPTS USED:
    - f-string with mixed types  (str, int, etc. all work inside {})
    - repr() via !r              → wraps value in quotes automatically

WHY IT MATTERS:
    "AssertionError" tells you nothing. A clear message tells you exactly
    what failed and why — crucial for debugging in CI/CD pipelines.
"""
return f"Field {field!r}: expected {expected!r}, got {actual!r}"
```

# ─────────────────────────────────────────────────────────────────────────────

# 4. AUTHENTICATION / TOKEN HANDLING

# ─────────────────────────────────────────────────────────────────────────────

def mask_token(token: str, visible_chars: int = 4) -> str:
"""
REAL USE CASE:
You must never log a raw Bearer token. When your logger prints auth headers,
you want to show enough to identify the token without exposing it:
"ghp_****...****Ab3X"

```
STRING CONCEPTS USED:
    - len()                  → check token length
    - str slicing [start:end]  → grab first/last N chars
    - str * int              → repeat "*" for the masked portion
    - string concatenation + → join parts

WHY IT MATTERS:
    Leaked tokens in CI logs = security incident.
    This is a real production practice in every company.
"""
if len(token) <= visible_chars * 2:
    return "*" * len(token)
masked_middle = "*" * (len(token) - visible_chars * 2)
return token[:visible_chars] + masked_middle + token[-visible_chars:]
```

def build_bearer_header(token: str) -> str:
"""
REAL USE CASE:
Your auth_client.py builds {"Authorization": "Bearer <token>"}.
This is how that header VALUE string is constructed.

```
STRING CONCEPTS USED:
    - str.startswith()  → check if someone accidentally passed "Bearer ghp_..."
    - f-string          → assemble the header value

WHY IT MATTERS:
    If your .env has AUTH_TOKEN=Bearer ghp_abc, you'd end up with
    "Bearer Bearer ghp_abc" — a real bug that causes 401 errors.
"""
token = token.strip()
if token.lower().startswith("bearer "):
    # already prefixed — strip it before re-adding
    token = token[7:]
return f"Bearer {token}"
```

# ─────────────────────────────────────────────────────────────────────────────

# 5. RESPONSE BODY ASSERTIONS

# ─────────────────────────────────────────────────────────────────────────────

def assert_description_updated(response_description: str, expected_keyword: str) -> bool:
"""
REAL USE CASE:
In your test_update_repo you PATCH the description and assert:
assert response["json"]["description"] == "Updated by automation"
But what if you only care that the description CONTAINS a keyword,
not that it matches exactly? (Common in partial-update testing.)

```
STRING CONCEPTS USED:
    - in operator            → substring membership check
    - str.lower()            → case-insensitive containment

WHY IT MATTERS:
    "Updated by automation" contains "automation" — this is a softer,
    more resilient assertion for dynamic content.
"""
return expected_keyword.lower() in response_description.lower()
```

def normalise_visibility(visibility: str) -> str:
"""
REAL USE CASE:
GitHub returns "visibility": "public" or "private".
Some internal systems might pass "Public", "PUBLIC", "  private  ".
Normalise before asserting.