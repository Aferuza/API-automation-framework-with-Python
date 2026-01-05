from datetime import time
import requests
from auth.auth_client import get_auth_headers
from src.utils.config import API_BASE_URL, AUTH_TOKEN, TIMEOUT
from src.utils.logger import logger

#  All HTTP calls now automatically include auth, logging, response time, and structured output.
# defines how requests are made.
# The requests are executed when tests (or scripts) call its methods.
class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "Content-Type": "application/json"
        }

    # def get(self, endpoint):
    #     response = requests.get(f"{self.base_url}{endpoint}",
    #         headers=self.headers,
    #         timeout=TIMEOUT
    #     )
    #     print(f"Github GET request details:")
    #     return {
    #         "status_code": response.status_code,
    #         "json": response.json(),
    #         "response_time": response.elapsed.total_seconds()
    #     }
'''Create repo (POST)
Update repo settings (PATCH)
Validate repo metadata (GET)
Delete repo (DELETE)'''

# Build full URL
def request(self, method, endpoint, json_body=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = get_auth_headers()
    # Start Timer
    start = time.time()
    # Send HTTP Request
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=json_body
    )
    # Compute Elapsed Time
    elapsed = time.time() - start
    # Logging
    logger.info(
        f"{method} {endpoint} -> {response.status_code} ({elapsed:.3f}s)"
    )
    # Returns a dictionary containing all useful info for tests
    return {
        "status_code": response.status_code,
        "json": response.json() if response.content else {},
        "headers": response.headers,
        "response_time": elapsed
    }

def get(self, endpoint):
    return self.request("GET", endpoint)

def post(self, endpoint, body):
    return self.request("POST", endpoint, body)

def patch(self, endpoint, body):
    return self.request("PATCH", endpoint, body)

def delete(self, endpoint):
    return self.request("DELETE", endpoint)
