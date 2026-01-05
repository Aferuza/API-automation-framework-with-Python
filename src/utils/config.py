# - Separates config from code
# - Enables multiple environments (dev/stage/prod)
# - DevOps best practice
import os

from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TIMEOUT = int(os.getenv("TIMEOUT",10))


if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL is missing")

if not AUTH_TOKEN:
    raise RuntimeError("AUTH_TOKEN is missing")

# print("Auth tok loaded:", bool(AUTH_TOKEN))