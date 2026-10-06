"""1.10 apply: decisions -> new docx copy + change log. The only writer in the package.

apply(draft, decisions_path, out) -> ChangeLog
- Re-ingest the draft; rebuild findings; attach decisions. Only ACCEPT (replace/delete rows),
  PICK and DELETE choices produce edits. SKIP/SEEN do nothing.
- For each edit: re-locate the sentence by normalised text (finding_id must match); re-run the
  rule's regex on the current sentence to get the span. Mismatch -> stale, logged, skipped.
- Edit the docx paragraph: concatenate run texts, locate the span, split runs at its boundaries,
  replace the text in the first affected run, delete the text from the others, keep the first
  run's formatting. Delete rows also eat one adjacent space.
- Apply edits right-to-left within a paragraph so offsets stay valid.
- Write `out` (never the input). Write `<out>.changes.md`: location | rule_id | before | after,
  plus the stale list.
- Re-run the checker on `out`; accepted ids must be absent; list new findings in the log.
Tracked changes: Word > Review > Compare (original vs out). Not produced here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from checker.config import Config


@dataclass
class Change:
    rule_id: str
    paragraph: int
    before: str
    after: str
    sentence: str


@dataclass
class ChangeLog:
    applied: list[Change] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)       # finding ids
    new_findings: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        raise NotImplementedError


def replace_in_paragraph(paragraph, start: int, end: int, new_text: str) -> None:
    """python-docx paragraph; offsets relative to ''.join(run.text for run in paragraph.runs)."""
    raise NotImplementedError


def apply(draft: Path, decisions_path: Path, out: Path, config: Config) -> ChangeLog:
    raise NotImplementedError
