"""Inflection and case for replace rows (scope 1.1): "Utilizes" -> "Uses", "utilized" -> "used".

render_candidates(row, match) -> list[str]   every candidate, rendered
render(row, match) -> str                     the first (or only) candidate

Rendering, in order:
1. Keywords in the replacement column: "lowercase" (B7.2; keeps a capital at sentence start),
   "first word only" (B9.10).
2. Backreferences (\\1, \\2) are expanded with match.expand (B9.3).
3. Tense pair "can / could" (B1.21) resolves to one word from the matched auxiliary:
   is/are -> can, was/were -> could. It is not a pick row once rendered.
4. "word(s)" (B2.5 "method(s)"): plural when the match is plural.
5. Inflection: a bare verb in FORM_MAP takes the form of the matched word
   (-s, -ed, -ing, or the -tion/-ment noun). Only single-word matches are inflected.
6. Case: all-caps match -> all caps; capitalised match -> capitalised replacement.
Delete rows render "". Eating the adjacent space and re-capitalising the next word is apply's job.
FORM_MAP is small and explicit on purpose; do not import an inflector.
"""
from __future__ import annotations

import re

from checker.findings import Action
from checker.rules.loader import RuleRow

FORM_MAP: dict[str, dict[str, str]] = {
    "use":      {"s": "uses", "ed": "used", "ing": "using"},
    "show":     {"s": "shows", "ed": "showed", "ing": "showing"},
    "explain":  {"s": "explains", "ed": "explained", "ing": "explaining"},
    "help":     {"s": "helps", "ed": "helped", "ing": "helping"},
    "ease":     {"s": "eases", "ed": "eased", "ing": "easing"},
    "try":      {"s": "tries", "ed": "tried", "ing": "trying"},
    "begin":    {"s": "begins", "ed": "began", "ing": "beginning"},
    "end":      {"s": "ends", "ed": "ended", "ing": "ending"},
    "affect":   {"s": "affects", "ed": "affected", "ing": "affecting"},
    "develop":  {"s": "develops", "ed": "developed", "ing": "developing", "noun": "development"},
    "change":   {"s": "changes", "ed": "changed", "ing": "changing", "noun": "change"},
    "find out": {"s": "finds out", "ed": "found out", "ing": "finding out"},
}
TENSE_PAIRS = {("can", "could")}
PAST_AUX = {"was", "were", "had"}
PLURAL_MARK = "(s)"


def detect_form(word: str) -> str:
    """'' | 's' | 'ed' | 'ing' | 'noun' from the matched word's ending."""
    w = word.lower()
    if w.endswith("ing"):
        return "ing"
    if w.endswith("ed"):
        return "ed"
    if w.endswith(("tion", "sion", "ment")):
        return "noun"
    if w.endswith("s") and not w.endswith("ss"):
        return "s"
    return ""


def apply_case(template: str, text: str) -> str:
    """Copy the case pattern of `text` (the match) onto `template`."""
    if not template or not text:
        return template
    letters = [c for c in text if c.isalpha()]
    if len(letters) > 1 and all(c.isupper() for c in letters):
        return template.upper()
    if text[0].isupper():
        return template[0].upper() + template[1:]
    return template


def _inflect(base: str, matched: str) -> str:
    if " " in matched.strip() or base not in FORM_MAP:
        return base
    form = detect_form(matched)
    return FORM_MAP[base].get(form, base) if form else base


def _plural(base: str, matched: str) -> str:
    stem = base[: -len(PLURAL_MARK)]
    return stem + "s" if matched.lower().endswith("s") else stem


def _render_one(template: str, row: RuleRow, match: re.Match) -> str:
    matched = match.group(0)
    if template == "lowercase":
        out = matched.lower()
        return out[0].upper() + out[1:] if match.start() == 0 else out
    if template == "first word only":
        return matched.split()[0]
    if "\\" in template:
        return apply_case(match.expand(template), matched)
    if template.endswith(PLURAL_MARK):
        return apply_case(_plural(template, matched), matched)
    return apply_case(_inflect(template, matched), matched)


def render_candidates(row: RuleRow, match: re.Match) -> list[str]:
    if row.action == Action.DELETE:
        return [""]
    if row.candidates:
        cands = row.candidates
        if tuple(c.lower() for c in cands) in TENSE_PAIRS:
            first = match.group(0).split()[0].lower()
            return [apply_case(cands[1] if first in PAST_AUX else cands[0], match.group(0))]
        return [_render_one(c, row, match) for c in cands]
    return [_render_one(row.replacement or "", row, match)]


def render(row: RuleRow, match: re.Match) -> str:
    return render_candidates(row, match)[0]
