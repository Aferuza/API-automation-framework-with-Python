# Reusable logic using nested and lambda functions.
import time

def retry_request(request_fn, retries=3, delay=2):
    def attempt():
        for i in range(retries):
            response = request_fn()
            if response.status_code == 200:
                return response
            time.sleep(delay)
        return response
    return attempt()

def get_cleaned_users(raw_list):
    return list(map(lambda u: u.strip().lower(), raw_list))

def validate_response(response, validator_fn):
    return validator_fn(response)


def get_jwt_token():
    return None