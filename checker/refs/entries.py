"""Reference-list entry parsing (ported from check_refs.parse_entry).

parse(entry) -> Entry with doi, first_author, year, suffix, volume, pages, title_guess, raw.
Changes from the script: accept bare "doi:10…" and "https://doi.org/…"; anchor the pages regex
after the volume/issue group so a year range in a title is not read as pages; keep the year
suffix (2020a) for orphan matching.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

DOI_RE = re.compile(r"(?:https?://doi\.org/|\bdoi:\s*)(10\.\S+?)(?=[\s)\]]|$)", re.I)


@dataclass
class Entry:
    raw: str
    index: int
    doi: str | None
    first_author: str
    year: int | None
    suffix: str
    volume: str | None
    pages: tuple[str, str] | None
    title_guess: str

    @property
    def key(self) -> str:
        """Orphan-match key: normalised surname + year + suffix."""
        raise NotImplementedError


def parse(entry: str, index: int) -> Entry:
    raise NotImplementedError


def parse_all(entries: list[str]) -> list[Entry]:
    return [parse(e, i) for i, e in enumerate(entries) if len(e) > 30]
