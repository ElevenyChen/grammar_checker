"""Id -> Python implementation for non-regex rows (scope 1.1).

    @rule("B9.8a", "B9.8b")                 # one function may serve several ids
    def elegant_variation(doc, row, config) -> list[Finding]: ...

    @rule("B.OF", stub=True)                # registered but not built: raises NotImplementedError
    def of_density(doc, row, config): raise NotImplementedError

- check_coverage(table) raises UnimplementedRule listing every Python row with no entry at all,
  so the loader fails loudly before any run. Stubs count as covered.
- run_python_rows runs each row on its own: a stub is reported back as unbuilt and the other
  rows still run.
"""
from __future__ import annotations

from typing import Callable

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow, RuleTable

RuleFn = Callable[[Document, RuleRow, Config], list[Finding]]
RULES: dict[str, RuleFn] = {}
STUBS: set[str] = set()


class UnimplementedRule(RuntimeError):
    pass


def rule(*rule_ids: str, stub: bool = False) -> Callable[[RuleFn], RuleFn]:
    def deco(fn: RuleFn) -> RuleFn:
        for rid in rule_ids:
            if rid in RULES:
                raise RuntimeError(f"duplicate implementation for {rid}")
            RULES[rid] = fn
            if stub:
                STUBS.add(rid)
        return fn
    return deco


def _load_impl() -> None:
    import checker.rules.impl  # noqa: F401  (registers implementations)


def check_coverage(table: RuleTable) -> None:
    _load_impl()
    missing = [r.id for r in table.python_rows if r.id not in RULES]
    if missing:
        raise UnimplementedRule("no Python implementation for: " + ", ".join(missing))


def run_python_rows(doc: Document, table: RuleTable, config: Config) -> tuple[list[Finding], list[RuleRow]]:
    """(findings, rows that are not built yet)."""
    check_coverage(table)
    out: list[Finding] = []
    unbuilt: list[RuleRow] = []
    for row in table.python_rows:
        try:
            out.extend(RULES[row.id](doc, row, config))
        except NotImplementedError:
            unbuilt.append(row)
    return out, unbuilt
