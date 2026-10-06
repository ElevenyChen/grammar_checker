# LLM Polishing — source table and audits

One source table, three views. Every row carries `step` and `severity`; the views are filters.

- **Module A — Claim audit** (After-drafting **Step 1**). Does the sentence say more than the evidence licenses? Tool lists hits with the sentence; human decides. Run before any language work.
- **Module B — Language** (After-drafting **Step 3**). Shorter, plainer, consistent. Run only after Steps 1–2 pass.
- **Cheatsheet extract**: rows with `severity = gate` that keep recurring.

**Severity rule (fixed — do not relax when adding rows):**
- `gate` — the advisor or co-author flagged it in the comment record, **or** the word changes claim strength / how the reader weighs evidence.
- `style` — only shorter or smoother. Reader's understanding does not change.

`action`: `replace` (mechanical), `delete`, `flag` (surface it; human judges). Sources: L = Lafferty pp. 11–21 · W = Williams (1990; page) · D = Doumont · A = advisor comments (date in `advisor_comments_digest.md`).

Status: Williams rows filled (Day 4). Test on the PSJ draft on Day 5 and re-grade severity by false-positive rate; B9.4, B9.8, B9.9 are the rows most likely to need it.

---

## Module A — Claim audit (Step 1)

### A1. Claim verbs: what each tier costs

A verb is a promise about the test behind it. Pick the tier the evidence paid for, not the tier that sounds like a contribution. [Lafferty p.2 evidence chain, read backwards; A: "Wait, do we demonstrate this?" 2024-10; "How do we know this? Just vibes?" 2025-05]

| Tier | Verbs | Evidence that licenses it |
|---|---|---|
| T0 describe | is / are / were, occurred, made up N%, most, the majority of | a descriptive statistic with count **and** denominator, at the stated level of analysis |
| T1 associate | is associated with, predicts, correlates with, varies with, is more likely to | a model coefficient with CI or *p*, covariates stated |
| T2 test | supports H, is consistent with H, fails to reject H₀, provides evidence for | the test that was assigned to that hypothesis in the Introduction — not an omnibus test standing in for it [A, Mako 2025-05] |
| T3 show | shows, demonstrates, establishes, confirms, reveals, validates | a direct test **and** the obvious alternative explanations addressed (statistical artefact, selection, denominator) [A, Mako: "Do we know this is not just a statistical feature?"] |
| T4 explain | explains, causes, drives, leads to, results in, produces | a causal identification strategy; otherwise downgrade to T1 with "consistent with a mechanism in which…" |
| T5 integrate | integrates, reconciles, unifies, synthesizes, bridges | a framework from which both theories' predictions follow, and a test of that framework — not two theories tested side by side [A, Mako 2024-11: "It just hypothesizes that both might be true"] |

Words that almost never get paid for in an observational paper: **prove, debunk, definitively**. Flag every occurrence.

Downgrade path when the evidence is short: T5 → "test side by side"; T4 → T1 + "consistent with"; T3 → T2; T2 → T0 + state the pattern.

### A2. Null hypotheses stated as hypotheses

An H that predicts *no difference / no interaction / constant proportion* cannot be supported, only not rejected. Label it H₀ and phrase the result as "fails to reject". [A, Mako 2025-05]
Pattern: `H\d[^.]*(no (systematic )?difference|does not (interact|differ)|remains? constant|independent of)`.

### A3. Citation verbs: match what the source did

| Verb | The source must have… |
|---|---|
| argues, claims, proposes, theorizes | taken a position (conceptual work) |
| finds, reports, observes | produced an empirical result |
| shows, demonstrates | run a test whose design supports that conclusion |
| defines, describes, distinguishes | given a definition or typology |
| notes, mentions, documents a case | said it once or as an example — do not generalize it [A, Mako 2025-12: Jhaver] |
| reviews, summarizes | secondary source; cite the primary if the claim is load-bearing |

Two checks the tool cannot do: (1) the sentence is actually in the source [A, Mako 2025-05: Ostrom 2009]; (2) the source's domain is the one you imply [A, Mako 2025-05: Givel and online communities]. Separate your synthesis from the cited claim in different sentences [A, Mako 2025-05].

### A4. Evaluation without evidence

`crucial, critical, essential, vital, important, significant (non-statistical), notably, interestingly, remarkably` — flag. Replace with the reason it matters, or delete. [L p.4 "without saying it is important"; A, Mako 2025-05 "You mention this as 'crucial' but…"]

