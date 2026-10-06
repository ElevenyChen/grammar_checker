"""report.md: flat list by step, Module A first, Module B withheld until module_a_cleared
(or --all), soft band after the steps, then the views, then the fixed closing section
**Not checked by this tool**, which is always last.

Per finding: severity | rule_id | where | evidence | suggestion | decision.
Decided findings read as a change list: accepted rows show before and after; skipped rows are
marked; undecided rows are open.
"""
from __future__ import annotations

from pathlib import Path

from checker.findings import Choice, Finding, Report, Severity, Step
from checker.pipeline import STEP_STAGES

STEP_TITLES = {
    Step.CLAIM: "Step 1 — Claim audit (Module A)",
    Step.STRUCTURE: "Step 2 — Sentence and paragraph structure",
    Step.LANGUAGE: "Step 3 — Language (Module B)",
    Step.PROOF: "Step 4 — Format and references",
}
STAGE_TITLES = {
    "checker": "This tool",
    "window 1": "Chat window 1 — Architecture",
    "window 2": "Chat window 2 — Advisor gate",
    "window 3": "Chat window 3 — Displays",
    "window 4": "Chat window 4 — Language, human rows",
    "human": "Human only",
}


def _cell(text: str | None, limit: int = 160) -> str:
    if not text:
        return ""
    t = " ".join(str(text).split())
    if len(t) > limit:
        t = t[: limit - 1] + "…"
    return t.replace("|", "\\|")


def _where(f: Finding) -> str:
    loc = f.location
    s = f" s{loc.sentence + 1}" if loc.sentence is not None else ""
    return f"{loc.section or loc.section_kind} ¶{loc.paragraph}{s}"


def _decision(f: Finding) -> str:
    d = f.decision
    if d is None:
        return "open"
    if d.choice == Choice.ACCEPT:
        return f"accepted: {f.evidence} → {f.suggestion or '(delete)'}"
    if d.choice == Choice.PICK:
        return f"picked: {f.evidence} → {d.picked}"
    if d.choice == Choice.DELETE:
        return f"delete: {f.evidence}"
    return d.choice.value


def _table(findings: list[Finding]) -> list[str]:
    lines = ["| sev | rule | where | evidence | suggestion | decision |",
             "|---|---|---|---|---|---|"]
    for f in findings:
        if f.action.value == "delete":
            sug = "(delete)"
        else:
            sug = f.suggestion or (" / ".join(f.candidates) if f.candidates else "")
        if f.score is not None:
            sug = f"{sug} (score {f.score:.2f})".strip()
        lines.append(f"| {f.severity.value} | {f.rule_id} | {_cell(_where(f), 60)} | "
                     f"{_cell(f.evidence)} | {_cell(sug, 80)} | {_cell(_decision(f), 80)} |")
    return lines


def _module_a_state(report: Report) -> str:
    if _not_run(report, 1):
        return "not run"
    return "cleared" if report.module_a_cleared else "open"


def _ingest(report: Report) -> list[str]:
    st = report.stats
    out = ["## Ingest", "",
           f"Reader: {st.get('reader')} · {st.get('words', 0):,} words · "
           f"{st.get('sentences', 0)} sentences · {st.get('paragraphs', 0)} paragraphs · "
           f"{st.get('reference_entries', 0)} reference entries", "",
           "| section | kind | paragraphs | sentences |", "|---|---|---|---|"]
    base = _indent_base(report)
    for s in st.get("sections", []):
        indent = "  " * max(s["level"] - base, 0)
        out.append(f"| {indent}{_cell(s['name'], 70) or '(untitled)'} | {s['kind']} | {s['paragraphs']} | {s['sentences']} |")
    warnings = st.get("warnings", [])
    if warnings:
        out += ["", "Warnings:"] + [f"- {_cell(w, 200)}" for w in warnings]
    if st.get("over_threshold"):
        out += ["", "Rules flagging more than 30 % of sentences (wrong threshold, not a bad draft): "
                + ", ".join(st["over_threshold"])]
    if st.get("stale_decisions"):
        out += ["", f"{len(st['stale_decisions'])} earlier decisions no longer match a sentence (the text changed)."]
    return out + [""]


def _views(report: Report) -> list[str]:
    out: list[str] = []
    for v in report.views:
        out += [f"### View: {v.name}", ""]
        if not v.rows:
            out += ["(empty)", ""]
            continue
        cols = list(v.rows[0].keys())
        out += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        out += ["| " + " | ".join(_cell(r.get(c), 200) for c in cols) + " |" for r in v.rows]
        out.append("")
    return (["## Views", ""] + out) if out else []


def _not_checked(report: Report) -> list[str]:
    out = ["## Not checked by this tool", ""]
    stages: dict[str, list] = {}
    for n in report.not_checked:
        stages.setdefault(n.stage, []).append(n)
    for stage in list(STAGE_TITLES) + [s for s in stages if s not in STAGE_TITLES]:
        items = stages.get(stage)
        if not items:
            continue
        out += [f"### {STAGE_TITLES.get(stage, stage)}", ""]
        out += [f"- {n.item}" + (f" — {n.reason}" if n.reason else "") for n in items]
        out.append("")
    return out


def _not_run(report: Report, key) -> bool:
    """True when none of the stages feeding this step ran (all unbuilt or skipped)."""
    stages = report.stats.get("stages", {})
    return not any(stages.get(name) for name in STEP_STAGES[key])


def _indent_base(report: Report) -> int:
    levels = [s["level"] for s in report.stats.get("sections", []) if s["level"] > 0]
    return min(levels) if levels else 1


def render(report: Report, show_module_b: bool) -> str:
    name = Path(report.source).name
    main = [f for f in report.findings if f.severity != Severity.SOFT]
    soft = [f for f in report.findings if f.severity == Severity.SOFT]
    lines = [f"# Checker report — {name}", "",
             f"Generated {report.generated_at} · {len(report.findings)} findings · "
             f"Module A {_module_a_state(report)}", ""]
    lines += _ingest(report)

    for step in Step:
        title = STEP_TITLES[step]
        items = [f for f in main if f.step == step]
        lines += [f"## {title}", ""]
        if _not_run(report, int(step)):
            lines += ["Not run: the checks for this step are not built yet.", ""]
            continue
        if step == Step.LANGUAGE and not show_module_b:
            lines += [f"Withheld until every Module A gate finding has a decision "
                      f"({len(items)} findings waiting). Use --all to show.", ""]
            continue
        lines += (_table(items) if items else ["No findings."]) + [""]

    lines += ["## Approximate checks (soft)", ""]
    if _not_run(report, "soft"):
        lines += ["Not run: the checks for this step are not built yet.", ""]
    else:
        lines += (_table(soft) if soft else ["No findings."]) + [""]
    lines += _views(report)
    lines += _not_checked(report)
    return "\n".join(lines).rstrip() + "\n"


def write(report: Report, out: Path, show_module_b: bool) -> Path:
    out.write_text(render(report, show_module_b), encoding="utf-8")
    return out
