# src/utils/config.py

import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# ── API Config ─────────────────────────────────────────────────────────────────
API_BASE_URL          = os.getenv("API_BASE_URL")
TIMEOUT               = int(os.getenv("TIMEOUT", 10))
PERFORMANCE_THRESHOLD = float(os.getenv("PERFORMANCE_THRESHOLD", 1.5))

# ── Auth ───────────────────────────────────────────────────────────────────────
AUTH_TOKEN            = os.getenv("AUTH_TOKEN")

# ── GitHub Identity ────────────────────────────────────────────────────────────
GITHUB_USERNAME       = os.getenv("GITHUB_USERNAME")  # fills {owner} in endpoint templates
GITHUB_REPO           = os.getenv("GITHUB_REPO")       # fills {repo} in endpoint templates

# ── Validation — fail immediately if critical values are missing ───────────────
# Catches missing .env values before any test runs
# Much clearer than a cryptic 401 or URL error mid-test

if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL is missing from .env")

if not AUTH_TOKEN:
    raise RuntimeError("AUTH_TOKEN is missing from .env")

if not GITHUB_USERNAME:
    raise RuntimeError("GITHUB_USERNAME is missing from .env")

if not GITHUB_REPO:
    raise RuntimeError("GITHUB_REPO is missing from .env")