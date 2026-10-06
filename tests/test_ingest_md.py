"""Markdown reader + section classification on the fixture (build step 1)."""
import pytest

from checker.config import Config
from checker.model import SectionKind


def test_sections_and_skips(sample_md):
    from checker.ingest import md_reader, sections
    doc = md_reader.read(sample_md)
    sections.classify(doc, Config())
    kinds = [s.kind for s in doc.sections]
    assert kinds[0] == SectionKind.TITLE
    assert SectionKind.METHODS in kinds and SectionKind.RESULTS in kinds and SectionKind.REFERENCES in kinds
    assert len(doc.reference_entries) == 3
    assert any(s.kind == "table" for s in doc.skipped)
    assert all(not p.is_heading for p in doc.body_paragraphs())
    assert all(doc.slice(p.span) == p.text for p in doc.paragraphs)


def test_inline_markup_stripped():
    from checker.ingest.md_reader import strip_inline
    assert strip_inline("A **bold** and *it* and `code` and [link](http://x)") == "A bold and it and code and link"


@pytest.mark.slow
def test_full_ingest(sample_md, nlp):
    from checker import ingest
    doc = ingest.read(sample_md, Config(), nlp=nlp)
    sents = list(doc.sentences())
    assert len(sents) == 21
    assert all(doc.slice(s.span) == s.text for s in sents)
    cited = [s for s in sents if "(Smith, 2019" in s.text][0]
    assert cited.protected, "parenthetical citation must be masked"
    narrative = [s for s in sents if s.text.startswith("Jones et al. (2020a)")][0]
    assert doc.slice(narrative.protected[0]) == "Jones et al. (2020a)"
