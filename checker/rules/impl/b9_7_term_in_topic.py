"""B9.7 term in topic position: a term's first occurrence lands in the first six words of its
sentence. Needs the glossary list; without one, derive terms as in A6 (capitalised + X analysis).
Severity style. Skip if the sentence is paragraph-initial in the section that defines the term.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow
from checker.rules.registry import rule


@rule("B9.7")
def term_in_topic(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError
