# Writing Checker — Phase 1 Scope

Status: approved for build. Date: 2026-10-01. Updated 2026-10-06 (input, output, reference check, UI, open items).
Owner: Eleveny. Rules come from `scientific_writing_map.md`, `llm_polishing.md`, `figure_table_checklist.md`.

## Purpose

A mechanical checker that runs the parts of the writing map a machine can run, and hands the rest to a chat window or to a human. It reduces checking work. It must not create new work.

## One principle

The machine finds. The human decides. The checker and the chat audits report; they never rewrite, never paraphrase, never suggest new sentences.

## Pipeline

```
draft → 1. mechanical checker → 2. four chat-window audits → 3. human
```

Each stage lists what it did not check and passes that list to the next stage.

---

## 1. Mechanical checker (build now)

Python, spaCy `en_core_web_lg`, sentence-transformers (local). No API.

### 1.0 Input
One file: the manuscript `.docx` as sent to the advisor. Body text only. Tables, images, captions, and the reference section are skipped by every check in 1.1–1.7; the reference section is read once, separately, by 1.9. Displays belong to chat window 3.

Section headings come from Word paragraph styles (Heading 1/2). Fallback: a short paragraph matching a standard section name (Introduction, Methods, Results, Discussion, Limitations, Conclusion, References). Markdown input is a second reader using `#` lines.

Internal model: document → section (name, kind) → paragraph → sentence, each with its character span and spaCy parse. Every check reads this model and nothing else. Section kind is a first-class field; 1.3 passive, 1.4 orphan terms, B9.8, and the B4 Intro/Conclusion exemption all depend on it.

Optional sidecars next to the draft: `decisions.json` from the last session (1.8), and a config file (Crossref contact address, section-name fallback list).

### 1.1 Word rules
Source: the machine appendix in `llm_polishing.md`. Load that table at runtime. Do not copy it into code. Actions: `replace`, `delete`, `flag`.

Loader contract:
- The appendix needs an `id` column before the loader is written. The report (1.8) and the calibration count (§5) both key on `rule_id`. Add the ids in the markdown, not in code.
- A row whose pattern compiles as a regex runs on each sentence string.
- A row that does not compile (elegant variation, of-density, non-temporal *while/since*, shared 8-gram, orphan term, B9.9) is looked up by id in a Python registry. The loader fails loudly if no implementation exists. The markdown says *what* is checked; code says *how*.
- B9.5 skip-list runs first and protects its subjects from B9.1–B9.3.
- `replace` rows must fully determine the new text. Rows that list alternatives (*develop / change*, *help / ease*, *can / could*) are shown with their candidates; the human picks one and the chosen string is stored in the decision. Inflection and case (*Utilizes → Uses*, *utilized → used*) come from a per-row form map in code, tested with a before/after fixture file.
- A replacement that changes words outside the match (B9.3 rewrites tense and subject) is a sentence-grade row: accepted one at a time, never batch. Pure word swaps may be batch-accepted per rule.
- Protected spans are masked before any row runs: direct quotations, parenthetical citations, URLs and DOIs, headings, reference list.

### 1.2 Claim-verb flags (Module A machine rows)
T3–T5 verbs, prove/debunk/definitively, non-statistical *significant*, stacked hedges, null hypotheses written as H. Flag with the sentence. No judgment.

### 1.3 Sentence checks (dependency parse)
- Subject more than 6 words from sentence start
- `It is … that` / `There are …` openers
- Last 3–4 content words are metadiscourse, or repeat the previous sentence's ending
- Nominalization on a light verb (*perform an analysis*)
- Subject–verb gap > 8 words
- Bare *this / these* as subject
- Passive run ≥ 3 sentences outside Methods

### 1.4 Paragraph checks
- Topic/clincher candidate check. Four symptoms only: first sentence starts with a list/time word (B6); last sentence is only a citation or a display reference; last sentence ends in metadiscourse; paragraph has ≤ 2 sentences.
- First-sentence promise (B9.9): last 3–4 content words of sentence 1 do not recur in the paragraph.
- Orphan terms (A6): capitalized or technical terms that first appear after the Results heading.
- Repeated passages (A7): n-gram overlap across paragraphs.

