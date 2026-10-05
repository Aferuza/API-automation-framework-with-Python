"""Run pytest and save a timestamped self-contained HTML report."""

import os
import sys
from pathlib import Path

import pytest
from src.reporting.report_generator import create_timestamped_report_path


ROOT = Path(__file__).resolve().parent


def main():
    os.chdir(ROOT)
    report_path = create_timestamped_report_path()
    arguments = [
        "-o",
        "addopts=",
        *sys.argv[1:],
        "--html",
        str(report_path),
        "--self-contained-html",
    ]
    return pytest.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
