"""Inflection and case for replace rows (scope 1.1): "Utilizes" -> "Uses", "utilized" -> "used".

render(row, match) -> str:
- replacement from the row; if it holds backreferences, expand with match.expand.
- Inflect: if the matched head word ends in s/es/ed/ing and the replacement is a bare verb in
  FORM_MAP, pick the matching form. FORM_MAP is tiny and explicit; do not import an inflector.
- Case: copy the first-letter case of the match. All-caps matches stay all-caps.
- delete rows return "" and the caller also eats one adjacent space.
Tested by tests/test_forms.py against tests/fixtures/forms.csv (before,rule_id,after).
"""
from __future__ import annotations

import re

from checker.rules.loader import RuleRow

FORM_MAP: dict[str, dict[str, str]] = {
    "use":     {"s": "uses", "ed": "used", "ing": "using"},
    "show":    {"s": "shows", "ed": "showed", "ing": "showing"},
    "explain": {"s": "explains", "ed": "explained", "ing": "explaining"},
    "help":    {"s": "helps", "ed": "helped", "ing": "helping"},
    "try":     {"s": "tries", "ed": "tried", "ing": "trying"},
    "begin":   {"s": "begins", "ed": "began", "ing": "beginning"},
    "end":     {"s": "ends", "ed": "ended", "ing": "ending"},
    "affect":  {"s": "affects", "ed": "affected", "ing": "affecting"},
    "develop": {"s": "develops", "ed": "developed", "ing": "developing"},
    "change":  {"s": "changes", "ed": "changed", "ing": "changing"},
    "find out": {"s": "finds out", "ed": "found out", "ing": "finding out"},
}


def detect_form(word: str) -> str:
    """'' | 's' | 'ed' | 'ing' from the matched word's ending."""
    raise NotImplementedError


def apply_case(template: str, text: str) -> str:
    raise NotImplementedError


def render(row: RuleRow, match: re.Match) -> str:
    raise NotImplementedError
