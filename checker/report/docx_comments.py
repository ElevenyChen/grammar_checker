"""Fourth renderer (scope 1.8, later): one Word comment per finding on a copy of the draft.
Requires python-docx >= 1.2 (document.add_comment on a run range). Original untouched.
Comment text: `rule_id · severity · suggestion`. Sharing format for advisors.
"""
from __future__ import annotations

from pathlib import Path

from checker.findings import Report


def write(report: Report, draft: Path, out: Path) -> Path:
    raise NotImplementedError
