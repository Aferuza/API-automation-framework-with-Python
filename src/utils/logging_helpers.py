import time
import requests


def format_request_log(method: str, path: str, status_code: int, elapsed: float) -> str:
    method = method.upper().ljust(6)
    return f"[{method}]{path} -> {status_code} ({elapsed:.3f}s)"


def send_request(method, url, **kwargs):
    start = time.perf_counter()
    response = requests.request(method, url, **kwargs)
    elapsed = time.perf_counter() - start

    log_line = format_request_log(
        method, response.request.path_url, response.status_code, elapsed
    )
    print(log_line)

    return response