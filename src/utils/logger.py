import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
if LOG_LEVEL not in VALID_LEVELS:
    raise ValueError(
        f"Invalid LOG_LEVEL '{LOG_LEVEL}'. Must be one of: {', '.join(sorted(VALID_LEVELS))}"
    )

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)