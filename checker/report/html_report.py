"""report.html: the decision panel (scope §7). Template in templates/report.html; the JSON payload
is inlined into a <script id="data" type="application/json"> tag so the page opens from file://.

write(report, doc, out) -> Path
The template is static; this module only substitutes the payload and the title.
"""
from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from checker.findings import Report
from checker.model import Document
from checker.report.json_report import payload


def render(report: Report, doc: Document) -> str:
    template = resources.files("checker.report").joinpath("templates/report.html").read_text(encoding="utf-8")
    data = json.dumps(payload(report, doc), ensure_ascii=False).replace("</", "<\\/")
    return template.replace("/*__DATA__*/null", data).replace("__TITLE__", Path(report.source).name)


def write(report: Report, doc: Document, out: Path) -> Path:
    out.write_text(render(report, doc), encoding="utf-8")
    return out