### A5. Stacked hedges

Two hedges on one claim (`most … primarily`, `may often`, `can potentially`, `seems to suggest`) — keep one, ideally replace with the number. [A, Seth 2025-11]

### A6. Orphan terms

Any technical term, method, or named analysis whose first occurrence is in Results or Discussion — flag. [A, Mako 2025-05: bootstrapping; Doumont: jargon] Machine approximation: capitalized terms and words ending in *-ing analysis / model / test* that do not appear before the Results heading.

### A7. Repeated passages

Paragraphs with high n-gram overlap elsewhere in the manuscript (e.g. ≥ 8-word shared spans) — flag both locations. Repetition in one coding is noise, not effective redundancy. [D p.9, 11; A, Seth 2025-02, Mako 2025-05]

---

## Module B — Language (Step 3)

Human-readable grouping. The machine list is in the appendix.

### B1. Wordy phrases → short words [L pp. 16–21, pruned to social-science use]

`in order to → to · a number of → many · the (vast) majority of → most · due to the fact that / owing to the fact that / on account of → because · in the event that → if · prior to → before · subsequent to → after · at this point in time → now · on a daily basis → daily · in close proximity → near · approximately → about · a considerable amount of → much · whether or not → whether · despite the fact that / in spite of the fact that → although · in terms of → (delete or "about") · with regard to / with respect to → about · for the purpose of → for · in the absence of → without · has the capacity to → can · is able to → can · the question as to whether → whether · the fact that → (delete)`

### B2. Academic register → plain word [L]

`utilize → use · employ → use · elucidate → explain · facilitate → help/ease · methodology → method · demonstrate → show (style only; tier unchanged) · ascertain → find out · endeavor → try · initiate → begin · terminate → end · optimum → best · impact (verb) → affect · referred to as → called · evidenced → showed`

### B3. Delete-if-meaning-unchanged [L]

`very · actually · completely · totally · quite · basically · essentially (non-technical) · needless to say · it is important to note that · it should be emphasized that · it is worth pointing out that`
All `-ly` adverbs: flag; delete or replace with a specific. [L p.14]

### B4. Metadiscourse [L p.14; W pp. 40–41, 73]

`we found that X → X · we argue that · our initial hypothesis was that · these data might indicate · to conclude / in conclusion` — flag; usually delete the frame and keep the content. Exception: a frame that clarifies agency where agency matters (D p.68), and the conventional Intro/Conclusion announcements (*we show, we argue*) that Williams p.40 treats as normal. Sentence-**final** metadiscourse is a separate row (B9.6): it steals the stress.

### B5. Empty openers and buried main clauses [L; D p.65]

`It is … that …`, `There are/is …` at sentence start; `Figure X shows that [finding]` → `[finding] (Figure X)`. Flag. The message should be in the main clause. Exception per W p.34, 71: a *There is* that introduces the topic the next sentences develop is legitimate — check whether the following sentence picks up the noun.

### B6. Paragraph openers [L p.14]

First word of a paragraph in `First, Next, Then, After, Also, Another, In addition, Additionally` — flag; often a sign the paragraph's connection to the previous one is missing.

### B7. Advisor-specific [A]

| pattern | action | why | severity |
|---|---|---|---|
| evolve, evolution, evolving | replace → develop / change / development | co-author's standing objection; "evolve just means change" (Seth 2025-11, 2026-01) | gate |
| Institutional Layering Theory, Punctuated Equilibrium Theory (capitalized) | replace → lowercase; keep ILT / PET | not proper names (Mako 2025-05) | gate |
| downplay | replace → "treat as a threat to validity" | 2025-05 | style |
| "competing" (of PET and ILT) | flag | message-specific: the paper's claim is that they are not (Mako 2025-12) — manuscript-bound, remove row for other papers | gate |
| non-parallel phrasing across H1…Hn | flag (manual: diff the H sentences) | same frame, different construct (Seth 2025-11) | gate |
| Chi-squared / χ² mixed; dot vs underscore in variable names mixed | flag | consistency (Mako 2025-05; Seth 2025-12) | style |
| numbers: mixed thousands separators; leading zero missing where value can exceed 1 | flag | APA §6.36; Seth 2025-02, 2025-12 | style |

### B8. Clichés [L] — flag

`plays a role in · take-home message · tip of the iceberg · level playing field · cutting edge · window of opportunity · the bottom line · in this day and age · food for thought · viable alternative · meaningful dialogue · at the end of the day`

### B9. Williams — sentence position [W]

