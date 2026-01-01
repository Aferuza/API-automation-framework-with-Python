import sys
import os

sys.path.insert(0, os.path.abspath("src"))
import pytest
from src.reporting.report_generator import generate_report
# from reporting.report_generator import generate_report
# Run pytest quietly
result = pytest.main(["-q"])

# Determine test outcome
status = "PASS" if result == 0 else "FAIL"

# Generate HTML report
generate_report(status=status, time="See logs")

print("Test execution complete. Report generated.")
