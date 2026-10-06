"""Document model (scope 1.0). Every check reads this and nothing else.

document -> section (name, kind) -> paragraph -> sentence
Each node carries its character span in `Document.text`. Section kind is first-class:
1.3 passive run, 1.4 orphan terms, B9.8 and the B4 Intro/Conclusion exemption depend on it.
Tables, images, captions are not in the model; they are listed in `Document.skipped`
so the report can say what was not checked. The reference section is kept as raw
entries for 1.9 and excluded from `body_paragraphs()`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator


class SectionKind(str, Enum):
    TITLE = "title"
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    LITERATURE = "literature"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    LIMITATIONS = "limitations"
    CONCLUSION = "conclusion"
    APPENDIX = "appendix"
    REFERENCES = "references"
    OTHER = "other"

    @property
    def is_body(self) -> bool:
        return self not in (SectionKind.TITLE, SectionKind.REFERENCES)

    @property
    def after_results(self) -> bool:
        """For A6 orphan terms: Results and everything that follows."""
        return self in (SectionKind.RESULTS, SectionKind.DISCUSSION,
                        SectionKind.LIMITATIONS, SectionKind.CONCLUSION, SectionKind.APPENDIX)


@dataclass(frozen=True)
class Span:
    """Half-open character range in Document.text."""
    start: int
    end: int

    def __len__(self) -> int:
        return self.end - self.start

    def overlaps(self, other: "Span") -> bool:
        return self.start < other.end and other.start < self.end

    def shift(self, delta: int) -> "Span":
        return Span(self.start + delta, self.end + delta)


@dataclass
class Sentence:
    index: int                 # within its paragraph
    doc_index: int             # global sentence index
    text: str
    span: Span                 # absolute, in Document.text
    paragraph: "Paragraph" = field(repr=False)
    parsed: Any = None         # spaCy Span, attached by ingest.segment
    protected: list[Span] = field(default_factory=list)  # absolute spans masked by ingest.protect

    @property
    def section(self) -> "Section":
        return self.paragraph.section

    @property
    def tokens(self):
        return list(self.parsed) if self.parsed is not None else []

    def is_protected(self, span: Span) -> bool:
        return any(span.overlaps(p) for p in self.protected)

    def content_words(self, last: int | None = None) -> list[Any]:
        """Non-stop, non-punct tokens; last N if given. Used by 1.3, 1.4, 1.5, B9.9."""
        words = [t for t in self.tokens if not t.is_stop and not t.is_punct and not t.is_space]
        return words[-last:] if last else words


@dataclass
class Paragraph:
    index: int                 # global paragraph index (headings included)
    text: str
    span: Span
    section: "Section" = field(repr=False)
    style: str | None = None   # docx paragraph style name, if any
    is_heading: bool = False
    heading_level: int | None = None  # 0 = document title, 1.. = heading depth; None for body
    sentences: list[Sentence] = field(default_factory=list)

    @property
    def first(self) -> Sentence | None:
        return self.sentences[0] if self.sentences else None

    @property
    def last(self) -> Sentence | None:
        return self.sentences[-1] if self.sentences else None


@dataclass
class Section:
    name: str                  # heading text as written
    kind: SectionKind
    level: int                 # heading level; 0 for implicit front matter
    paragraphs: list[Paragraph] = field(default_factory=list)
    heading: Paragraph | None = None

    @property
    def body(self) -> list[Paragraph]:
        return [p for p in self.paragraphs if not p.is_heading]

    def sentences(self) -> Iterator[Sentence]:
        for p in self.body:
            yield from p.sentences


@dataclass
class SkippedItem:
    """Something present in the source the checker did not read (scope 1.0)."""
    kind: str                  # "table" | "image" | "caption" | "note" | "display" | "label" | "code" | "other"
    where: str                 # nearest heading or paragraph index
    note: str = ""


@dataclass
class Document:
    source: str
    text: str                                 # paragraphs joined by "\n\n"; all spans index into this
    sections: list[Section] = field(default_factory=list)
    reference_entries: list[str] = field(default_factory=list)  # raw entries for refs/
    skipped: list[SkippedItem] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)          # title, word count, reader used

    # ---- navigation
    @property
    def paragraphs(self) -> list[Paragraph]:
        return [p for s in self.sections for p in s.paragraphs]

    def body_paragraphs(self) -> list[Paragraph]:
        """Checked paragraphs: no headings, no references, no title block."""
        return [p for s in self.sections if s.kind.is_body for p in s.body]

    def sentences(self) -> Iterator[Sentence]:
        for p in self.body_paragraphs():
            yield from p.sentences

    def section_of_kind(self, kind: SectionKind) -> list[Section]:
        return [s for s in self.sections if s.kind == kind]

    def paragraph_at(self, offset: int) -> Paragraph | None:
        for p in self.paragraphs:
            if p.span.start <= offset < p.span.end:
                return p
        return None

    def sentence_at(self, offset: int) -> Sentence | None:
        p = self.paragraph_at(offset)
        if p is None:
            return None
        for s in p.sentences:
            if s.span.start <= offset < s.span.end:
                return s
        return None

    def slice(self, span: Span) -> str:
        return self.text[span.start:span.end]