### 1.5 Approximate checks — severity `soft`
No API. Lower precision than the rules above; reported in their own band.
- Old-before-new link: subject of sentence N vs. end of sentence N−1. Lemma match → word-vector match → sentence-embedding fallback. No term dictionary (unmaintainable). Thresholds set by hand-labeling 40–60 sentence pairs from the PSJ draft and picking the F1-best cut.
- Paragraph outlier: sentence embedding vs. paragraph centroid. Paragraphs of ≥ 4 sentences only. Report cosine and position; the outlier may be off-topic or may be the real message.

### 1.6 Views (no judgment)
- Skeleton view: first and last sentence of every paragraph, in order. This is the input for chat audit 1.
- Hypothesis sentences side by side (H1 … Hn), for the human to check parallel structure.
- Number formats found in the text, in one table.

### 1.7 Format
Thousands separators, leading zeros, χ² vs Chi-squared, theory names lowercase / initialisms uppercase. In-text citations vs. reference list moved to 1.9.

### 1.8 Report
One record format for every check:
`id | step | severity | rule_id | action | location | evidence | suggestion | decision`
`id` is a hash of `rule_id` + normalised sentence text, so a finding keeps its identity across runs after unrelated edits. `location` = section, paragraph index, sentence index, character span.
Severity bands: `gate`, `style` (both from `llm_polishing.md`), `soft` (1.5 only).
Ordered by step. Module A results come first. Module B is withheld until every `gate` finding in Module A has a decision in `decisions.json`; the tool always computes everything, the report only hides.

Each stage appends to a **Not checked by this tool** list (what it skipped and why, plus §2 and §3), written at the end of every report.

Outputs, written next to the draft:

| File | What | Reader |
|---|---|---|
| `report.json` | every finding; source for the other two | the tool, the page |
| `report.md` | flat list by step, ending with *Not checked by this tool* | human; pasted into chat windows as the task list |
| `report.html` | the reading surface (§7), JSON inlined so it opens from the filesystem | human |
| `decisions.json` | exported from the page; one entry per decided finding: `id, rule_id, location, evidence, proposed, choice (accept / skip / pick:<text> / delete / seen), time` | the tool on the next run; `apply` (1.10) |

Docx comments are a fourth renderer, added after the findings are right. Recent `python-docx` supports `add_comment`; one comment per finding on a copy of the draft, original untouched. Sharing format for advisors, not the reading format.

The draft is never rewritten by the checker or the page.

### 1.9 Reference check (from `check_refs.py`)
Runs as step 4, on the reference section only, results in the 1.8 record format. Needs internet on the first run; every Crossref response is cached locally by DOI, so later runs are offline. This is a deterministic lookup, not model-based classification, and does not break the API-free decision (§6).

- **Existence and metadata** (existing script): DOI resolved on Crossref; title similarity, first author, year (±1 tolerated for online-first), volume, pages. FAIL = different paper → `gate`. WARN = drift → `style`.
- **Non-DOI entries** (new, opt-in): Crossref bibliographic query by title + first author; no hit above the title cut → `gate`, "unconfirmed". Turns the manual checklist into only the entries a lookup could not find.
- **Orphan match, two ways** (new): extract author-year citations from body text (parenthetical and narrative, *et al.*, `&` vs *and*, year suffixes, semicolon lists); key each reference entry by first-author surname + year. Cited-but-not-listed → `gate`. Listed-but-not-cited → `style`. Near misses (surname spelling, year off by one) reported separately.
- What the source actually says stays human-only (§3).

Changes while moving the script into the package: read the reference section from the document model (docx exports often have no blank lines between entries); accept a bare `doi:` prefix; contact address and output paths from config; anchor the pages regex after the volume; treat the 0.55 / 0.80 title cuts as calibration rows (§5).

### 1.10 Apply
`apply draft.docx decisions.json` writes a new copy with accepted `replace` / `delete` rows applied, plus a markdown change log (location, before, after). Rules:
- Re-locate each decided sentence by text, re-match the span. Sentence changed since the decision → skip, list as stale. Nothing is applied by paragraph number.
- Work on the concatenated paragraph text; split Word runs at span boundaries; keep the first run's formatting. This is the error-prone part; test on the real draft first.
- Re-run the checker on the copy: accepted rows must yield zero findings; list any new finding a replacement created.
- Tracked changes come from Word (Review → Compare, original vs copy), not from the tool.

---

