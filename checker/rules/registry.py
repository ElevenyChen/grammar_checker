"""Id -> Python implementation for non-regex rows (scope 1.1).

    @rule("B9.8")
    def elegant_variation(doc, row, config) -> list[Finding]: ...

`check_coverage(table)` raises UnimplementedRule listing every python row without an entry,
so the loader fails loudly before any run.
"""
from __future__ import annotations

from typing import Callable

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow, RuleTable

RuleFn = Callable[[Document, RuleRow, Config], list[Finding]]
RULES: dict[str, RuleFn] = {}


class UnimplementedRule(RuntimeError):
    pass


def rule(rule_id: str) -> Callable[[RuleFn], RuleFn]:
    def deco(fn: RuleFn) -> RuleFn:
        if rule_id in RULES:
            raise RuntimeError(f"duplicate implementation for {rule_id}")
        RULES[rule_id] = fn
        return fn
    return deco


def check_coverage(table: RuleTable) -> None:
    missing = [r.id for r in table.python_rows if r.id not in RULES]
    if missing:
        raise UnimplementedRule("no Python implementation for: " + ", ".join(missing))


def run_python_rows(doc: Document, table: RuleTable, config: Config) -> list[Finding]:
    import checker.rules.impl  # noqa: F401  (registers implementations)
    check_coverage(table)
    out: list[Finding] = []
    for row in table.python_rows:
        out.extend(RULES[row.id](doc, row, config))
    return out
