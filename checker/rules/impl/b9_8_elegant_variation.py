"""B9.8 elegant variation: >= 3 of {change, modification, revision, amendment}, or >= 2 of
{remove, delete, repeal} / {add, introduce, adopt} / {community, subreddit, group} in one section.

Lemma match on tokens. One Finding per (section, concept set) at the first occurrence of the
second lexeme, extra["lexemes"] = {lemma: count}. Severity gate. The concept sets are
manuscript-bound; read them from the row's pattern text so other papers edit the markdown.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document
from checker.rules.loader import RuleRow
from checker.rules.registry import rule


def parse_sets(pattern: str) -> list[tuple[int, set[str]]]:
    """'≥3 of {a, b, c}' / '≥2 of {x, y} / {p, q}' -> [(3, {a,b,c})], [(2,{x,y}),(2,{p,q})]."""
    raise NotImplementedError


@rule("B9.8")
def elegant_variation(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    raise NotImplementedError
