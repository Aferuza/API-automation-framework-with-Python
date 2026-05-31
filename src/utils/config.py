import os
from dotenv import load_dotenv

load_dotenv()

def _require(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: '{var_name}'. "
            f"Check your .env file locally or GitHub Actions secrets in CI."
        )
    return value

# Lazy: read at import, but don't raise — let the fixture raise
API_BASE_URL = os.getenv("API_BASE_URL", "")
AUTH_TOKEN   = os.getenv("AUTH_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")
GITHUB_REPO     = os.getenv("GITHUB_REPO", "")

TIMEOUT               = float(os.getenv("TIMEOUT", "10"))
PERFORMANCE_THRESHOLD = float(os.getenv("PERFORMANCE_THRESHOLD", "1.5"))