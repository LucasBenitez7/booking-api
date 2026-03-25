"""
Newman runner — equivalent to ticketmaster's test:api npm script.

Usage:
    uv run test-api        # with HTML report (opens postman/results.html)
    uv run test-api-ci     # plain CLI output only (for CI)

Requires Newman: npm install -g newman
Optional HTML report: npm install -g newman-reporter-htmlextra
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLLECTION = ROOT / "postman" / "collection.json"
ENVIRONMENT = ROOT / "postman" / "environment.json"
REPORT = ROOT / "postman" / "results.html"


def _run(extra_args: list[str]) -> None:
    cmd = [
        "newman",
        "run",
        str(COLLECTION),
        "-e",
        str(ENVIRONMENT),
        *extra_args,
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def main() -> None:
    """With HTML report (newman-reporter-htmlextra required)."""
    _run(
        [
            "--reporters",
            "cli,htmlextra",
            "--reporter-htmlextra-export",
            str(REPORT),
        ]
    )


def ci() -> None:
    """Plain CLI output — suitable for CI pipelines."""
    _run(["--reporters", "cli"])
