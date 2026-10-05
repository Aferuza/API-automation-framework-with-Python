import base64
import hashlib
import json
import os
import re
import pytest
from pathlib import Path
from pytest_html import extras
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from src.utils.config import API_BASE_URL, AUTH_TOKEN
from src.api.api_client import APIClient
from src.api.endpoints import USER_REPOS, REPO
from src.utils.config import GITHUB_REPO, GITHUB_USERNAME

ROOT = Path(__file__).parent.parent
SCREENSHOTS_DIR = ROOT / "reports" / "screenshots"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save and embed a browser screenshot for each test that used Selenium."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return

    driver = item.funcargs.get("driver")
    if driver is None:
        return

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)[:120]
    suffix = hashlib.sha1(item.nodeid.encode("utf-8")).hexdigest()[:10]
    screenshot_path = SCREENSHOTS_DIR / f"{safe_name}-{suffix}.png"

    try:
        screenshot = driver.get_screenshot_as_base64()
        screenshot_path.write_bytes(base64.b64decode(screenshot))
        report.extras = list(getattr(report, "extras", []))
        report.extras.append(extras.png(screenshot, name="Browser screenshot"))
    except WebDriverException as error:
        report.extras = list(getattr(report, "extras", []))
        report.extras.append(
            extras.text(f"Could not capture browser screenshot: {error}", name="Screenshot note")
        )


@pytest.fixture
def driver():
    """Create an isolated Chrome session for UI tests and API-to-UI checks."""
    options = Options()
    if os.getenv("UI_HEADLESS", "true").lower() in {"1", "true", "yes"}:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(2)
    yield browser
    browser.quit()


def load_user_schema() -> dict:
    with open(ROOT / "src" / "validation" / "schemas" / "user_schema.json") as f:
        return json.load(f)


def load_repo_schema() -> dict:
    with open(ROOT / "src" / "validation" / "schemas" / "repo_schema.json") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def client():
    # Only raise here — mocked tests never call this fixture
    if not API_BASE_URL or not AUTH_TOKEN:
        pytest.skip("Live credentials not configured — skipping live tests")
    return APIClient(base_url=API_BASE_URL, token=AUTH_TOKEN)


@pytest.fixture(scope="module")
def user_schema():
    return load_user_schema()


@pytest.fixture(scope="module")
def repo_schema():
    return load_repo_schema()


@pytest.fixture(scope="module")
def managed_repo(client):
    repo_endpoint = REPO.format(owner=GITHUB_USERNAME, repo=GITHUB_REPO)

    # Defensive cleanup: if a prior run crashed mid-suite (CI timeout,
    # killed process, etc.), the yield-based teardown below never ran.
    # Delete first so create() below always starts from a clean slate.
    # A 404 here is expected and fine — nothing to clean up — so it's
    # excluded from ERROR logging via quiet_statuses.
    client.delete(repo_endpoint, quiet_statuses=(404,))

    create_response = client.post(USER_REPOS, body={
        "name": GITHUB_REPO,
        "description": "Created by API automation framework",
        "private": False,
        "auto_init": True
    })
    assert create_response["status_code"] == 201, (
        f"Setup failed — could not create repo: {create_response['status_code']}"
    )

    yield create_response

    response = client.delete(repo_endpoint)
    assert response["status_code"] in (204, 404), (
        f"Unexpected status during teardown delete: {response['status_code']}"
    )
