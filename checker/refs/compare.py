"""Metadata comparison (ported from check_refs.compare). Returns (status, notes) with status in
PASS / WARN / FAIL. Thresholds from config.refs.title_sim_fail / title_sim_warn (§5 calibration rows).
norm() and title_sim() come across unchanged.
"""
from __future__ import annotations

from checker.config import Config
from checker.refs.entries import Entry


def norm(s: str) -> str:
    raise NotImplementedError


def title_sim(a: str, b: str) -> float:
    raise NotImplementedError


def compare(entry: Entry, remote: dict, config: Config) -> tuple[str, list[str]]:
    raise NotImplementedError
