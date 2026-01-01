import requests
import os

def get_jwt_token():
    """Authenticate with API and return JWT token."""
    url = os.getenv("TOKEN_URL", "https://api.example.com/login")
    credentials = {
        "username": os.getenv("API_USER"),
        "password": os.getenv("API_PASS")
    }
    response = requests.post(url, json=credentials)
    response.raise_for_status()
    return response.json().get("access_token")
