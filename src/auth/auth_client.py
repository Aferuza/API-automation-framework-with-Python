from src.utils.config import AUTH_TOKEN

# Returns authentication headers for API requests
def get_auth_headers():
    return {
        # Bearer token authentication
        "Authorization": f"Bearer {AUTH_TOKEN}",

        # Request JSON responses
        "Accept": "application/json"
    }
