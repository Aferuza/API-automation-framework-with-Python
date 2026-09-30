# smoke_test_logger.py
from src.utils.logger import logger

logger.info("test message", extra={"method": "GET", "endpoint": "/user", "status_code": 200, "elapsed": 0.15})
logger.error("test error", extra={"method": "POST", "endpoint": "/user/repos", "status_code": 422, "elapsed": 0.09})