"""Appendix step-3 rows that need the parse rather than a regex.

- of-density: count "of" per sentence; flag when > 1 per config.thresholds.of_density_per_words.
- while (non-temporal): token "while" whose clause has no time expression (no DATE/TIME entity,
  no "when/during/as" nearby) -> suggest although.
- since (non-temporal): same shape -> suggest because.
- impact (verb): token.lemma_ == "impact" and pos_ == VERB -> replace affect (inflected).
- passive with agent: auxpass + agent child; flag only, note "judge by B9.H4".
Ids below are placeholders until the id column exists; rename to match the appendix.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow
from checker.rules.registry import rule


@rule("B.OF")
def of_density(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


@rule("B.WHILE")
def while_non_temporal(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


@rule("B.SINCE")
def since_non_temporal(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


@rule("B2.IMPACT")
def impact_verb(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


@rule("B.PASSIVE")
def passive_with_agent(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError
