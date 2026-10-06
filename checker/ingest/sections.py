"""Section classification (scope 1.0): heading style first, name match as fallback.

classify(doc, config) rebuilds doc.sections from the provisional single section:
- A heading opens a section. Its kind comes from config.sections (normalised prefix match on the
  heading text). An unmatched heading inherits the kind of its nearest shallower heading, so a
  subsection of Results is still Results. A matched heading at any depth starts its own kind
  (a "Limitations" subsection under Discussion is LIMITATIONS).
- Drafts with no heading styles at all: a short paragraph (<= 6 words) whose text matches a
  section name becomes a level-1 heading.
- Front matter before the first heading: the title paragraph(s) form a TITLE section with any
  short lines that follow (authors, affiliations). A front paragraph starting "Abstract" opens an
  ABSTRACT section. A long front paragraph opens an OTHER section, so it is still checked.
- References: body paragraphs are kept in the REFERENCES section (so findings have a location)
  and also collected into doc.reference_entries, joining continuation paragraphs (a paragraph
  without a year in parentheses near its start belongs to the previous entry).
Mutates doc in place.
"""
from __future__ import annotations

import re

from checker.config import Config
from checker.model import Document, Paragraph, Section, SectionKind

NUMBERING_RE = re.compile(r"^(?:\d+(?:\.\d+)*\.?|[ivxlc]+\.|[a-z]\.|[a-z]\))\s+", re.I)
ENTRY_START_RE = re.compile(r"\((?:19|20)\d{2}[a-z]?[,)]|\(n\.d\.\)|\(in press\)", re.I)
FALLBACK_MAX_WORDS = 6
FRONT_SHORT_WORDS = 30


def normalise_heading(text: str) -> str:
    t = text.strip().lower()
    t = NUMBERING_RE.sub("", t)
    return t.rstrip(" .:;")


def kind_for_heading(text: str, config: Config) -> SectionKind | None:
    """Kind whose configured name is a prefix of the heading (whole-word); None if none match."""
    t = normalise_heading(text)
    best: tuple[int, SectionKind] | None = None
    for kind_name, names in config.sections.items():
        try:
            kind = SectionKind(kind_name)
        except ValueError:
            continue
        for name in names:
            if t == name or (t.startswith(name) and not t[len(name)].isalnum()):
                if best is None or len(name) > best[0]:
                    best = (len(name), kind)
    return best[1] if best else None


def classify(doc: Document, config: Config) -> None:
    paragraphs = [p for s in doc.sections for p in s.paragraphs]
    if not any(p.is_heading and (p.heading_level or 0) > 0 for p in paragraphs):
        _promote_fallback_headings(paragraphs, config)

    sections: list[Section] = []
    stack: list[tuple[int, SectionKind]] = []
    current: Section | None = None
    seen_heading = False

    def open_section(name: str, kind: SectionKind, level: int, heading: Paragraph | None) -> Section:
        sec = Section(name=name, kind=kind, level=level, heading=heading)
        sections.append(sec)
        return sec

    for p in paragraphs:
        if p.is_heading and p.heading_level == 0:
            # document title
            if current is None or current.kind != SectionKind.TITLE:
                current = open_section(p.text, SectionKind.TITLE, 0, p)
            _add(current, p)
            continue

        if p.is_heading:
            seen_heading = True
            level = p.heading_level or 1
            while stack and stack[-1][0] >= level:
                stack.pop()
            parent = stack[-1][1] if stack else None
            kind = kind_for_heading(p.text, config) or parent or SectionKind.OTHER
            stack.append((level, kind))
            current = open_section(p.text, kind, level, p)
            _add(current, p)
            continue

        if not seen_heading:
            current = _front_matter(p, current, open_section)
        elif current is None:
            current = open_section("", SectionKind.OTHER, 0, None)
        _add(current, p)

    doc.sections = sections
    doc.reference_entries = _reference_entries(doc)


def _add(section: Section, p: Paragraph) -> None:
    p.section = section
    section.paragraphs.append(p)


def _front_matter(p: Paragraph, current: Section | None, open_section) -> Section:
    if p.text.lower().startswith("abstract"):
        return open_section("Abstract", SectionKind.ABSTRACT, 0, None)
    if current is not None and current.kind == SectionKind.ABSTRACT:
        return current
    if len(p.text.split()) < FRONT_SHORT_WORDS and (current is None or current.kind == SectionKind.TITLE):
        return current or open_section("(front matter)", SectionKind.TITLE, 0, None)
    if current is not None and current.kind == SectionKind.OTHER:
        return current
    return open_section("(front matter)", SectionKind.OTHER, 0, None)


def _promote_fallback_headings(paragraphs: list[Paragraph], config: Config) -> None:
    for p in paragraphs:
        if p.is_heading or len(p.text.split()) > FALLBACK_MAX_WORDS:
            continue
        if kind_for_heading(p.text, config) is not None:
            p.is_heading = True
            p.heading_level = 1


def _reference_entries(doc: Document) -> list[str]:
    entries: list[str] = []
    for sec in doc.section_of_kind(SectionKind.REFERENCES):
        for p in sec.body:
            if entries and not ENTRY_START_RE.search(p.text[:250]):
                entries[-1] = entries[-1] + " " + p.text
            else:
                entries.append(p.text)
    return entries
