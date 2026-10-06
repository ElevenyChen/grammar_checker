"""Ingest: source file -> Document (scope 1.0).

read(path) picks the reader by extension, classifies sections, segments sentences with spaCy,
and masks protected spans. Everything downstream consumes the result.
"""
from __future__ import annotations

from pathlib import Path

from checker.config import Config
from checker.model import Document


def read(path: Path, config: Config, nlp=None) -> Document:
    """Full ingest pipeline. `nlp` lets callers share one loaded spaCy model."""
    from checker.ingest import docx_reader, md_reader, protect, sections, segment

    suffix = Path(path).suffix.lower()
    if suffix == ".docx":
        doc = docx_reader.read(Path(path))
    elif suffix in (".md", ".markdown", ".txt"):
        doc = md_reader.read(Path(path))
    else:
        raise ValueError(f"unsupported input: {suffix}")
    sections.classify(doc, config)
    segment.segment(doc, config, nlp=nlp)
    protect.mask(doc)
    return doc