## 2. Chat-window audits (hook — prompts to be written later)

Four separate chat conversations in the Writing Lesson project, run after §1. The window sees the whole text, which the checker cannot. Rule files are already in the project; do not paste them.

| Window | Rules | Input | Checks |
|---|---|---|---|
| 1 Architecture | map A, B | title, abstract, headings, skeleton view (1.6) | message consistent across title / abstract / Discussion opening / Conclusion; seven moves present and in order; one theme per paragraph; each paragraph leads to the next |
| 2 Advisor gate | map D (all 10) | full text | numbers with level + denominator (list task); for/against paragraph per H; H restated where tested; zombie concepts; content in the owning section; parallel H wording (list, not verdict) |
| 3 Displays | `figure_table_checklist.md` | each figure/table + caption + the paragraph that cites it | title is a claim; caption stands alone; text stands alone; counts with percentages |
| 4 Language, human rows | `llm_polishing.md` Module A evidence location, B9.H1–H4 | one section per run | where the test for each T2+ verb is; topic string; stress; first-sentence promise; passive justification |

Rules for all four prompts (to be written):
- Report only. No rewriting, no paraphrase, no suggested sentences — even if asked.
- Output one line per hit: `rule_id | location | verbatim sentence | verdict`.
- `pass` is an allowed answer.
- Check only items in the given files. Do not add rules.
- Level/denominator and citation fidelity are list tasks, not verdicts.
- Input includes the checker's "Not checked by this tool" section as the task list.

Files not fed to the windows: `advisor_comments_digest.md` (evidence, not rules), `Scientific_Writing_Skill_v3.1.md` (not vetted), `cheatsheet.md` (duplicate of the map).

---

## 3. Human only (hook — listed in every report)

- Does the evidence pay for the claim verb? (Module A decision)
- Is each number at the right level of analysis? Right denominator?
- Does the rationale for and against each H hold?
- Does each citation say only what the source says?
- Is the title a sentence a reader could disagree with?
- Message and selection: which findings are necessary, which to cut
- Figures: which comparison each claim needs

---

## 4. Out of scope, and why

| Item | Why |
|---|---|
| Rewriting of any kind | Judgment is not outsourced (ITP) |
| Synonym / term dictionary | Never complete; endless false positives; cohesion is a human skill to keep |
| Outline as input | Creates work for the user. The checker outputs a skeleton instead (1.6) |
| Data / evidence verification module | Appendix + chat window already do this |
| Figure and table generation or checking in the tool | Window 3 handles it |
| Intro paragraph template (P1–P7) | Window 1 + skeleton view |
| API-based classification (seven moves, section ownership) | Needs whole-text context; windows do it better and cheaper |
| General grammar / fluency correction (Grammarly-style) | Needs a trained model and data; a homemade one is unreliable. This tool is a linter for house style: it proposes only what a row in the markdown says, so it cannot invent a suggestion, and every false positive traces to one rule. Grammar and fluency go to the chat windows or Word's editor |
| Editing the draft from the page | A browser cannot write a docx safely; the page is a decision surface, `apply` (1.10) is the only writer |
| Tables and figures in the input | Skipped at ingest; window 3 checks displays |

---

## 5. Calibration plan

1. Run §1 on the PSJ draft once.
2. Count false positives per `rule_id`.
3. A rule that flags > 30% of sentences has a wrong threshold, not a bad draft.
4. Re-grade severity by false-positive rate. Candidate rows: B9.4, B9.8, B9.9, all of 1.5.
5. Hand-label the sentence pairs for 1.5 before tuning (see 1.5).

## 6. Decisions log

