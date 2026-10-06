"""Run regex rows over sentences (scope 1.1).

run(doc, table, config):
1. Build the B9.5 skip set: sentences whose subject matches a skip row; B9.1–B9.3 do not fire there.
2. For each body sentence and each regex row: finditer on sentence.text (anchors ^ $ are sentence
   anchors by construction). Drop hits overlapping Sentence.protected.
3. Section exemptions: the B4 "we found that" row is skipped in INTRODUCTION/CONCLUSION; the
   "(paragraph start)" rows only test sentence.index == 0.
4. Build a Finding: evidence = matched text; suggestion = forms.render(row, match) for
   replace/delete rows; candidates for pick rows; grade/can_delete from the row; module from step.
5. Finding.id = finding_id(row.id, sentence.text, occurrence) where occurrence counts hits of the
   same rule in the same sentence.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document, Sentence
from checker.rules.loader import RuleRow, RuleTable

SKIP_PROTECTS = {"B9.1", "B9.2", "B9.3"}
INTRO_CONCLUSION_EXEMPT = {"B4.1"}          # ids assigned in build step 2; keep in sync with appendix


def skip_set(doc: Document, table: RuleTable) -> set[int]:
    """doc_index of sentences protected by B9.5."""
    raise NotImplementedError


def run_row(sentence: Sentence, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


def run(doc: Document, table: RuleTable, config: Config) -> list[Finding]:
    raise NotImplementedError
