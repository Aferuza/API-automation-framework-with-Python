import time
from http.client import responses
from turtledemo.penrose import start

import requests

from src.utils.config import API_BASE_URL
from src.auth.auth_client import get_auth_headers
from src.utils.logger import logger

class APIClient:
    # make a get request
    def get(self, endpoint):
        url = f"{API_BASE_URL}{endpoint}"
        headers= get_auth_headers()
        start=time.time()
        response= requests.get(url, headers=headers)
        elapsed = time.time()-start
        logger.info(f"GET{endpoint}->{response.status_code}({elapsed:.3f}s)")
        return {"status_code":response.status_code,
                "json":response.json(),
                "headers": response.headers,
                "response_time":elapsed}

