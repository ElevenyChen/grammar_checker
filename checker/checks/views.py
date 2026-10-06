"""1.6 views: no judgment. Returned as View objects and rendered in all three reports.

skeleton     first and last sentence of every body paragraph, in order, with section and index.
             This is the input for chat window 1.
hypotheses   every sentence containing an H label (H1, H2a …), side by side, for the human to
             check parallel structure. One row per label; a label with several sentences lists all.
numbers      every number token with its surrounding 5 words, its format class (plain, comma,
             percent, decimal, leading-dot, p-value, year) and location. One table.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import View
from checker.model import Document


def skeleton(doc: Document) -> View:
    raise NotImplementedError


def hypotheses(doc: Document) -> View:
    raise NotImplementedError


def numbers(doc: Document) -> View:
    raise NotImplementedError


def run(doc: Document, config: Config) -> list[View]:
    return [skeleton(doc), hypotheses(doc), numbers(doc)]
