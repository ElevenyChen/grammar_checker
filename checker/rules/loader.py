"""Parse the machine appendix in llm_polishing.md into RuleRow objects (scope 1.1).

Appendix row format (inside the ```-fenced block under "## Appendix — machine view"):
    id | step | severity | action | pattern | replacement
Columns are separated by " | " (whitespace on both sides); a pipe inside a regex never has
whitespace before it. The pre-id format (first column a digit) raises MissingRuleId.

Row semantics:
- Trailing qualifiers in the pattern column, stripped before compiling: "(case-sensitive)" turns
  off re.I; "(paragraph start)" restricts the row to a paragraph's first sentence; "(verb)" and
  "(adverb)" set `pos`, a part-of-speech filter applied to each hit by regex_rules.
- A named group `hit` in the pattern sets the reported span (whole-sentence patterns, A4.2).
- known_terms(path) reads the "### Known terms (A6 exemptions)" block that follows the appendix.
- `is_regex` is True when the remaining pattern holds no prose marker (NON_REGEX_MARKERS) and
  compiles. Everything else is a Python row, dispatched by id via rules.registry.
- action "skip" (B9.5) is a suppression row, kept in `skip_rows`.
- Last column: replacement for replace/delete rows, note for flag rows.
  " / " splits a replacement into candidates (pick row).
- `grade`: SENTENCE when the replacement uses backreferences (\\1, \\2); else WORD.
- `can_delete`: flag rows whose note names deletion as an outcome.
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
    "(non-temporal)", "paragraph-initial", "defined term", "(POS)",
    "where value", "(both sides nominalized)",
)
QUALIFIER_RE = re.compile(r"\s+\((case-sensitive|paragraph start|verb|adverb)\)\s*$")
KNOWN_TERMS_HEADING = "### Known terms (A6 exemptions)"
COLUMN_SPLIT_RE = re.compile(r"\s+\|(?:\s+|$)")
BACKREF_RE = re.compile(r"\\\d")


class MissingRuleId(ValueError):
    pass


class RuleTableError(ValueError):
    pass


@dataclass
class RuleRow:
    id: str
    step: Step
    severity: Severity | None        # None for skip rows
    action: Action | None            # None for skip rows
    pattern: str                     # qualifiers stripped
    replacement: str | None          # replace/delete rows
    note: str                        # flag rows: the last column; others: ""
    is_regex: bool
    compiled: re.Pattern | None = None
    candidates: list[str] = field(default_factory=list)
    grade: Grade = Grade.WORD
    can_delete: bool = False
    case_sensitive: bool = False
    paragraph_start: bool = False
    pos: str | None = None           # "verb" | "adverb": keep only hits with that part of speech
    is_skip: bool = False
    raw: str = ""

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
    start = md_text.find(APPENDIX_HEADING)
    if start == -1:
        raise RuleTableError(f"no '{APPENDIX_HEADING}' heading")
    open_ = md_text.find("```", start)
    close = md_text.find("```", open_ + 3)
    if open_ == -1 or close == -1:
        raise RuleTableError("appendix fenced block not found")
    body = md_text[open_ + 3:close]
    return body.split("\n", 1)[1] if "\n" in body else ""


def looks_like_regex(pattern: str) -> bool:
    return not any(m in pattern for m in NON_REGEX_MARKERS)


def parse_row(line: str) -> RuleRow | None:
    """One appendix line -> RuleRow; None for blank lines. Raises MissingRuleId / RuleTableError."""
    if not line.strip():
        return None
    parts = [p.strip() for p in COLUMN_SPLIT_RE.split(line.rstrip() + " ", maxsplit=5)]
    if parts and parts[0].isdigit():
        raise MissingRuleId(f"appendix row has no id column: {line.strip()[:60]!r}")
    if len(parts) != 6:
        raise RuleTableError(f"expected 6 columns, got {len(parts)}: {line.strip()[:80]!r}")
    rid, step_s, sev_s, action_s, pattern, last = parts
    step = Step(int(step_s))
    is_skip = action_s == "skip"
    severity = None if is_skip else Severity(sev_s)
    action = None if is_skip else Action(action_s)

    case_sensitive = paragraph_start = False
    pos = None
    while True:
        m = QUALIFIER_RE.search(pattern)
        if not m:
            break
        q = m.group(1)
        case_sensitive |= q == "case-sensitive"
        paragraph_start |= q == "paragraph start"
        if q in ("verb", "adverb"):
            pos = q
        pattern = pattern[:m.start()]

    is_regex = looks_like_regex(pattern)
    compiled = None
    if is_regex:
        try:
            compiled = re.compile(pattern, 0 if case_sensitive else re.I)
        except re.error:
            is_regex = False

    takes_text = action in (Action.REPLACE, Action.DELETE)
    replacement = (last if takes_text else None)
    if action == Action.DELETE:
        replacement = ""
    note = "" if takes_text else last
    candidates = [c.strip() for c in last.split(" / ")] if takes_text and " / " in last else []
    grade = Grade.SENTENCE if replacement and BACKREF_RE.search(replacement) else Grade.WORD
    can_delete = action == Action.FLAG and "delete" in note.lower()

    return RuleRow(
        id=rid, step=step, severity=severity, action=action, pattern=pattern,
        replacement=replacement, note=note, is_regex=is_regex, compiled=compiled,
        candidates=candidates, grade=grade, can_delete=can_delete,
        case_sensitive=case_sensitive, paragraph_start=paragraph_start, pos=pos, is_skip=is_skip,
        raw=line.strip(),
    )


def known_terms(path: Path) -> set[str]:
    """Lower-cased terms from the known-terms block; empty if the block is absent."""
    text = Path(path).read_text(encoding="utf-8")
    start = text.find(KNOWN_TERMS_HEADING)
    if start == -1:
        return set()
    open_ = text.find("```", start)
    close = text.find("```", open_ + 3)
    if open_ == -1 or close == -1:
        return set()
    body = text[open_ + 3:close].split("\n", 1)[-1]
    return {line.strip().lower() for line in body.splitlines() if line.strip()}


def load(path: Path) -> RuleTable:
    """Parse the appendix, validate ids are unique, return the table."""
    text = Path(path).read_text(encoding="utf-8")
    rows: list[RuleRow] = []
    skips: list[RuleRow] = []
    seen: set[str] = set()
    for line in extract_appendix_block(text).splitlines():
        row = parse_row(line)
        if row is None:
            continue
        if row.id in seen:
            raise RuleTableError(f"duplicate rule id {row.id}")
        seen.add(row.id)
        (skips if row.is_skip else rows).append(row)
    return RuleTable(rows=rows, skip_rows=skips, source=Path(path))
