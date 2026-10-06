"""report.json: Report.as_dict() plus the document text and paragraph spans so the page can
render the left pane without re-reading the docx.

write(report, doc, out) -> Path
Shape: {"report": Report.as_dict(),
        "document": {"source", "text",
                     "paragraphs": [{index, start, end, section, kind, is_heading, heading_level}],
                     "sentences": [{doc_index, paragraph, index, start, end}],
                     "skipped": [{kind, where, note}]}}
`location.paragraph` in a finding is the paragraph `index` here; offsets index into `text`.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from checker.findings import Report
from checker.model import Document


def payload(report: Report, doc: Document) -> dict:
    paragraphs = []
    sentences = []
    for p in doc.paragraphs:
        paragraphs.append({
            "index": p.index, "start": p.span.start, "end": p.span.end,
            "section": p.section.name, "kind": p.section.kind.value,
            "is_heading": p.is_heading, "heading_level": p.heading_level,
        })
        for s in p.sentences:
            sentences.append({"doc_index": s.doc_index, "paragraph": p.index, "index": s.index,
                              "start": s.span.start, "end": s.span.end})
    return {
        "report": report.as_dict(),
        "document": {
            "source": doc.source,
            "text": doc.text,
            "paragraphs": paragraphs,
            "sentences": sentences,
            "skipped": [asdict(s) for s in doc.skipped],
        },
    }


def write(report: Report, doc: Document, out: Path) -> Path:
    out.write_text(json.dumps(payload(report, doc), ensure_ascii=False, indent=1), encoding="utf-8")
    return out
