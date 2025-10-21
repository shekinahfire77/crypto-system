"""Script to run tests with coverage report."""

#!/usr/bin/env python3
"""
Run tests with coverage report.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --coverage   # Run with coverage
    python run_tests.py --cov=70     # Set minimum coverage threshold
"""

import subprocess
import sys
from typing import Optional


def run_tests(coverage: bool = False, min_coverage: Optional[int] = None) -> int:
    """Run tests with optional coverage."""
    cmd = ["pytest", "tests/", "-v", "--tb=short"]

    if coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing",
        ])

        if min_coverage:
            cmd.append(f"--cov-fail-under={min_coverage}")

    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point."""
    coverage = "--coverage" in sys.argv or "--cov" in sys.argv
    min_coverage = None

    for arg in sys.argv[1:]:
        if arg.startswith("--cov="):
            min_coverage = int(arg.split("=")[1])

    return run_tests(coverage=coverage, min_coverage=min_coverage)


if __name__ == "__main__":
    sys.exit(main())
