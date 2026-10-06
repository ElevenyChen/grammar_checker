"""Command line (scope §7 session).

checker run DRAFT [--config checker.toml] [--decisions decisions.json] [--refs] [--offline] [--all] [--out DIR]
checker refs DRAFT [--offline]                 1.9 only
checker apply DRAFT DECISIONS [--out FILE]     1.10
checker stats REPORT.json                      §5
checker label-pairs REPORT.json [--n 50] [--out pairs.csv]
checker tune PAIRS.csv
checker comments DRAFT REPORT.json [--out FILE]   docx comments (later)
checker rules [--config]                       print the parsed rule table and coverage (debug)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from checker.config import Config


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="checker", description="The machine finds. The human decides.")
    p.add_argument("--config", type=Path, default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run the checker on a draft")
    r.add_argument("draft", type=Path)
    r.add_argument("--decisions", type=Path, default=None)
    r.add_argument("--refs", action="store_true", help="also run 1.9")
    r.add_argument("--offline", action="store_true", help="refs: cache only")
    r.add_argument("--all", action="store_true", help="show Module B even if A is not cleared")
    r.add_argument("--out", type=Path, default=None, help="output directory (default: next to draft)")

    f = sub.add_parser("refs", help="reference check only (1.9)")
    f.add_argument("draft", type=Path)
    f.add_argument("--offline", action="store_true")
    f.add_argument("--out", type=Path, default=None)

    a = sub.add_parser("apply", help="write a copy with accepted replacements (1.10)")
    a.add_argument("draft", type=Path)
    a.add_argument("decisions", type=Path)
    a.add_argument("--out", type=Path, default=None)

    s = sub.add_parser("stats", help="false-positive table per rule (§5)")
    s.add_argument("report", type=Path)

    l = sub.add_parser("label-pairs", help="sample sentence pairs for 1.5 labelling")
    l.add_argument("report", type=Path)
    l.add_argument("--n", type=int, default=50)
    l.add_argument("--out", type=Path, default=Path("pairs.csv"))

    t = sub.add_parser("tune", help="pick F1-best cut from labelled pairs")
    t.add_argument("pairs", type=Path)

    c = sub.add_parser("comments", help="docx comments renderer (later)")
    c.add_argument("draft", type=Path)
    c.add_argument("report", type=Path)
    c.add_argument("--out", type=Path, default=None)

    sub.add_parser("rules", help="print the parsed rule table and implementation coverage")
    return p


def cmd_run(args, config: Config) -> int:
    from checker import pipeline
    from checker.decisions import module_a_cleared
    from checker.report import html_report, json_report, md_report

    if not args.draft.exists():
        raise SystemExit(f"no such file: {args.draft}")
    out_dir = args.out or args.draft.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    report, doc = pipeline.analyse(args.draft, config, decisions_path=args.decisions,
                                   with_refs=args.refs, online=not args.offline)
    stem = args.draft.stem
    paths = [
        json_report.write(report, doc, out_dir / f"{stem}.report.json"),
        md_report.write(report, out_dir / f"{stem}.report.md",
                        show_module_b=args.all or module_a_cleared(report.findings)),
        html_report.write(report, doc, out_dir / f"{stem}.report.html"),
    ]
    st = report.stats
    print(f"{st['sentences']} sentences in {st['paragraphs']} paragraphs, "
          f"{len(report.findings)} findings, {len(st.get('warnings', []))} ingest warnings")
    for p in paths:
        print(f"  {p}")
    return 0


def cmd_refs(args, config: Config) -> int:
    from checker import ingest
    from checker.refs import check
    doc = ingest.read(args.draft, config)
    findings, _ = check.run(doc, config, online=not args.offline)
    for f in findings:
        print(f"{f.severity.value:5} {f.rule_id:20} {f.evidence[:90]}  {f.suggestion or ''}")
    return 0


def cmd_apply(args, config: Config) -> int:
    from checker.apply import apply
    out = args.out or args.draft.with_name(args.draft.stem + ".checked.docx")
    log = apply(args.draft, args.decisions, out, config)
    print(log.to_markdown())
    return 0


def cmd_stats(args, config: Config) -> int:
    from checker.calibrate import stats
    print(stats.run(args.report))
    return 0


def cmd_label_pairs(args, config: Config) -> int:
    from checker.calibrate import label_pairs
    label_pairs.run(args.report, args.n, args.out)
    return 0


def cmd_tune(args, config: Config) -> int:
    from checker.calibrate import tune
    print(tune.run(args.pairs))
    return 0


def cmd_comments(args, config: Config) -> int:
    from checker.report import docx_comments
    raise SystemExit("docx comments: not built yet (scope 1.8, fourth renderer)")


def cmd_rules(args, config: Config) -> int:
    from checker.rules import loader, registry
    import checker.rules.impl  # noqa: F401
    table = loader.load(config.paths.polishing)
    for r in table.rows + table.skip_rows:
        kind = "regex" if r.is_regex else ("python ✓" if r.id in registry.RULES else "python ✗ MISSING")
        print(f"{r.id:12} step{int(r.step)} {str(r.severity and r.severity.value):5} {str(r.action and r.action.value):7} {kind:16} {r.pattern[:60]}")
    return 0


COMMANDS = {"run": cmd_run, "refs": cmd_refs, "apply": cmd_apply, "stats": cmd_stats,
            "label-pairs": cmd_label_pairs, "tune": cmd_tune, "comments": cmd_comments, "rules": cmd_rules}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = Config.load(args.config)
    try:
        return COMMANDS[args.cmd](args, config)
    except NotImplementedError as e:
        print(f"not built yet: {e or args.cmd}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
