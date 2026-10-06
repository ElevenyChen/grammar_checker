"""docx -> Document. Body text only (scope 1.0).

The reader only turns the body into RawBlocks; ingest.blocks decides what is body text.
- Walk document.body children in order: w:p -> paragraph block, w:tbl -> table block,
  w:sdt -> descend into w:sdtContent (content controls; Word's own bibliography lives there),
  w:sectPr -> ignored, anything else -> "other".
- Paragraph text is extracted here, not with python-docx's Paragraph.text, so that text-box
  content (w:txbxContent), deleted revisions and mc:Fallback duplicates stay out, and tabs /
  breaks / non-breaking hyphens map to visible characters. Inserted revisions count as text.
- Heading level: style "Heading N" (or a style based on one) -> N; style "Title" -> title.
- A paragraph holding w:drawing / w:pict / w:object is flagged has_image; its text (usually none)
  is still offered as a paragraph.
- Runs are not touched here; `apply` has its own run logic.
"""
from __future__ import annotations

import re
from pathlib import Path

from checker.ingest.blocks import RawBlock, build
from checker.model import Document

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
SKIP_SUBTREES = {W + "txbxContent", W + "del", W + "moveFrom", MC + "Fallback",
                 W + "instrText", W + "delText", W + "footnoteReference", W + "endnoteReference"}
IMAGE_TAGS = (W + "drawing", W + "pict", W + "object")
HEADING_RE = re.compile(r"^heading\s*(\d)$", re.I)


def read(path: Path) -> Document:
    import docx  # python-docx

    document = docx.Document(str(path))
    styles = _style_map(document)
    blocks: list[RawBlock] = []
    _walk(document.element.body, styles, blocks)
    doc = build(str(path), blocks)
    doc.meta["reader"] = "docx"
    return doc


def _walk(container, styles: dict[str, tuple[str, int | None, bool]], out: list[RawBlock]) -> None:
    for el in container.iterchildren():
        tag = el.tag
        if tag == W + "p":
            out.append(_paragraph_block(el, styles))
        elif tag == W + "tbl":
            out.append(RawBlock(kind="table"))
        elif tag == W + "sdt":
            content = el.find(W + "sdtContent")
            if content is not None:
                _walk(content, styles, out)
        elif tag == W + "sectPr":
            continue
        elif isinstance(tag, str):
            out.append(RawBlock(kind="other"))


def _paragraph_block(p, styles) -> RawBlock:
    style_id = paragraph_style(p)
    name, level, is_title = styles.get(style_id, (style_id, None, False)) if style_id else (None, None, False)
    return RawBlock(
        kind="para",
        text=paragraph_text(p),
        style=name,
        heading_level=level,
        is_title=is_title,
        has_image=contains_drawing(p),
    )


def paragraph_style(p) -> str | None:
    """Style id of a w:p element, or None."""
    ppr = p.find(W + "pPr")
    if ppr is None:
        return None
    ps = ppr.find(W + "pStyle")
    return ps.get(W + "val") if ps is not None else None


def contains_drawing(p) -> bool:
    return next(p.iter(*IMAGE_TAGS), None) is not None


def paragraph_text(p) -> str:
    parts: list[str] = []
    _collect(p, parts)
    return "".join(parts)


def _collect(el, parts: list[str]) -> None:
    for child in el.iterchildren():
        tag = child.tag
        if not isinstance(tag, str) or tag in SKIP_SUBTREES:
            continue
        if tag == W + "t":
            parts.append(child.text or "")
        elif tag == W + "tab":
            parts.append("\t")
        elif tag in (W + "br", W + "cr"):
            parts.append(" ")
        elif tag == W + "noBreakHyphen":
            parts.append("-")
        elif tag == W + "softHyphen":
            continue
        elif tag in IMAGE_TAGS:
            continue
        else:
            _collect(child, parts)


def _style_map(document) -> dict[str, tuple[str, int | None, bool]]:
    """style_id -> (name, heading level or None, is_title). Follows base styles up to 4 levels."""
    out: dict[str, tuple[str, int | None, bool]] = {}
    for st in document.styles:
        try:
            sid, name = st.style_id, st.name
        except Exception:  # noqa: BLE001  latent/odd styles
            continue
        level, is_title, cur, depth = None, False, st, 0
        while cur is not None and depth < 4:
            n = (getattr(cur, "name", "") or "").strip()
            m = HEADING_RE.match(n)
            if m:
                level = int(m.group(1))
                break
            if n.lower() == "title":
                is_title = True
                break
            cur = getattr(cur, "base_style", None)
            depth += 1
        out[sid] = (name, level, is_title)
    return out
