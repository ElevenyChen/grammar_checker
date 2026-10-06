"""Shared ingest step: reader blocks -> Document (scope 1.0).

Readers (docx, markdown) only turn their source into a flat list of RawBlock. Everything that
decides what is body text lives here, so both readers behave the same:

- Empty paragraphs are dropped (they never enter Document.text).
- Heading-styled paragraphs longer than MAX_HEADING_WORDS are treated as body text and a warning
  is recorded (a misstyled paragraph is still text the author wrote).
- Tables, images, code and other non-paragraph blocks are skipped and recorded.
- Captions ("Figure 3. …", "Table 2 Title …"), notes ("Note. …"), specific notes ("ᵃ …") and
  probability notes ("*p < .05 …") are skipped and recorded.
- A caption, table or image opens a display block. Inside it, short label-like paragraphs
  (fewer than DISPLAY_MAX_WORDS words and no terminal punctuation, e.g. "Part 1: Logistic
  Regression", "Model fit: AIC = …") are display material. The block closes at the first heading
  or the first body-like paragraph.
- Outside display blocks, a very short paragraph with no terminal punctuation ("Code & Data:"),
  a keywords line, or a paragraph that is only a URL is a label and skipped.
Section assignment happens later in sections.classify; here every paragraph goes into one
provisional section.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from checker.model import Document, Paragraph, Section, SectionKind, SkippedItem, Span

MAX_HEADING_WORDS = 25
DISPLAY_MAX_WORDS = 25
LABEL_MAX_WORDS = 5
SEP = "\n\n"

# "Figure 3." "Figure B2." "Table 2 Hurdle Model" "Table 1:" "Figure 4" alone.
# Not "Figure 3 shows that …" (lower-case word after the number is body text, a B5 target).
CAPTION_RE = re.compile(r"^(?:Figure|Fig\.|Table)\s+[A-Z]?\d+[a-z]?(?:\s*[.:]|\s*$|\s+[A-Z(])")
NOTE_RE = re.compile(r"^(?:Note[s]?\.|Source[s]?:)\s")
SPECIFIC_NOTE_RE = re.compile(r"^[ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ†‡§]")
PROB_NOTE_RE = re.compile(r"^\*+\s*p\s*[<=≤]")
URL_ONLY_RE = re.compile(r"^(?:https?://|www\.)\S+$")
KEYWORDS_RE = re.compile(r"^key\s?words\b", re.I)
TERMINAL_RE = re.compile(r"[.?!][\"'”’)]*$")


@dataclass
class RawBlock:
    kind: str                    # "para" | "table" | "image" | "code" | "other"
    text: str = ""
    style: str | None = None
    heading_level: int | None = None   # set by the reader when the style marks a heading
    is_title: bool = False             # Word "Title" style / markdown document title
    has_image: bool = False            # paragraph that also carries a drawing


def _words(text: str) -> int:
    return len(text.split())


def _is_label(text: str, max_words: int) -> bool:
    if URL_ONLY_RE.match(text) or KEYWORDS_RE.match(text):
        return True
    return _words(text) < max_words and not TERMINAL_RE.search(text)


def build(source: str, blocks: list[RawBlock]) -> Document:
    doc = Document(source=source, text="")
    provisional = Section(name="", kind=SectionKind.OTHER, level=0)
    pieces: list[str] = []
    offset = 0
    last_heading = "(start)"
    in_display = False
    warnings: list[str] = []

    def where() -> str:
        return f"{last_heading} · after ¶{len(provisional.paragraphs) - 1}"

    def skip(kind: str, note: str = "") -> None:
        doc.skipped.append(SkippedItem(kind=kind, where=where(), note=note[:80]))

    for b in blocks:
        if b.kind != "para":
            skip(b.kind)
            in_display = b.kind in ("table", "image")
            continue
        text = b.text.strip()
        if b.has_image:
            skip("image")
            in_display = True
        if not text:
            continue

        heading = b.heading_level is not None or b.is_title
        if heading and _words(text) > MAX_HEADING_WORDS:
            warnings.append(f"heading-styled paragraph treated as body text: {text[:60]!r}")
            heading = False

        if heading:
            in_display = False
        else:
            if CAPTION_RE.match(text):
                skip("caption", text); in_display = True; continue
            if NOTE_RE.match(text):
                skip("note", text); in_display = True; continue
            if SPECIFIC_NOTE_RE.match(text) or PROB_NOTE_RE.match(text):
                skip("note", text); continue
            if in_display and _is_label(text, DISPLAY_MAX_WORDS):
                skip("display", text); continue
            in_display = False
            if _is_label(text, LABEL_MAX_WORDS):
                skip("label", text); continue

        if pieces:
            offset += len(SEP)
        span = Span(offset, offset + len(text))
        level = (0 if b.is_title else b.heading_level) if heading else None
        para = Paragraph(
            index=len(provisional.paragraphs),
            text=text,
            span=span,
            section=provisional,
            style="Title" if b.is_title else b.style,
            is_heading=heading,
            heading_level=level,
        )
        if heading:
            last_heading = text[:40]
        provisional.paragraphs.append(para)
        pieces.append(text)
        offset = span.end

    doc.text = SEP.join(pieces)
    doc.sections = [provisional]
    doc.meta["warnings"] = warnings
    return doc
