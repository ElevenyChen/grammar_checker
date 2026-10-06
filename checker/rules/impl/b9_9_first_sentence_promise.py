"""B9.9 first-sentence promise (scope 1.4): last 3–4 content words of a paragraph's first sentence
do not recur (stem/lemma match) in the rest of the paragraph.

Paragraphs with >= 3 sentences only (shorter ones are caught by the 1.4 short-paragraph symptom).
Severity gate per the table, but it is a §5 re-grade candidate; report the matched/unmatched
words in extra so the false-positive count is easy.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow
from checker.rules.registry import rule


@rule("B9.9", stub=True)
def first_sentence_promise(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError
