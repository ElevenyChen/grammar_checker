"""docx reader, display filtering, section kinds (build step 1). Builds a synthetic docx so no
manuscript is committed."""
import pytest

from checker.config import Config
from checker.model import SectionKind

docx = pytest.importorskip("docx")

LONG = ("Policy is a major avenue for communicating structure in organizations and communities, "
        "including those that leverage new media, and this sentence is long enough to be body text.")


@pytest.fixture
def draft(tmp_path):
    d = docx.Document()
    d.add_paragraph("A Title That Makes a Claim", style="Title")
    d.add_paragraph("Jane Doe, University", style="Normal")
    d.add_heading("Abstract", 1)
    d.add_paragraph("Communities add rules. They rarely delete them.")
    d.add_paragraph("Keywords governance, rules, Reddit")
    d.add_heading("", 1)                                     # empty spacer heading
    d.add_heading("1. Introduction", 1)
    d.add_paragraph("Rules matter (Smith, 2019). Figure 2 shows that rules grow.")
    d.add_heading("Related Work", 1)
    d.add_heading(LONG, 2)                                   # misstyled body paragraph
    d.add_heading("Theories of Rule Change", 2)
    d.add_paragraph("Layering is gradual. H1: Additions are more common than deletions.")
    d.add_heading("Methods", 1)
    d.add_heading("Data", 2)
    d.add_paragraph("We sampled 130,851 communities.")
    d.add_paragraph("Table 1 Descriptive Statistics")
    d.add_paragraph("Part 1: Counts")
    d.add_table(rows=2, cols=2)
    d.add_paragraph("Model fit: AIC = 43,272")
    d.add_paragraph("Note. N = 130,851 communities.")
    d.add_paragraph("*p < .05. **p < .01.")
    d.add_heading("Results", 1)
    d.add_heading("Communities Mostly Add Rules.", 2)
    d.add_paragraph("Most changes are additions (Figure 1).")
    d.add_heading("Discussion", 1)
    d.add_heading("Limitations", 2)
    d.add_paragraph("The sample is selective.")
    d.add_paragraph("Code & Data:")
    d.add_paragraph("https://example.org/repo")
    d.add_heading("Appendix A: Model", 1)
    d.add_paragraph("The hurdle model fits better.")
    d.add_heading("References", 1)
    d.add_paragraph("Smith, J. (2019). A title. Journal, 1(1), 1–2.")
    d.add_paragraph("Continuation line of the entry above.")
    d.add_paragraph("Jones, A., & Lee, B. (2020a). Another. Journal, 2(1), 3–4. https://doi.org/10.1/x")
    path = tmp_path / "draft.docx"
    d.save(path)
    return path


def _doc(path):
    from checker.ingest import docx_reader, sections
    doc = docx_reader.read(path)
    sections.classify(doc, Config())
    return doc


def test_section_kinds(draft):
    doc = _doc(draft)
    kinds = {s.name: s.kind for s in doc.sections}
    assert doc.sections[0].kind == SectionKind.TITLE
    assert kinds["Abstract"] == SectionKind.ABSTRACT
    assert kinds["1. Introduction"] == SectionKind.INTRODUCTION
    assert kinds["Theories of Rule Change"] == SectionKind.LITERATURE      # inherits from Related Work
    assert kinds["Data"] == SectionKind.METHODS
    assert kinds["Communities Mostly Add Rules."] == SectionKind.RESULTS
    assert kinds["Limitations"] == SectionKind.LIMITATIONS                 # named subsection
    assert kinds["Appendix A: Model"] == SectionKind.APPENDIX
    assert kinds["References"] == SectionKind.REFERENCES


def test_display_material_skipped_body_kept(draft):
    doc = _doc(draft)
    body = [p.text for p in doc.body_paragraphs()]
    assert "Rules matter (Smith, 2019). Figure 2 shows that rules grow." in body   # B5 target stays
    for gone in ("Table 1 Descriptive Statistics", "Part 1: Counts", "Model fit: AIC = 43,272",
                 "Note. N = 130,851 communities.", "*p < .05. **p < .01.", "Code & Data:",
                 "https://example.org/repo", "Keywords governance, rules, Reddit"):
        assert gone not in body, gone
    kinds = sorted(s.kind for s in doc.skipped)
    assert kinds.count("table") == 1 and kinds.count("caption") == 1 and kinds.count("display") == 2
    assert "Jane Doe, University" not in body                                       # front matter


def test_misstyled_heading_becomes_body(draft):
    doc = _doc(draft)
    assert LONG in [p.text for p in doc.body_paragraphs()]
    assert doc.meta["warnings"]


def test_reference_entries_joined(draft):
    doc = _doc(draft)
    assert len(doc.reference_entries) == 2
    assert doc.reference_entries[0].endswith("Continuation line of the entry above.")


def test_spans_round_trip(draft):
    doc = _doc(draft)
    assert all(doc.slice(p.span) == p.text for p in doc.paragraphs)


@pytest.mark.slow
def test_segmentation_guards(draft, nlp):
    from checker import ingest
    doc = ingest.read(draft, Config(), nlp=nlp)
    texts = [s.text for s in doc.sentences()]
    assert "Layering is gradual." in texts
    assert "H1: Additions are more common than deletions." in texts      # no split after "H1:"
