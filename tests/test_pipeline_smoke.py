"""End-to-end on the fixture. Three files, report ends with Not checked by this tool, unbuilt stages listed
instead of reported as clean, Module B withheld while Module A is open.
EXPECTED_RULE_HITS documents what the fixture is for in later steps."""
import json

import pytest

from checker.config import Config

EXPECTED_RULE_HITS = {
    # fixture text                                       expected rule family
    "utilize": "B2",            "in order to": "B1",          "demonstrate": "A1 T3",
    "evolve": "B7",             "integrates": "A1 T5",        "It is important to note": "B3",
    "prior to": "B1",           "a number of": "B1",          "The majority of": "B1",
    "no systematic difference": "A2", "First,": "B6 / P.OPEN", "conducted an analysis": "B9.1",
    "There was a reduction": "B9.2", "was due to": "B9.4",     "as noted above": "B9.6",
    "passive run in Methods": "S.PASS exempt",                "bootstrapping analysis": "A6",
    "crucial": "A4",            "Most … primarily": "A5",     "significant": "A4 non-stat",
    "revision / amendment / modification": "B9.8",            "In conclusion": "B4",
    "seem to suggest": "A5",    "Taylor 2018": "R.LISTED_NOT_CITED",
}


@pytest.mark.slow
def test_cli_run_writes_three_files(sample_md, nlp, tmp_path):
    from checker import cli
    from checker.ingest import segment
    segment._NLP[Config().models.spacy] = nlp
    assert cli.main(["run", str(sample_md), "--out", str(tmp_path)]) == 0
    md = (tmp_path / "sample.report.md").read_text()
    html = (tmp_path / "sample.report.html").read_text()
    data = json.loads((tmp_path / "sample.report.json").read_text())
    headings = [l for l in md.splitlines() if l.startswith("## ")]
    assert headings[-1] == "## Not checked by this tool"
    assert "Module A open" in md                       # gate findings exist, none decided
    assert "Withheld until every Module A gate finding has a decision" in md
    assert "not built yet" in md
    assert '"findings"' in html and "/*__DATA__*/null" not in html
    assert data["document"]["sentences"] and data["report"]["stats"]["sentences"] == 21


@pytest.mark.slow
@pytest.mark.xfail(reason="views are build step 3", strict=False)
def test_views_present(sample_md, nlp):
    from checker import pipeline
    report = pipeline.run(sample_md, Config(), nlp=nlp)
    assert {v.name for v in report.views} == {"skeleton", "hypotheses", "numbers"}
