"""Crossref access with a local cache (1.9). Deterministic lookup, not model classification.

- works(doi): GET https://api.crossref.org/works/<doi>; cache at config.paths.cache_dir/crossref/<sha1(doi)>.json
- query(title, author): GET /works?query.bibliographic=…&rows=3; cached by sha1 of the query.
- 1 s sleep between uncached requests; User-Agent carries config.refs.crossref_contact.
- Any error is returned as {"_error": "…"} and cached too, with a short TTL (1 day) so a transient
  failure is retried later.
"""
from __future__ import annotations

from pathlib import Path

from checker.config import Config

API = "https://api.crossref.org/works"


class Cache:
    def __init__(self, root: Path):
        self.root = root

    def get(self, key: str) -> dict | None:
        raise NotImplementedError

    def put(self, key: str, value: dict) -> None:
        raise NotImplementedError


def works(doi: str, config: Config, cache: Cache) -> dict:
    raise NotImplementedError


def query(title: str, author: str, config: Config, cache: Cache) -> list[dict]:
    raise NotImplementedError
