"""Appendix step-3 rows that need the parse rather than a regex.

- of-density: count "of" per sentence; flag when > 1 per config.thresholds.of_density_per_words.
- while (non-temporal): token "while" whose clause has no time expression (no DATE/TIME entity,
  no "when/during/as" nearby) -> suggest although.
- since (non-temporal): same shape -> suggest because.
- B.NOUNS noun string: three or more nouns in a row before model / system / analysis /
  approach ("community rule change analysis"). Built.
- B9.4b resulted from / stemmed from / arose from with a nominalized head on both sides
  (subject head and the object of "from" end in tion/sion/ment/ance/ence/ysis/ity).
Passive with agent (B.PASSIVE) and impact as a verb (B2.11, `(verb)` qualifier) are regex rows
and run in regex_rules.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.model import Span
from checker.rules import emit
from checker.rules.loader import RuleRow
from checker.rules.registry import rule

NOUN_STRING_HEADS = {"model", "system", "analysis", "approach"}
NOUN_STRING_MIN = 3     # nouns before the head (the row: "≥3 nouns in a row")


@rule("B.NOUNS")
def noun_string(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    out: list[Finding] = []
    for s in doc.sentences():
        toks = list(s.parsed)
        base = s.paragraph.span.start
        occ = 0
        for i, tok in enumerate(toks):
            if tok.lemma_.lower() not in NOUN_STRING_HEADS or tok.pos_ != "NOUN":
                continue
            j = i
            while j > 0 and toks[j - 1].pos_ in ("NOUN", "PROPN"):
                j -= 1
            if i - j < NOUN_STRING_MIN:
                continue
            span = Span(base + toks[j].idx, base + tok.idx + len(tok.text))
            if any(p.start <= span.start and span.end <= p.end for p in s.protected):
                continue
            out.append(emit.finding(row, s, span, occ))
            occ += 1
    return out


@rule("B.OF", stub=True)
def of_density(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


@rule("B.WHILE", stub=True)
def while_non_temporal(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError


@rule("B.SINCE", stub=True)
def since_non_temporal(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError



@rule("B9.4b", stub=True)
def resulted_from_nominalized(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError
