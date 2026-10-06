"""Parse the machine appendix in llm_polishing.md into RuleRow objects (scope 1.1).

Expected appendix row format, after the id column is added (build step 2):
    id | step | severity | action | pattern | replacement
inside the ```-fenced block under "## Appendix — machine view". The pre-id format
    step | severity | action | pattern | replacement
must raise MissingRuleId so nobody runs the tool on an un-keyed table.

Row semantics:
- `is_regex` is True when `pattern` compiles with re.I (case-insensitive unless the replacement
  column says "(case-sensitive)") AND the pattern contains no prose annotation. A prose annotation
  is anything matching the NON_REGEX_MARKERS below. Non-regex rows are dispatched by id via
  rules.registry.
- action "skip" (B9.5) is a suppression row, kept in `skip_rows`.
- `candidates`: a replacement containing " / " splits into alternatives (pick row).
- `grade`: SENTENCE when the replacement uses backreferences (\\1, \\2) or the note says
  "sentence"; else WORD.
- `can_delete`: True for flag rows whose replacement/note contains "delete".
- `module`: step 1 -> A, step 3 -> B, else NONE.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from checker.findings import Action, Grade, Module, Severity, Step

APPENDIX_HEADING = "## Appendix — machine view"
NON_REGEX_MARKERS = (
    "≥", "both present", "density", "in one section", "first occurrence", "shared",
    "(verb)", "(non-temporal)", "(paragraph start)", "paragraph-initial", "defined term",
    "where value", "(both sides nominalized)",
)


class MissingRuleId(ValueError):
    pass


@dataclass
class RuleRow:
    id: str
    step: Step
    severity: Severity | None        # None for skip rows
    action: Action | None            # None for skip rows
    pattern: str
    replacement: str | None
    note: str                        # free text after the replacement, if any
    is_regex: bool
    compiled: re.Pattern | None = None
    candidates: list[str] = field(default_factory=list)
    grade: Grade = Grade.WORD
    can_delete: bool = False
    case_sensitive: bool = False
    is_skip: bool = False

    @property
    def module(self) -> Module:
        return Module.A if self.step == Step.CLAIM else Module.B if self.step == Step.LANGUAGE else Module.NONE


@dataclass
class RuleTable:
    rows: list[RuleRow]
    skip_rows: list[RuleRow]
    source: Path

    def by_id(self, rule_id: str) -> RuleRow:
        for r in self.rows + self.skip_rows:
            if r.id == rule_id:
                return r
        raise KeyError(rule_id)

    @property
    def regex_rows(self) -> list[RuleRow]:
        return [r for r in self.rows if r.is_regex]

    @property
    def python_rows(self) -> list[RuleRow]:
        return [r for r in self.rows if not r.is_regex]


def extract_appendix_block(md_text: str) -> str:
    """Text inside the first fenced block after APPENDIX_HEADING."""
    raise NotImplementedError


def parse_row(line: str) -> RuleRow | None:
    """One `|`-separated line -> RuleRow; None for blank lines. Raises MissingRuleId."""
    raise NotImplementedError


def load(path: Path) -> RuleTable:
    """Parse the appendix, compile regex rows, validate ids are unique, return the table."""
    raise NotImplementedError


def looks_like_regex(pattern: str) -> bool:
    return not any(m in pattern for m in NON_REGEX_MARKERS)
