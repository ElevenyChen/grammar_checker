"""`checker tune pairs.csv`: for each score column, sweep cuts and pick the F1-best; print the
table and the recommended soft_link value for checker.toml. Also reports which score column wins,
so the fallback order in checks.soft can be simplified if one column dominates.
"""
from __future__ import annotations

from pathlib import Path


def run(pairs_csv: Path) -> dict[str, float]:
    raise NotImplementedError
