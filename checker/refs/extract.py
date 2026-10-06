"""In-text citation extraction from body sentences (1.9 orphan match).

Forms to cover: (Author, 2020); (Author & Author, 2020); (Author et al., 2020a); Author (2020);
Author and Author (2020); Author et al. (2020); semicolon lists inside one parenthesis;
page locators (p. 12) after the year; "n.d." and "in press".
Returns Citation(surname, year, suffix, location, raw). Keys normalised like Entry.key.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from checker.findings import Location
from checker.model import Document

YEAR = r"(?:19|20)\d{2}[a-z]?|n\.d\.|in press"
PAREN_RE = re.compile(r"\(([^()]*?\b(?:%s)\b[^()]*)\)" % YEAR)
NARRATIVE_RE = re.compile(r"\b([A-Z][\w'’-]+(?:\s(?:and|&)\s[A-Z][\w'’-]+|\set al\.)?)\s\((%s)\)" % YEAR)


@dataclass
class Citation:
    surname: str
    year: str
    suffix: str
    raw: str
    location: Location

    @property
    def key(self) -> str:
        raise NotImplementedError


def extract(doc: Document) -> list[Citation]:
    raise NotImplementedError
