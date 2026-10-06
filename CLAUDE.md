# Writing checker — project guide

Read `checker_scope.md` first. It is the contract. This file says how the code is laid out and how to work in it.

## What this is
A mechanical checker for one person's scientific-writing house style. Python 3.11, local only. Rules live in markdown (`llm_polishing.md` appendix, `scientific_writing_map.md`); code loads them at runtime. Output is a JSON report, a markdown report, and a self-contained HTML decision panel. The draft is never rewritten except by `checker apply`, which writes a new copy.

One principle: **the machine finds, the human decides.** No check proposes text that a rule row did not fully specify. No rewriting, no paraphrase, no suggested sentences.

## Status
- **Build step 1 done (2026-10-06).** Ingest (docx + markdown), section kinds, segmentation, protected spans, pipeline, JSON and markdown reports. Verified on the PSJ draft and the NMS revised draft: all section kinds correct, no tool-caused sentence splits left.
- Next: build step 2.

## Layout (structure fixed 2026-10-06; unbuilt bodies raise NotImplementedError)
```
checker/
  model.py        Document → Section → Paragraph → Sentence, spans into Document.text   (done)
  findings.py     Finding record, Decision, NotChecked, View, Report, finding_id()      (done)
  config.py       Config from checker.toml, defaults = the scope's numbers             (done)
  pipeline.py     analyse()/run(); stages; unbuilt stage -> "not built yet" in report   (done)
  decisions.py    decisions.json load/attach/save (stub); module_a_cleared (done)
  apply.py        the only writer: decisions → new docx + change log                   (stub)
  cli.py          run / refs / apply / stats / label-pairs / tune / comments / rules   (wired)
  ingest/         blocks (shared display filter), docx_reader, md_reader, sections,
                  segment (spaCy + boundary_guard), protect                            (done)
  rules/          loader (appendix → RuleRow), registry (@rule id), regex_rules, forms (stubs)
  rules/impl/     Python implementations for non-regex appendix rows                   (stubs)
  checks/         sentence (1.3), paragraph (1.4), soft (1.5), format (1.7), views (1.6)(stubs)
  refs/           entries, extract, crossref (cached), compare, orphans, check (1.9)   (stubs)
  report/         json_report, md_report (done), html_report (template TODOs, step 6), docx_comments
  calibrate/      stats (§5), label_pairs, tune (1.5 thresholds)
tests/            contract tests; most are xfail(NotImplementedError) until built
check_refs.py     legacy script; refs/ supersedes it. Delete once refs/ passes on the PSJ draft.
```

## Ingest behaviour worth knowing
- What counts as body text is decided in `ingest/blocks.py` for both readers: captions ("Figure 3.", "Table 2 Title"), "Note." lines, ᵃ/†/`*p <` notes, short label lines inside a table/figure block, keywords lines, bare URLs, and short colon-ended labels are skipped and listed in Not checked. "Figure 3 shows that…" (lower-case after the number) stays body text on purpose: it is a B5 target.
- A heading-styled paragraph over 25 words is body text plus an ingest warning.
- Section kind: named heading at any depth starts its kind; unnamed headings inherit from the nearest shallower heading. Names live in `Config.sections`.
- Sentence starts are only allowed after terminal punctuation (`boundary_guard`), plus abbreviation and parenthesis guards. Check new drafts with the suspicious-sentence audit (short, lower-case start, no terminal punctuation); every remaining hit should be real text.
- Unbuilt stages never make a step look clean: the markdown says "Not run" and the header says "Module A not run".

## Conventions
- Every check is `run(doc, config) -> list[Finding]` (views return `list[View]`, soft returns `(findings, stats)`). Checks read the Document model only; never the file.
- `Finding.id = finding_id(rule_id, sentence_text, occurrence)`. Never key anything on paragraph number alone.
- Rule ids from the appendix are the source of truth for regex rows. Non-appendix checks use the fixed ids in their module docstrings (S.*, P.*, SOFT.*, F.*, R.*). Keep that list and the docstrings in sync.
- Severity comes from the table or the docstring, never decided ad hoc. Re-grading happens in the markdown (§5), not in code.
- Section kind is on every sentence via `sentence.section.kind`. Use it; do not re-detect headings.
- Protected spans (`Sentence.protected`) are checked by the regex engine; Python rules must check them too.
- Drop a hit rather than guess. False negatives are cheap here; false positives create work (scope: "it must not create new work").
- No network except `refs/crossref.py`, and that goes through the cache.
- Thresholds are in `Config.thresholds`; do not hard-code numbers in checks.

## Build order and definition of done (scope §9)
1. **Ingest + report skeleton.** `md_reader`, `docx_reader`, `sections`, `segment`, `protect`, `json_report`, `md_report`, `pipeline.run` with no rules. Done when `checker run tests/fixtures/sample.md` writes three files and `report.md` ends with *Not checked by this tool*, and the PSJ draft docx ingests with the right section kinds.
2. **Rule table.** Add the `id` column to the appendix in `llm_polishing.md` (format `id | step | severity | action | pattern | replacement`; ids like B1.1, B2.3, A1.T3, B9.4; keep B9.x as is). Then `loader`, `regex_rules`, `forms`, `registry`, Module A rows. Done when `checker rules` shows no MISSING and `tests/test_forms.py` passes. First false-positive count on the PSJ draft.
3. **Parse checks.** `checks/sentence.py`, `checks/paragraph.py`, `rules/impl/*`, `checks/format.py`, `checks/views.py`.
4. **Soft checks** with `label_pairs` and `tune`. Do not set `soft_link` / `soft_outlier` by eye.
5. **Calibration.** `calibrate/stats.py`; re-grade severities in the markdown.
6. **Page.** Fill the TODOs in `report/templates/report.html`; `decisions.py`. Done when accept/skip survive a re-run and Module B unfolds only after A is cleared.
7. **apply**, then **refs**, then **docx_comments**.

## Environment (done 2026-10-06)
```
source .venv/bin/activate              # Python 3.11, spaCy 3.8, en_core_web_lg, python-docx 1.2, pytest
checker run DRAFT.docx --out OUTDIR    # or: python -m checker run …
pytest                                 # slow tests need en_core_web_lg; skip with -m "not slow"
cp checker.toml.example checker.toml   # set crossref_contact before build step 7
pip install -e ".[soft]"               # build step 4 only: sentence-transformers (pulls in PyTorch)
```
Git repository initialised; nothing committed yet. Drafts, reports and decisions are git-ignored: never commit a manuscript.

Test drafts (read-only, outside the repo; copy to a scratch folder before running):
- PSJ draft: `~/Desktop/Paper Writing/2025_Accrete and Reform_ Dual Mechanisms of Institutional Change in Online Communities.docx`
- NMS revised: `~/Desktop/Paper Writing/Chen et al. 2025/2026_ChenEtAl_RuleChange_NewMedia+Society_REVISED.docx`

## Do not
- Add a synonym or term dictionary (§4).
- Call a language-model API from the checker (§6). If ever added: pinned snapshot, temperature 0, indices not text, cached.
- Let the page write to the docx. `apply` is the only writer.
- Copy appendix rows into code. If a row needs Python, register it by id in `rules/impl`.
- Check tables, figures, or captions. They are skipped at ingest and belong to chat window 3.
