"""Protected spans (scope 1.1): masked before any rule runs.

mask(doc) fills Sentence.protected with absolute spans for:
- direct quotations: "…" and “…”, and ‘…’ runs of four or more words
- parenthetical citations: a parenthesis holding an author-like token next to a year
  ("(Smith, 2019; Jones et al., 2020a)", "(Lindblom 1959)"), not "(April 2020)" or "(2018–2023)"
- narrative citations: "Jones et al. (2020a)", "Smith and Lee (2019)", "March et al.'s (2000)"
- URLs and DOIs
- hypothesis labels (H1, H2a) themselves, not the sentence
Spans are found on the paragraph text, so a quotation crossing a sentence boundary is still
masked; each sentence receives the parts that overlap it, clipped to its span.
Headings and the reference list are not in the sentence stream, so nothing to mask there.
"""
from __future__ import annotations

import re

from checker.model import Document, Span

YEAR = r"(?:19|20)\d{2}[a-z]?|n\.d\.|in press"
NAME = r"[A-Z][A-Za-z'’\-–]+"
MONTHS = {"January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December", "Spring", "Summer", "Fall", "Autumn", "Winter"}

QUOTE_RE = re.compile(r'"[^"\n]{3,}?"|“[^”\n]{3,}?”')
SINGLE_QUOTE_RE = re.compile(r"‘[^’\n]+?’")
PAREN_RE = re.compile(r"\([^()]*?\b(?:%s)[^()]*\)" % YEAR)
AUTHOR_YEAR_RE = re.compile(r"(%s)(,|\s+et al\.,?|\s+(?:&|and)\s+%s,?)?\s+(?:%s)" % (NAME, NAME, YEAR))
POSSESSIVE = r"(?:['’]s|['’])?"
NARRATIVE_RE = re.compile(r"\b%s(?:\s+(?:&|and)\s+%s|\s+et al\.)?%s\s+\((?:%s)(?:,\s*pp?\.\s*[\d–\-]+)?\)"
                          % (NAME, NAME, POSSESSIVE, YEAR))
URL_RE = re.compile(r"https?://\S+|www\.\S+|\bdoi:\s*10\.\S+", re.I)
H_LABEL_RE = re.compile(r"\bH\d+[a-z]?\b")


def _is_citation_paren(inner: str) -> bool:
    """An author-like name next to a year. "April 2020" is a date; "March et al., 2000" is not."""
    for m in AUTHOR_YEAR_RE.finditer(inner):
        if m.group(1) not in MONTHS or m.group(2):
            return True
    return False


def spans_in(text: str, base: int) -> list[Span]:
    """All protected spans in `text`, shifted by `base` to absolute offsets, merged."""
    raw: list[tuple[int, int]] = []
    for rx in (QUOTE_RE, NARRATIVE_RE, URL_RE, H_LABEL_RE):
        raw += [m.span() for m in rx.finditer(text)]
    raw += [m.span() for m in SINGLE_QUOTE_RE.finditer(text) if len(m.group().split()) >= 4]
    raw += [m.span() for m in PAREN_RE.finditer(text) if _is_citation_paren(m.group())]
    raw.sort()
    merged: list[list[int]] = []
    for s, e in raw:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [Span(base + s, base + e) for s, e in merged]


def mask(doc: Document) -> None:
    for para in doc.body_paragraphs():
        spans = spans_in(para.text, para.span.start)
        for sent in para.sentences:
            sent.protected = [
                Span(max(sp.start, sent.span.start), min(sp.end, sent.span.end))
                for sp in spans if sp.overlaps(sent.span)
            ]
