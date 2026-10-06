"""A7 repeated passages (scope 1.4): shared n-gram (config.thresholds.ngram) across paragraphs.

Shingle each body paragraph's lowercase content tokens; map shingle -> paragraph ids; any shingle
in two paragraphs yields one Finding per pair at the first paragraph with extra["other"] = the
second location. Merge overlapping shingles into one span. Severity gate.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow
from checker.rules.registry import rule


@rule("A7")
def repeated_passages(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError
