"""decisions.json (scope 1.8 / §7): load, attach to findings, save, and the Module A gate.

File shape: {"source": "...", "decisions": [Decision.as dict, ...]}
- load(path) -> dict[id, Decision]
- attach(findings, decisions): set Finding.decision where ids match. A decision whose id no
  longer matches any finding is kept in the file (the sentence changed) and reported in
  Report.stats["stale_decisions"].
- module_a_cleared(findings): every Finding with module A and severity gate has a decision.
- merge(old, new): page exports replace earlier choices for the same id; others are kept.
"""
from __future__ import annotations

from pathlib import Path

from checker.findings import Decision, Finding


def load(path: Path | None) -> dict[str, Decision]:
    raise NotImplementedError


def save(path: Path, source: str, decisions: dict[str, Decision]) -> None:
    raise NotImplementedError


def attach(findings: list[Finding], decisions: dict[str, Decision]) -> list[str]:
    """Returns ids of stale decisions (no matching finding)."""
    raise NotImplementedError


def module_a_cleared(findings: list[Finding]) -> bool:
    """Every Module A gate finding has a decision. Vacuously true when there are none."""
    return all(f.decision is not None for f in findings
               if f.module.value == "A" and f.severity.value == "gate")


def merge(old: dict[str, Decision], new: dict[str, Decision]) -> dict[str, Decision]:
    raise NotImplementedError
