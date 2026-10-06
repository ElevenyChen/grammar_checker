"""`checker stats report.json`: per-rule table of count, share of sentences flagged, and the
decisions so far (accept vs skip = observed precision). Warn when share > 0.30: wrong threshold,
not a bad draft. Output: markdown table to stdout and `<report>.stats.md`.
"""
from __future__ import annotations

from pathlib import Path


def run(report_path: Path, out: Path | None = None) -> str:
    raise NotImplementedError
