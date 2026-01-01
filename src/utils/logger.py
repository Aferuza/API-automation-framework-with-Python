import logging
from time import asctime

# Configure global logging format and level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# Create a reusable logger instance
logger = logging.getLogger(__name__)


