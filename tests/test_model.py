"""Document model invariants: spans index into Document.text; body_paragraphs excludes headings and
references; sentence_at round-trips."""
from checker.model import Document, Paragraph, Section, SectionKind, Sentence, Span


def test_span_overlap():
    assert Span(0, 5).overlaps(Span(4, 9))
    assert not Span(0, 5).overlaps(Span(5, 9))


def test_body_paragraphs_excludes_headings_and_references():
    intro = Section("Introduction", SectionKind.INTRODUCTION, 1)
    refs = Section("References", SectionKind.REFERENCES, 1)
    h = Paragraph(0, "Introduction", Span(0, 12), intro, is_heading=True)
    p = Paragraph(1, "Rules matter.", Span(14, 27), intro)
    p.sentences.append(Sentence(0, 0, "Rules matter.", Span(14, 27), p))
    r = Paragraph(2, "Smith (2019).", Span(29, 42), refs)
    intro.paragraphs += [h, p]
    refs.paragraphs += [r]
    doc = Document("x", "Introduction\n\nRules matter.\n\nSmith (2019).", [intro, refs])
    assert doc.body_paragraphs() == [p]
    assert doc.sentence_at(15) is p.sentences[0]
    assert doc.slice(p.span) == "Rules matter."