Principle behind every row: readers look for **characters in subjects, actions in verbs** (p. 21), **old information at the sentence start, new at the end** (p. 48), and **the paragraph's key words at the end of its first sentence** (p. 88). A row is `gate` only when the pattern changes what the reader reconstructs (a hidden causal link, two words for one concept, a paragraph that promises one theme and delivers another); the rest is `style`.

Hedge/intensifier calibration is not a Williams table — hedges stay in A5; intensifiers in A4/B3.

**Machine rows**

| id | pattern | action | severity | why | W |
|---|---|---|---|---|---|
| B9.1 | empty verb + nominalization: *conduct/perform/make/provide/carry out/undertake* + *an analysis / a comparison / an investigation / an assessment* | replace → the verb (*analyze, compare*) | style | the action is in the noun; the verb is doing nothing | p. 31 #1 |
| B9.2 | *There is/are* + nominalization (*There is a need for, There was a reduction in*) | flag → find the character, make it the subject; keep if the next sentence develops that noun | style | overlaps B5; this row adds the exception | p. 31 #2, p. 34 |
| B9.3 | nominalization as subject of an empty verb: *The intention/aim/purpose/expectation of X is/was* | replace → *X intends / aims / expects* | style | | p. 31 #3 |
| B9.4 | nominalization + *was due to / was because of / resulted from / was a consequence of / is attributable to* + nominalization | flag → split into two clauses joined by *because / if / although* | **gate** | the causal link is hidden in a preposition; rewriting exposes the alternative explanation (Mako: "you can't delete many rules if you don't have many") | p. 31 #5 |
| B9.5 | nominalization as subject that refers back (*This pattern, These results, The same asymmetry, Such a shift*) | **keep** — do not fire B9.1–B9.3 on it | — | it is doing cohesion work: compresses the previous sentence so this one can comment on it | p. 33 #1, p. 56 |
| B9.6 | sentence ends in metadiscourse: *…, as noted above / as shown earlier / as our analysis shows / it should be noted* | replace → move mid-sentence or delete | style | the stress position carries the reader's memory of the sentence; metadiscourse there is anticlimax | p. 73 |
| B9.7 | a term's first occurrence is in the first six words of its sentence | flag → rewrite so the term lands at the end, after familiar material | style | new terms belong in the stress, not the topic | p. 75 |
| B9.8 | ≥ 3 lexemes for one concept (manuscript list: *change / modification / revision / amendment*; *remove / delete / repeal*; *add / introduce / adopt*; *community / subreddit / group*) | flag → one term | **gate** | elegant variation: the reader assumes different words are different concepts | p. 87 |
| B9.9 | paragraph-initial sentence: its last 3–4 content words do not recur (or have no lexical relative) in the rest of the paragraph | flag (approximate; count false positives Day 5) | **gate** | the issue promised a theme the discussion does not deliver (Romanov) | p. 88, p. 94 |
| B9.10 | redundant pairs: *each and every, first and foremost, any and all, basic and fundamental, full and complete, true and accurate, various and sundry* | replace → first word | style | | p. 116 |
| B9.11 | redundant modifiers: *past history, end result, final outcome, future plans, consensus of opinion, completely finish, sudden crisis, advance planning, free gift* | delete the modifier | style | | p. 116 |

