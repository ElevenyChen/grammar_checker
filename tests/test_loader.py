"""Rule table loader (build step 2): the appendix in llm_polishing.md is the source of truth."""
import pytest

from checker.findings import Action, Grade
from checker.rules import loader, registry


@pytest.fixture(scope="module")
def table(polishing_md_path):
    return loader.load(polishing_md_path)


@pytest.fixture(scope="module")
def polishing_md_path():
    from pathlib import Path
    return Path(__file__).resolve().parents[1] / "llm_polishing.md"


def test_ids_unique_and_present(table):
    ids = [r.id for r in table.rows + table.skip_rows]
    assert len(ids) == len(set(ids)) and all(ids)


def test_regex_rows_compile(table):
    assert table.regex_rows
    for r in table.regex_rows:
        assert r.compiled is not None, r.id


def test_python_rows_have_implementations(table):
    registry.check_coverage(table)


def test_qualifiers_and_flags(table):
    assert table.by_id("B7.2").case_sensitive
    assert table.by_id("B6").paragraph_start and table.by_id("B6").is_regex
    assert table.by_id("B7.1").candidates == ["develop", "change"]
    assert table.by_id("B9.3").grade == Grade.SENTENCE
    assert table.by_id("B3.3").can_delete
    assert table.by_id("B3.1").action == Action.DELETE and table.by_id("B3.1").replacement == ""
    assert [r.id for r in table.skip_rows] == ["B9.5"]
    assert not table.by_id("A6").is_regex and not table.by_id("B.NOUNS").is_regex
    assert table.by_id("B2.11").is_regex and table.by_id("B2.11").pos == "verb"
    assert table.by_id("A1.T3").pos == "verb" and table.by_id("B3.3").pos == "adverb"
    assert "hit" in table.by_id("A4.2").compiled.groupindex


def test_known_terms(polishing_md_path):
    terms = loader.known_terms(polishing_md_path)
    assert {"ci", "covid"} <= terms


def test_old_format_rejected():
    with pytest.raises(loader.MissingRuleId):
        loader.parse_row(r"1 | gate  | flag    | \bprove\b    |")


def test_non_regex_markers():
    assert not loader.looks_like_regex("≥3 of {change, modification} in one section")
    assert loader.looks_like_regex(r"\bin order to\b")
