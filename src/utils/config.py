# - Separates config from code
# - Enables multiple environments (dev/stage/prod)
# - DevOps best practice
import os

from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
API_TOKEN = os.getenv("API_TOKEN")

if not API_BASE_URL or not API_TOKEN:
    raise RuntimeError("Missing API Configs")