**Human rows** (not machine-checkable; run in Step 2 alongside the map's structure checklist — this is the Day 4 three-step diagnosis)

| id | check | how |
|---|---|---|
| B9.H1 | topic string | underline the first 5–6 words of every sentence (the subject of every clause); read only the underlined parts in a row. A subject outside the set must pick up the end of the previous sentence. [p. 23, p. 56] |
| B9.H2 | stress | circle the last 3–4 words of every sentence. Each must be new; none may be metadiscourse or a repeat of the previous sentence's words. [p. 48, p. 68] |
| B9.H3 | issue → discussion | the last 3–4 words of the paragraph's first sentence must name what the paragraph develops. If the paragraph feels unfocused, read its last two sentences first — the real theme is usually there; move it up. [p. 88, p. 95] |
| B9.H4 | active / passive | for a run of passives, ask: does the reader need the agent? is the subject string consistent? If yes/yes, keep the passive (Methods runs on *rules were coded…* legitimately). [pp. 37–39] |

---

## Appendix — machine view

Format: `id | step | severity | action | pattern | replacement`. Regex is case-insensitive unless noted. `flag` rows return the sentence; their last column is a note.
Ids follow the module sections above (A1–A7, B1–B9); `B.*` rows have no module section. A replacement with ` / ` offers candidates the human picks from. Ids are what reports, decisions and the calibration count key on: do not renumber a row, retire it.

Qualifiers at the end of the pattern column keep a row a regex and narrow it:
- `(case-sensitive)`: no re.I.
- `(paragraph start)`: only a paragraph's first sentence.
- `(verb)`: keep a hit only if a word in it is used as a verb (spaCy), not as a modifier: *established rules*, *growth–driven*, *communities established before* do not fire.
- `(adverb)`: keep a hit only if the word is tagged as an adverb: *likely*, *apply*, *family* do not fire.
A named group `(?P<hit>…)` sets the reported span when the pattern has to look at the whole sentence (A4.2). Any other prose in the pattern column means the row is implemented in Python under its id (`checker/rules/impl`).

Changes after the first false-positive count (2026-10-06, PSJ draft): A1.T3–T5 and B2.11 take `(verb)`; B3.3 takes `(adverb)` and skips restrictive adverbs (*only, nearly, exactly, roughly, partly*); A4.2 checks the whole sentence for a test or statistic, not only the text after the word; B.NOUNS moves from regex (any four words before the head) to a POS row.

```
A1.P      | 1 | gate  | flag    | \b(prove[sd]?|debunk(s|ed)?|definitively)\b                            |
A1.T3     | 1 | gate  | flag    | \b(demonstrat(e|es|ed)|establish(es|ed)|confirm(s|ed)|reveal(s|ed)|validat(e|es|ed))\b (verb) | T3 — check alternatives addressed
A1.T4     | 1 | gate  | flag    | \b(explain(s|ed)|caus(e|es|ed)|driv(e|es|en)|leads? to|results? in)\b (verb) | T4 — check causal design
A1.T5     | 1 | gate  | flag    | \b(integrat(e|es|ed|ing)|reconcil(e|es|ed)|unif(y|ies|ied)|synthesiz(e|es|ed)|bridg(e|es|ed))\b (verb) | T5 — check framework + test
A2        | 1 | gate  | flag    | \bH\d[^.]*(no (systematic )?difference|does not (interact|differ)|remains? constant|independent of) | label H0
A4.1      | 1 | gate  | flag    | \b(crucial(ly)?|critical(ly)?|essential(ly)?|vital(ly)?|important(ly)?|notabl[ey]|interestingly|remarkably)\b |
A4.2      | 1 | gate  | flag    | ^(?!.*(\bp\s*[<=>]|\bCI\b|\btests?\b|\bstatistic|χ²|=\s*[-–]?\.?\d)).*?\b(?P<hit>significant(ly)?)\b | non-statistical use (sentence reports no test or statistic)
A5.1      | 1 | gate  | flag    | \b(most|primarily|mainly|largely|generally)\b[^.]*\b(most|primarily|mainly|largely|generally)\b | stacked hedge
A5.2      | 1 | gate  | flag    | \b(may|might|can|could)\s+(often|potentially|possibly|sometimes)\b     | stacked hedge
A5.3      | 1 | gate  | flag    | \bseems? to (suggest|indicate)\b                                       |
A6        | 1 | gate  | flag    | first occurrence after "Results" of [A-Z][a-z]+ (analysis|model|test|procedure) | orphan term (approx.)
A7        | 1 | gate  | flag    | shared 8-gram between paragraphs                                       | repeated passage

B7.1      | 3 | gate  | replace | \bevol(ve|ves|ved|ving|ution)\b                                        | develop / change
B7.2      | 3 | gate  | replace | \b(Institutional Layering Theory|Punctuated Equilibrium Theory)\b (case-sensitive) | lowercase
B5.1      | 3 | gate  | flag    | ^(It is|There (is|are))\b                                              | empty opener (B5; see B9.2 exception)
B5.2      | 3 | gate  | flag    | \b(Figure|Table) \d+ (shows|illustrates|demonstrates|presents) that\b  | buried main clause
B9.4      | 3 | gate  | flag    | \b\w+(tion|sion|ment|ance|ence|ysis|ity)\b[^.]{0,40}\b(was|were|is|are) (due to|because of|a (consequence|result) of|attributable to)\b[^.]{0,40}\b\w+(tion|sion|ment|ance|ence|ysis|ity)\b | hidden causal link → two clauses
B9.4b     | 3 | gate  | flag    | \b(resulted from|stemmed from|arose from)\b (both sides nominalized)   | hidden causal link (variant)
B9.8a     | 3 | gate  | flag    | ≥3 of {change, modification, revision, amendment} in one section       | elegant variation
B9.8b     | 3 | gate  | flag    | ≥2 of {remove, delete, repeal} / {add, introduce, adopt} / {community, subreddit, group} in one section | elegant variation
B9.9      | 3 | gate  | flag    | paragraph-initial sentence: last 3–4 content words absent from rest of paragraph (stem match) | issue theme unmet (approx.)
B9.1      | 3 | style | flag    | \b(conduct|perform|make|provide|carry out|undertake|engage in)(s|ed|ing)?\s+(a|an|the)?\s*\w+(tion|sion|ment|ance|ence|ysis)\b | nominalization → verb
B9.2      | 3 | style | flag    | ^There (is|are|was|were) (a|an|no|some|little)?\s*\w+(tion|sion|ment|ance|ence|ysis)\b | keep if next sentence develops the noun
B9.3      | 3 | style | replace | ^The (intention|aim|purpose|expectation|goal) of (\w+) (is|was) to\b   | \2 intends to / \2 aims to / \2 expects to
B9.6      | 3 | style | flag    | (as (noted|shown|discussed|mentioned) (above|earlier|below|previously)|as our (analysis|results?|data) shows?|it should be noted)\.$ | sentence-final metadiscourse
B9.7      | 3 | style | flag    | defined term (from glossary list) whose first occurrence is within first 6 words of its sentence | term in topic position
B9.10     | 3 | style | replace | \b(each and every|first and foremost|any and all|basic and fundamental|full and complete|true and accurate|various and sundry)\b | first word only
B9.11a    | 3 | style | replace | \b(past|prior) history\b                                               | history
B9.11b    | 3 | style | replace | \b(past|prior) experience\b                                            | experience
B9.11c    | 3 | style | replace | \bend result\b                                                         | result
B9.11d    | 3 | style | replace | \bfinal outcome\b                                                      | outcome
B9.11e    | 3 | style | replace | \bfuture plans?\b                                                      | plan
B9.11f    | 3 | style | replace | \bconsensus of opinion\b                                               | consensus
B9.11g    | 3 | style | replace | \bcompletely finish\b                                                  | finish
B9.11h    | 3 | style | replace | \bsudden crisis\b                                                      | crisis
B9.11i    | 3 | style | replace | \badvance planning\b                                                   | planning
B9.5      | 3 | ---   | skip    | ^(This|These|That|Those|Such|The same) \w+(tion|sion|ment|ance|ence|ysis|ity|pattern|result|shift)\b | backward-referring nominalization: suppress B9.1–B9.3 on this sentence
B1.1      | 3 | style | replace | \bin order to\b                                                        | to
B1.2      | 3 | style | replace | \ba number of\b                                                        | many
B1.3      | 3 | style | replace | \bthe (vast )?majority of\b                                            | most
B1.4      | 3 | style | replace | \b(due to|owing to) the fact that\b                                    | because
B1.5      | 3 | style | replace | \bon account of\b                                                      | because
B1.6      | 3 | style | replace | \bin the event that\b                                                  | if
B1.7      | 3 | style | replace | \bprior to\b                                                           | before
B1.8      | 3 | style | replace | \bsubsequent to\b                                                      | after
B1.9      | 3 | style | replace | \bat this point in time\b                                              | now
B1.10     | 3 | style | replace | \bon a daily basis\b                                                   | daily
B1.11     | 3 | style | replace | \bin close proximity\b                                                 | near
B1.12     | 3 | style | replace | \bapproximately\b                                                      | about
B1.13     | 3 | style | replace | \ba considerable amount of\b                                           | much
B1.14     | 3 | style | replace | \bwhether or not\b                                                     | whether
B1.15     | 3 | style | replace | \b(despite|in spite of) the fact that\b                                | although
B1.16     | 3 | style | flag    | \bin terms of\b                                                        | delete or "about"
B1.17     | 3 | style | replace | \bwith (regard|respect) to\b                                           | about
B1.18     | 3 | style | replace | \bfor the purpose of\b                                                 | for
B1.19     | 3 | style | replace | \bin the absence of\b                                                  | without
B1.20     | 3 | style | replace | \b(has|have) the capacity to\b                                         | can
B1.21     | 3 | style | replace | \b(is|are|was|were) able to\b                                          | can / could
B1.22     | 3 | style | replace | \bthe question as to whether\b                                         | whether
B1.23     | 3 | style | flag    | \bthe fact that\b                                                      | delete
B2.1      | 3 | style | replace | \butiliz(e|es|ed|ing)\b                                                | use
B2.2      | 3 | style | replace | \bemploy(s|ed|ing)?\b(?= (a|an|the|data|method|model))                 | use
B2.3      | 3 | style | replace | \belucidat(e|es|ed)\b                                                  | explain
B2.4      | 3 | style | replace | \bfacilitat(e|es|ed)\b                                                 | help / ease
B2.5      | 3 | style | replace | \bmethodolog(y|ies)\b                                                  | method(s)
B2.6      | 3 | style | replace | \bascertain(s|ed)?\b                                                   | find out
B2.7      | 3 | style | replace | \bendeavou?r(s|ed)?\b                                                  | try
B2.8      | 3 | style | replace | \binitiat(e|es|ed)\b                                                   | begin
B2.9      | 3 | style | replace | \bterminat(e|es|ed)\b                                                  | end
B2.10     | 3 | style | replace | \boptimum\b                                                            | best
B2.11     | 3 | style | replace | \bimpact(s|ed)?\b (verb)                                               | affect
B2.12     | 3 | style | replace | \breferred to as\b                                                     | called
B3.1      | 3 | style | delete  | \b(very|actually|completely|totally|quite|basically)\b                 |
B3.2      | 3 | style | delete  | \b(needless to say|it is important to note that|it should be emphasized that|it is worth pointing out that)\b |
B3.3      | 3 | style | flag    | \b(?!(only|nearly|exactly|roughly|partly)\b)\w+ly\b (adverb)           | adverb: delete or replace with a specific
B4.1      | 3 | style | flag    | \bwe (found|find|argue|show|note) that\b                               | metadiscourse (mid-sentence; Intro/Conclusion announcements exempt)
B4.2      | 3 | style | flag    | \b(to conclude|in conclusion)\b                                        |
B4.3      | 3 | style | flag    | \bour (initial )?hypothesis was that\b                                 |
B6        | 3 | style | flag    | ^(First|Next|Then|After|Also|Another|In addition|Additionally)\b (paragraph start) |
B.OF      | 3 | style | flag    | \bof\b (density > 1 per 12 words)                                      | of-construction
B.NOUNS   | 3 | style | flag    | ≥3 nouns in a row before model / system / analysis / approach (POS)    | noun string
B.PASSIVE | 3 | style | flag    | \b(was|were|is|are|been) \w+ed by\b                                    | passive with agent — judge by B9.H4, not by count
B8        | 3 | style | flag    | \b(plays? a role in|take-home message|tip of the iceberg|level playing field|cutting edge|window of opportunity|the bottom line|in this day and age|food for thought|viable alternative|meaningful dialogue|at the end of the day)\b | cliché
B.WHILE   | 3 | style | flag    | \bwhile\b (non-temporal)                                               | although
B.SINCE   | 3 | style | flag    | \bsince\b (non-temporal)                                               | because
B.DIFF    | 3 | style | replace | \bdifferent than\b                                                     | different from
B7.3      | 3 | style | flag    | \bdownplay\b                                                           | "treat as a threat"
B7.4      | 3 | style | flag    | (Chi-squared|χ²) both present                                          | pick one
B7.5      | 3 | style | flag    | \d{4,}(?!,)  and  \d,\d{3}  both present                               | number format
B7.6      | 3 | style | flag    | (?<![\d.])\.\d+ where value can exceed 1                               | leading zero
```

Run order inside Step 3: B9.5 skip-list first, then gate rows, then style rows. Otherwise B9.1 fires on every *This analysis…* topic.

### Known terms (A6 exemptions)

Terms a reader of this paper is assumed to know. A6 never reports them as orphan terms. One term per line, matched case-insensitively. Keep it short: a missing entry only means one flag you would have seen anyway.

```
CI
SD
SE
COVID
COVID-19
```

---

## Cheatsheet extract (gate + recurs)

```
demonstrate / integrate / reconcile / confirm  → which test paid for this verb?
"most … primarily"                              → one hedge, or the number
crucial / essential / significant (non-stat)    → give the reason instead
evolve                                          → develop
a null stated as an H                           → H0, "fails to reject"
cited verb ≠ what the source did                → find / argue / note?
underline first 6 words of each sentence        → read them in a row; old at the start, new at the end
one concept, one word                           → change ≠ modification ≠ revision to a reader
```
