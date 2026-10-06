"""Run order (scope 1.8, llm_polishing.md "Run order inside Step 3").

analyse(path, config, decisions_path=None, with_refs=False) -> (Report, Document)
 1. ingest.read                      -> Document (sections, parse, protected spans)
 2. rules.loader.load                -> RuleTable; registry.check_coverage fails loudly
 3. rules.regex_rules.run            B9.5 skip set first, then gate rows, then style rows
 4. rules.registry.run_python_rows   A6, A7, B9.7–B9.9, misc, number format
 5. checks.sentence / paragraph / format
 6. checks.soft                      findings + pair scores into stats
 7. checks.views
 8. refs.check (optional)
 9. decisions.load + attach; module_a_cleared
10. not_checked: document.skipped + unbuilt stages + fixed §2/§3 list (NOT_CHECKED_FIXED)
11. stats: per-rule counts, sentences total, share flagged per rule (§5 warns > 0.30)

Stages 2–9 are wrapped: a stage that raises NotImplementedError is recorded as "not built yet"
in Not checked by this tool and the run continues. Any other exception propagates (a bug must
not be hidden as a missing feature).
Ordering of findings: step, then module A before B, then document position.
The pipeline computes everything; hiding Module B is the renderer's job (report/).
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from checker.config import Config
from checker.findings import Finding, NotChecked, Report, View
from checker.model import Document

OVER_THRESHOLD_SHARE = 0.30
RULES_STAGE = "word rules and claim verbs (1.1, 1.2)"
# which stages feed which report step; a step whose stages all failed to run says "Not run"
STEP_STAGES = {
    1: [RULES_STAGE],
    2: ["sentence checks (1.3)", "paragraph checks (1.4)", RULES_STAGE],
    3: [RULES_STAGE],
    4: ["format checks (1.7)", "reference check (1.9)", RULES_STAGE],
    "soft": ["approximate checks (1.5)"],
}

NOT_CHECKED_FIXED: list[NotChecked] = [
    # §2 windows
    NotChecked("window 1", "message consistent across title / abstract / Discussion opening / Conclusion"),
    NotChecked("window 1", "seven moves present and in order; one theme per paragraph; each paragraph leads to the next"),
    NotChecked("window 2", "numbers with level + denominator (list task)"),
    NotChecked("window 2", "for/against paragraph per H; H restated where tested; zombie concepts; content in owning section; parallel H wording"),
    NotChecked("window 3", "each figure/table: title is a claim; caption stands alone; text stands alone; counts with percentages"),
    NotChecked("window 4", "where the test for each T2+ verb is; topic string; stress; first-sentence promise; passive justification"),
    # §3 human
    NotChecked("human", "does the evidence pay for the claim verb? (Module A decision)"),
    NotChecked("human", "is each number at the right level of analysis? right denominator?"),
    NotChecked("human", "does the rationale for and against each H hold?"),
    NotChecked("human", "does each citation say only what the source says?"),
    NotChecked("human", "is the title a sentence a reader could disagree with?"),
    NotChecked("human", "message and selection: which findings are necessary, which to cut"),
    NotChecked("human", "figures: which comparison each claim needs"),
]

SKIP_REASONS = {
    "table": "tables are checked in chat window 3",
    "image": "figures are checked in chat window 3",
    "caption": "captions are checked in chat window 3",
    "note": "display notes are checked in chat window 3",
    "display": "lines inside a table/figure block are checked in chat window 3",
    "label": "short label lines and bare URLs are not prose",
    "code": "code blocks are not prose",
    "textbox": "text boxes are not read",
    "other": "unrecognised document element",
}


def sort_key(f: Finding) -> tuple:
    return (int(f.step), 0 if f.module.value == "A" else 1, f.location.span.start)


def compute_stats(findings: list[Finding], total_sentences: int) -> dict[str, Any]:
    """Per-rule count and share of sentences flagged; warn list for > 0.30 (§5)."""
    per_rule: dict[str, set] = {}
    counts: Counter = Counter()
    for f in findings:
        counts[f.rule_id] += 1
        if f.location.sentence is not None:
            per_rule.setdefault(f.rule_id, set()).add((f.location.paragraph, f.location.sentence))
    rules = {}
    for rid, n in sorted(counts.items()):
        flagged = len(per_rule.get(rid, ()))
        share = flagged / total_sentences if total_sentences else 0.0
        rules[rid] = {"count": n, "sentences_flagged": flagged, "share": round(share, 4)}
    over = [rid for rid, r in rules.items() if r["share"] > OVER_THRESHOLD_SHARE]
    return {"rules": rules, "over_threshold": over}


def _skipped_not_checked(doc: Document) -> list[NotChecked]:
    by_kind = Counter(s.kind for s in doc.skipped)
    out = []
    for kind, n in sorted(by_kind.items()):
        out.append(NotChecked("checker", f"{n} × {kind} skipped at ingest", SKIP_REASONS.get(kind, "")))
    return out


def _section_summary(doc: Document) -> list[dict[str, Any]]:
    return [
        {"name": s.name, "kind": s.kind.value, "level": s.level,
         "paragraphs": len(s.body), "sentences": sum(len(p.sentences) for p in s.body)}
        for s in doc.sections
    ]


def analyse(path: Path, config: Config, decisions_path: Path | None = None,
            with_refs: bool = False, online: bool = True, nlp=None) -> tuple[Report, Document]:
    from checker import ingest

    doc = ingest.read(Path(path), config, nlp=nlp)
    findings: list[Finding] = []
    views: list[View] = []
    unbuilt: list[NotChecked] = []
    extra_not_checked: list[NotChecked] = []
    stats: dict[str, Any] = {}

    ran: dict[str, bool] = {}

    def stage(name: str, build_step: int, fn: Callable[[], Any]) -> Any:
        try:
            result = fn()
            ran[name] = True
            return result
        except NotImplementedError:
            ran[name] = False
            unbuilt.append(NotChecked("checker", f"{name}: not built yet", f"build step {build_step}"))
            return None

    def rules_stage() -> list[Finding]:
        from checker.rules import loader, regex_rules, registry
        table = loader.load(config.paths.polishing)
        out = regex_rules.run(doc, table, config)
        return out + registry.run_python_rows(doc, table, config)

    def checks_stage(module: str) -> Callable[[], list[Finding]]:
        def run() -> list[Finding]:
            import importlib
            return importlib.import_module(f"checker.checks.{module}").run(doc, config)
        return run

    def soft_stage() -> list[Finding]:
        from checker.checks import soft
        out, soft_stats = soft.run(doc, config)
        stats.update(soft_stats)
        return out

    def views_stage() -> list[View]:
        from checker.checks import views as v
        return v.run(doc, config)

    def refs_stage() -> list[Finding]:
        from checker.refs import check
        out, nc = check.run(doc, config, online=online)
        extra_not_checked.extend(nc)
        return out

    findings += stage(RULES_STAGE, 2, rules_stage) or []
    findings += stage("sentence checks (1.3)", 3, checks_stage("sentence")) or []
    findings += stage("paragraph checks (1.4)", 3, checks_stage("paragraph")) or []
    findings += stage("format checks (1.7)", 3, checks_stage("format")) or []
    findings += stage("approximate checks (1.5)", 4, soft_stage) or []
    views += stage("views (1.6)", 3, views_stage) or []
    if with_refs:
        findings += stage("reference check (1.9)", 7, refs_stage) or []
    else:
        extra_not_checked.append(NotChecked("checker", "reference check (1.9)", "run with --refs"))

    findings.sort(key=sort_key)

    cleared = False
    if decisions_path is not None:
        def decisions_stage() -> None:
            from checker import decisions
            stale = decisions.attach(findings, decisions.load(decisions_path))
            stats["stale_decisions"] = stale
        stage("decisions file", 6, decisions_stage)

    from checker.decisions import module_a_cleared
    stats["stages"] = ran
    cleared = bool(ran.get(RULES_STAGE)) and module_a_cleared(findings)

    total_sentences = doc.meta.get("sentences", 0)
    stats.update(compute_stats(findings, total_sentences))
    stats.update({
        "sentences": total_sentences,
        "paragraphs": len(doc.body_paragraphs()),
        "words": sum(len(p.text.split()) for p in doc.body_paragraphs()),
        "sections": _section_summary(doc),
        "reference_entries": len(doc.reference_entries),
        "warnings": doc.meta.get("warnings", []),
        "reader": doc.meta.get("reader"),
    })

    not_checked = unbuilt + _skipped_not_checked(doc) + extra_not_checked + NOT_CHECKED_FIXED
    report = Report(
        source=str(path),
        generated_at=now(),
        findings=findings,
        not_checked=not_checked,
        views=views,
        stats=stats,
        module_a_cleared=cleared,
    )
    return report, doc


def run(path: Path, config: Config, decisions_path: Path | None = None,
        with_refs: bool = False, online: bool = True, nlp=None) -> Report:
    return analyse(path, config, decisions_path, with_refs, online, nlp)[0]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
