"""Regex rows and the Module A Python rows on real text (build step 2)."""
import pytest

from checker.config import Config

pytestmark = pytest.mark.slow


def _report(tmp_path, text, nlp, name="t.md"):
    from checker import pipeline
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return pipeline.run(path, Config(), nlp=nlp)


def _hits(report):
    return {(f.rule_id, f.evidence) for f in report.findings}


def test_fixture_rule_hits(sample_md, nlp):
    from checker import pipeline
    report = pipeline.run(sample_md, Config(), nlp=nlp)
    ids = {f.rule_id for f in report.findings}
    for rid in ("A1.T3", "A1.T5", "A2", "A4.1", "A4.2", "A5.1", "A5.3", "A6", "B1.1", "B1.2", "B1.3",
                "B1.7", "B2.1", "B3.2", "B4.2", "B5.1", "B6", "B7.1", "B9.1", "B9.2", "B9.4", "B9.6"):
        assert rid in ids, rid
    assert "rule B9.8a (elegant variation): not built yet" in {n.item for n in report.not_checked}


def test_protected_and_skip(tmp_path, nlp):
    text = ("# T\n\n## Introduction\n\n"
            'They called it "a very crucial step" in prior work (Smith, 2019).\n\n'
            "This analysis was conducted an analysis of rules.\n\n"
            "We found that rules grow.\n\n## Results\n\nWe found that rules grow quickly.\n")
    hits = _hits(_report(tmp_path, text, nlp))
    assert not any(e in ("very", "crucial") for _, e in hits)          # inside a quotation
    assert ("B9.1", "conducted an analysis") not in hits              # B9.5 skip-list sentence
    b41 = [e for r, e in hits if r == "B4.1"]
    assert b41 == ["We found that"]                                    # exempt in Introduction only


def test_replacement_rendering(tmp_path, nlp):
    text = "# T\n\n## Methods\n\nResearchers were able to utilize methodologies prior to coding.\n"
    found = {f.rule_id: f for f in _report(tmp_path, text, nlp).findings}
    assert found["B1.21"].suggestion == "could"
    assert found["B2.1"].suggestion == "use"
    assert found["B2.5"].suggestion == "methods"
    assert found["B1.7"].suggestion == "before"


def test_a7_flags_both_locations(tmp_path, nlp):
    shared = "communities that changed their rules mostly added new ones over time"
    text = (f"# T\n\n## Introduction\n\nWe note that {shared} in our sample.\n\n"
            f"## Discussion\n\nAs before, {shared} across the platform.\n")
    a7 = [f for f in _report(tmp_path, text, nlp).findings if f.rule_id == "A7"]
    assert len(a7) == 2
    assert {f.location.section for f in a7} == {"Introduction", "Discussion"}
    assert a7[0].extra["pair"] == a7[1].extra["pair"]
    assert shared in a7[0].evidence


def test_a6_only_terms_new_in_results(tmp_path, nlp):
    text = ("# T\n\n## Methods\n\nWe fit a hurdle model to the Rules Widget data.\n\n"
            "## Results\n\nThe hurdle model and the Wayback Machine data agree. "
            "A binomial test confirms it.\n")
    terms = {f.extra["term"] for f in _report(tmp_path, text, nlp).findings if f.rule_id == "A6"}
    assert "Wayback Machine" in terms and "binomial test" in terms
    assert "hurdle model" not in terms and "Rules Widget" not in terms


def test_pos_qualifiers(tmp_path, nlp):
    text = ("# T\n\n## Results\n\n"
            "Removing established rules is costly. The test established that rules grow.\n\n"
            "Communities established before 2017 differ. Patterns driven by the interplay of size persist. "
            "Growth–driven pressures matter.\n\n"
            "They are likely to apply rules early. Rules grew substantially.\n")
    hits = [(f.rule_id, f.evidence, f.sentence) for f in _report(tmp_path, text, nlp).findings]
    t3 = [s for r, e, s in hits if r == "A1.T3"]
    assert t3 == ["The test established that rules grow."]          # adjective and acl dropped
    t4 = [s for r, e, s in hits if r == "A1.T4"]
    assert t4 == ["Patterns driven by the interplay of size persist."]  # agentive acl kept
    ly = {e for r, e, s in hits if r == "B3.3"}
    assert "substantially" in ly and "likely" not in ly and "apply" not in ly


def test_significant_whole_sentence(tmp_path, nlp):
    text = ("# T\n\n## Results\n\nThe chi–square test shows the groups differ significantly. "
            "Rules had a significant effect on growth.\n")
    a42 = [(f.evidence, f.sentence) for f in _report(tmp_path, text, nlp).findings if f.rule_id == "A4.2"]
    assert a42 == [("significant", "Rules had a significant effect on growth.")]


def test_a6_known_and_defined_terms(tmp_path, nlp):
    text = ("# T\n\n## Methods\n\nWe count rules.\n\n## Results\n\n"
            "The 95% CI excludes zero during COVID. OR = Odds Ratio. A Wilcoxon test agrees.\n")
    terms = {f.extra["term"] for f in _report(tmp_path, text, nlp).findings if f.rule_id == "A6"}
    assert terms & {"Wilcoxon", "wilcoxon test"} and len(terms & {"Wilcoxon", "wilcoxon test"}) == 1
    assert not terms & {"CI", "COVID", "Odds Ratio"}


def test_noun_string(tmp_path, nlp):
    text = "# T\n\n## Methods\n\nWe ran a community rule change frequency analysis. We ran a regression model.\n"
    ns = [f.evidence for f in _report(tmp_path, text, nlp).findings if f.rule_id == "B.NOUNS"]
    assert ns == ["community rule change frequency analysis"]
