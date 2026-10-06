"""Two-way orphan match (1.9).

match(citations, entries) ->
  cited_not_listed: list[Citation]      -> gate   R.CITED_NOT_LISTED
  listed_not_cited: list[Entry]         -> style  R.LISTED_NOT_CITED
  near_misses: list[(Citation, Entry, reason)] -> style R.NEAR_MISS
Near miss = same surname and year ±1, or year equal and surname within edit distance 2.
Exact key match first; then near-miss pass on the leftovers.
"""
from __future__ import annotations

from checker.refs.entries import Entry
from checker.refs.extract import Citation


def match(citations: list[Citation], entries: list[Entry]) -> dict:
    raise NotImplementedError
