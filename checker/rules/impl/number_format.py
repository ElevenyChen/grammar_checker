"""Appendix rows B7.4–B7.6 (advisor-specific format rows; scope 1.7) that are 'both present' checks over the whole body (scope 1.7).

- Chi-squared vs χ²: both spellings present -> one Finding per minority occurrence.
- Thousands separators: \\d{4,} without comma and \\d,\\d{3} both present (exclude years 19xx/20xx,
  p-values, DOIs, protected spans).
- Leading zero: (?<![\\d.])\\.\\d+ where the value can exceed 1 (not after p, r, β, α, η²,
  which are bounded; APA 6.36).
Severity style.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow
from checker.rules.registry import rule


@rule("B7.4", stub=True)
def chi_squared_mixed(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


@rule("B7.5", stub=True)
def thousands_mixed(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


@rule("B7.6", stub=True)
def leading_zero(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError
