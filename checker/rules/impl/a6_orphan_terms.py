"""A6 orphan terms (scope 1.4, appendix step-1 row).

Candidates: capitalised tokens that are not sentence-initial and not in a protected span, plus
"<word> (analysis|model|test|procedure)" bigrams. A candidate whose first occurrence is in a
section with kind.after_results is flagged once, at that first occurrence, severity gate.
Exclude: H labels, "Table"/"Figure", months, the paper's own section names.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow
from checker.rules.registry import rule


@rule("A6")
def orphan_terms(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError
