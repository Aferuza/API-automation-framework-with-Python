import os
from dotenv import load_dotenv

load_dotenv()

def _require(var_name: str) -> str:
    """Fetch a required env variable or raise immediately with a clear message."""
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: '{var_name}'. "
            f"Check your .env file locally or GitHub Actions secrets in CI."
        )
    return value

API_BASE_URL = _require("API_BASE_URL")
AUTH_TOKEN = _require("AUTH_TOKEN")
GITHUB_USERNAME = _require("GHUB_USERNAME")
GITHUB_REPO = _require("GHUB_REPO")
TIMEOUT = float(os.getenv("TIMEOUT", "10"))
PERFORMANCE_THRESHOLD = float(os.getenv("PERFORMANCE_THRESHOLD", "1.5"))
