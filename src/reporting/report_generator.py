"""Report path helpers; pytest-html renders test outcomes and details."""

from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"


def create_timestamped_report_path() -> Path:
    """Create the reports directory and return a unique HTML report path."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    return REPORTS_DIR / f"test-report-{timestamp}.html"
