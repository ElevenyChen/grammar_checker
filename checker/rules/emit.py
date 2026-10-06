"""Build Finding records from rule rows. Shared by regex_rules and the Python rows in rules/impl,
so every rule fills the record the same way (scope 1.8)."""
from __future__ import annotations

from typing import Any

from checker.findings import Finding, Location, finding_id
from checker.model import Sentence, Span
from checker.rules.loader import RuleRow


def location(sentence: Sentence, span: Span) -> Location:
    sec = sentence.section
    return Location(section=sec.name, section_kind=sec.kind.value,
                    paragraph=sentence.paragraph.index, sentence=sentence.index, span=span)


def finding(row: RuleRow, sentence: Sentence, span: Span, occurrence: int = 0, *,
            evidence: str | None = None, suggestion: str | None = None,
            candidates: list[str] | None = None, score: float | None = None,
            extra: dict[str, Any] | None = None) -> Finding:
    """One finding for `row` at absolute `span` inside `sentence`.
    Flag rows default their suggestion to the row's note."""
    if suggestion is None and not candidates and row.note:
        suggestion = row.note
    return Finding(
        id=finding_id(row.id, sentence.text, occurrence),
        step=row.step,
        severity=row.severity,
        rule_id=row.id,
        action=row.action,
        location=location(sentence, span),
        evidence=evidence if evidence is not None else _slice(sentence, span),
        sentence=sentence.text,
        suggestion=suggestion,
        candidates=candidates or [],
        module=row.module,
        grade=row.grade,
        can_delete=row.can_delete,
        score=score,
        extra=extra or {},
    )


def _slice(sentence: Sentence, span: Span) -> str:
    a = span.start - sentence.span.start
    b = span.end - sentence.span.start
    return sentence.text[max(a, 0):max(b, 0)] if b <= len(sentence.text) else sentence.text[max(a, 0):]