- 2026-10-01 — Three stages: checker → four chat windows → human. Checker is API-free.
- 2026-10-01 — No synonym dictionary. No outline input. No rewriting anywhere.
- 2026-10-01 — Approximate checks stay in the checker with severity `soft`; whole-text checks go to the windows.
- 2026-10-01 — Chat prompts deferred; hook in §2.
- 2026-10-01 — If an API is ever added: pin a dated model snapshot, temperature 0, return sentence indices not text, cache every call locally. Candidate: Sonnet 5.
- 2026-10-06 — Input is the docx body text only. Tables, figures, captions skipped; reference section read only by 1.9.
- 2026-10-06 — Rules stay in the markdown. Appendix gets an `id` column. Non-regex rows get Python implementations under their id; loader fails if one is missing.
- 2026-10-06 — JSON is the primary output; markdown and HTML are rendered from it. Docx comments are a later fourth renderer, for sharing.
- 2026-10-06 — Decisions persist in `decisions.json`, keyed by finding id (rule + sentence text). Module B is withheld until every gate finding in A has a decision.
- 2026-10-06 — The page is a decision panel, not an editor. It shows the detected text and the decision state; no before/after diff. `apply` is the only writer; Word Compare gives tracked changes.
- 2026-10-06 — `check_refs.py` folded in as step 4 with cached Crossref lookups and a two-way orphan match. Deterministic lookup is not the API the API-free decision excludes.
- 2026-10-06 — Not a Grammarly clone. Linter model: only table-specified proposals, no trained corrector. Only 1.5 needs labelled data.

## 7. UI — decision panel

A single local HTML file, `report.html`, written per run with the JSON inlined. Vanilla JS, no server, no build step, no framework. Opens by double-click, can be emailed.

Layout:
1. Two panes. Left: the draft, paragraph by paragraph, unchanged text, serif, ~65-character lines, 18px, 1.6 line height. Detected spans underlined in severity colour: red `gate`, amber `style`, grey `soft`. The paragraph in view has a left border.
2. Right: findings for the paragraph in view, one line each: colour dot, `rule_id`, evidence, and for `replace` / `delete` rows the suggestion word so accept has a meaning. No tables, no nested lists, no rendered diff, no before/after sentence. An intersection observer on the left pane decides which paragraph is current; clicking a finding scrolls the left pane to the span and flashes it.
3. Keyboard: next / previous finding; accept / skip on `replace` and `delete` rows; pick on rows with candidates; a one-key delete on `flag` rows whose rule names deletion as an outcome (-ly adverbs); seen on other `flag` rows. A focus mode shows one finding at a time.
4. A decision changes the mark, never the text: accept → green underline; skip → faded; seen → faded. The left pane is read-only.
5. Module A first. The Module B list stays folded until every red Module A line has a decision.
6. Decisions go to local storage as you work and export as `decisions.json` (download). The checker reads it on the next run; `apply` consumes it.
7. `report.md` and docx comments (1.8) stay as secondary outputs for sharing.

Session:
1. Export the draft as docx. Run the checker (about a minute for 10,000 words, mostly the parse).
2. Open the page. Decide every Module A line. Export decisions.
3. Re-run with the decisions file. Module B unfolds. Decide. Export.
4. `apply` → edited copy + change log. Open in Word, Compare against the original, accept or reject there.
5. Run 1.9 once near the end (internet on first run).
6. Paste *Not checked by this tool* from `report.md` into the four chat windows as their task list.

## 8. Open

Resolved 2026-10-06:
- Docx comment output → fourth renderer, after findings are right (1.8).
- Section headings → Word paragraph styles, name-match fallback (1.0).

Still open:
- Docx run-splitting in `apply` (1.10): test on the real draft before trusting it.
- B9.3: keep as `replace` (sentence-grade, one at a time) or demote to `flag`? Decide after the first false-positive count.
- Which rows with alternative replacements become pick rows and which get a single canonical word (B7 *evolve*: develop or change?).
- Title-similarity cuts in 1.9 (0.55 / 0.80) untested on this reference list.
- Environment: Python 3.11 present; spaCy, sentence-transformers, python-docx not installed. Virtual environment with `en_core_web_lg` and a small local sentence encoder is step zero.

## 9. Build order

1. Document model, docx and markdown readers, sentence splitting, the finding record, JSON and markdown report with *Not checked by this tool*. Smoke test on the PSJ draft.
2. Add ids to the appendix. Table loader, regex rows, B9.5 skip-list first, Module A rows. First false-positive count per rule.
3. Dependency-parse sentence checks (1.3), paragraph checks (1.4), format (1.7), views (1.6).
4. Soft checks (1.5) with the labelling workflow: a command samples sentence pairs with all three scores to CSV; label link / no link; a second command picks the F1-best cut.
5. Calibration pass (§5). A stats command reports the share of sentences each rule flags and warns above 30 %. Re-grade severity in the markdown, not in code.
6. The page (§7) and `decisions.json`.
7. `apply` (1.10), then 1.9, then docx comments.
