# Scientific Writing Map

Course-level synthesis. Incomplete until Day 5.

> **Author design order ≠ reader presentation order.**
>
> **Design:** message → findings → details
> **Present:** motivation → message → details

Companion files: `figure_table_checklist.md` (display rules), `advisor_comments_digest.md` (evidence for Section D), `llm_polishing.md` (language audit, Steps 1 and 3), `cheatsheet.md` (desk reminder).

---

## Principles

### A. Message and selection [Doumont]

The paper exists to change what the reader thinks or does. Start from a one-sentence message, build 3–5 supporting claims, then reverse-select: keep only the findings necessary to establish, qualify, or challenge the message; cut everything else. "Necessary" includes nulls, boundary conditions, and contradictory evidence — a finding that limits the message belongs; a finding that merely happened does not.

```
                 MESSAGE   (so what)
                    |
          ---------------------
          |         |         |
       CLAIM 1   CLAIM 2   CLAIM 3    ≈3 per level
        /  \                 /  \
      info info            info info  (what)

          ↑
      reader sees the whole map
```

Why a tree: attention and working memory are limited. Group details under higher-level claims; keep few branches per level; a tree (choices + hierarchy) survives one weak branch where a chain (sequence) does not. Show the map so the reader always knows where they are, where they are going, and what the options are. Information = *what*; message = *so what*.

### B. Global component [Doumont: C/N/T/O/F/C/P]

The global component organizes the paper's motivation and outcome. The abstract compresses the whole sequence; sections of the paper expand different moves.

| Move | Question it answers | Who's asking |
|---|---|---|
| Context | Why now? What situation are we in? | Anyone |
| Need | Why you? What's the gap? | Readers |
| Task | Why me/us? What did we do? (past tense, *we*) | Authors |
| Object | Why this document? What does the paper cover? (present tense, *this paper*) | Document |
| Findings | What did we find? | Authors |
| Conclusion | So what does it mean for you? | Readers |
| Perspectives | What now? | Anyone |

Before = why the work was needed (Context, Need). Work = what we did (Task, Object). After = what we learned and what follows (Findings, Conclusion, Perspectives). The beginning tells readers why to enter; the end tells them what to leave with.

**Diagnostic:** if the abstract is missing the *after* → promissory. Missing the *before* → out of the blue. Missing need + conclusion → self-centered. A proposal is legitimately promissory: Seth's one-pager template ([1]–[9]) is Context–Need–Task–Perspectives with no Findings/Conclusion.

### C. Empirical-paper architecture [Lafferty]

**Evidence architecture:**
result/evidence → prediction or RQ → hypothesis/theoretical claim → central question.
Every major empirical result should have a role in that chain. Orphan results are candidates for deletion, appendix placement, or a different paper.

**Paper architecture:**
Problem → literature/gap → study context → hypotheses/RQs → predictions → methods → results → interpretation.
The Introduction establishes the question and expectations; Methods explains how they were tested; Results supplies the evidence; Discussion interprets what that evidence means.

**Paragraph/document architecture:**
Opening: hook → slant → problem.
Ordinary paragraph: topic → development → clincher.
Alternative document structures exist when audience/purpose changes.

**Figures** sit alongside the evidence architecture: claim → necessary comparison → display. Rules in `figure_table_checklist.md`.

`Seth's Writing Source.docx` is Lafferty pp. 4–7 verbatim; cite it as Lafferty.

### D. Advisor gate [from comment history — Day 3]

What the gate actually enforces, in order of how often it came up. Evidence, quotes, and recurrence in `advisor_comments_digest.md`.

1. **Level of analysis.** Every number says which level (community / rule) and which denominator. Rule-level evidence may support a community-level claim; it may not stand in for it.
2. **Rationale for every hypothesis, for and against**, built in the literature review, not bolted on in the H section. Mutually exclusive H's are one test, not a series.
3. **The reader remembers nothing and knows no theory.** Restate H/RQ where tested; hand-hold from "rules matter" to the specific theory.
4. **Plain words, parallel structure.** No weasel words, no euphemism, same sentence frame across parallel H's.
5. **Citations say only what the source says.** Separate your synthesis from the cited claim.
6. **No zombies, no rote repeats.** Every concept mentioned is paid off; nothing first appears in Results; no paragraph appears twice.
7. **Claims sized to evidence.** *Demonstrates, integrates, debunks* need a test that does that. A null is stated as a null.
8. **Content in the section that owns it.** Defence goes to Limitations, not Methods; interpretation to Discussion, not Results.
9. **Displays:** title is the claim; caption stands alone; text stands alone; percentages carry counts. → `figure_table_checklist.md`
10. **Format** (APA stats, numbers, capitalisation) → Step 4 / `llm_polishing.md`.

Flat-recurrence items (same error each round: 3, 9) go at the top of `cheatsheet.md`. Progressive items (1, 2) got finer each round and are better held in this map.

### E. Sentence and paragraph craft [Williams — Day 4]

Same premise as A–D at a smaller scale: the reader is not in the room, reads one sentence at a time, left to right. Williams answers one question — *where* in a sentence the reader expects *what*. Positions are fixed; what you put in them is the choice.

| Position (fixed) | Reader expects | Principle |
|---|---|---|
| subject | a character | 1. characters in subjects |
| verb | that character's crucial action | 2. actions in verbs |
| topic (sentence start) | old / familiar | 3. old before new |
| stress (sentence end) | new / important / what the next sentence picks up | 4. stress carries the point |
| issue (paragraph opening) | the paragraph's topic and theme words, in the stress of its last sentence | 5. the opening's stress promises the paragraph |
| discussion (paragraph body) | consistent topic string; theme words repeated, not varied | 6. one concept, one word |

Plus: the POINT sentence sits at the end of the issue or the end of the discussion; an opening paragraph's POINT sits at its end.

**Nominalization** (verb/adjective turned into noun: *compare → comparison*) is the main way 1–2 fail: the action hides in a noun, the verb goes empty (*was conducted*), the character disappears. Five mechanical patterns in `llm_polishing.md` B9.1–B9.4. Keep a nominalization only when it refers back to the previous sentence (*This pattern…*) or names a recurring concept (*layering*).

**Passive** is not a fault; it exists for cohesion. Choose by two questions: does the reader need the agent? is the subject string consistent? Methods can run on *rules were coded…* legitimately.

**Cohesion vs coherence.** Cohesion = each sentence picks up the previous sentence's end (the rope). Coherence = the paragraph delivers what its opening promised (the post the rope is tied to). A paragraph can have either without the other: the Romanov paragraph (Williams p. 88) is cohesive but promises *revolt* and delivers *succession*; three well-formed sentences on the same finding can be coherent but jump topics.

**Two pieces of advice Williams calls bad:** varying sentence openings to avoid monotony (p. 53); elegant variation (p. 87). For a bilingual writer the second is the trap — Chinese training rewards lexical variety, English scientific prose punishes it.

Why it comes last: these tools make any paragraph read smoothly, including paragraphs that should not exist. Run only after Steps 1–2.

Links to the other sections: 3–4 is Lafferty's topic–stress (p. 13) and Doumont's parallel/serial links (p. 63); the clincher works because the paragraph's last stress is the paragraph's stress; Seth's bossy caption is the figure's stress; *Figure 1 shows that [finding]* buries the finding in a subordinate clause.

---

## Before writing checklist

Stop before drafting if any load-bearing item is unresolved.

**Doumont:**
- Audience: Do I know who I'm writing for — and who the least specialized reader is?
- Message: Can I state the one sentence I want them to do or believe differently? (Not just what I found — what it means.)
- Tree: Do 3–5 main points support that message? If one weakens, do the others still stand?
- Selectivity: Starting from my conclusion, have I kept only the findings necessary to establish, qualify, or challenge it — including the nulls and limits — and cut the rest?
- Order: Am I organizing for the reader, not replaying my research chronology?
- Need: Can I name the gap between what exists and what's needed? (Not "X is important" — what's missing?)
- So what: Is it clear what the findings mean for the reader?
- Navigation: Can the reader tell where they are and where the paper is going?
- Abstract diagnostic: Does it have all seven moves? If not, which bad type — promissory, out of the blue, or self-centered?

**Lafferty:**
- Central question: Can all major findings fit under one question? If not, is this more than one paper?
- Evidence chain: For each major result, what prediction or RQ does it answer? What hypothesis does that prediction belong to?
- Orphan results: Does every major test/result have a role? If not — cut, appendix, or different paper.
- Enough evidence: Do I have enough coherent findings to support a paper yet?
- Paper architecture: Problem → lit/gap → context → hypotheses/RQs → predictions → methods → results → interpretation?
- Paragraph placeholders: Have I written topic-sentence and clincher placeholders before drafting?
- Opening: Hook → slant → actual problem, not a broad topic?
- Study context: Have I explained why this setting is the right place to answer the question?
- Predictions: Does each major test correspond to an expectation or RQ?
- Methods preview: Is it clear how the design tests those expectations?
- Results preview: Will the Introduction give the principal answer rather than withholding it?
- Figures: What comparison does each main claim require? Do planned displays match?

**Advisor:**
- Level: Is every hypothesis stated at the level the theory lives at? Do I know which numbers will be at which level?
- Rationale: Does the literature review build at least one argument for and one against each H?
- Reader: Have I written the hand-holding paragraph from "rules matter" to my theories?
- Zombies: List every concept I plan to introduce. Does each one have a place where it is paid off?

**Williams (pre-draft, p. 111):**
- Characters: Who are the 2–4 characters (real or abstract) most sentences will be about? That set is the topic string.
- Terms: One word per central concept, fixed before drafting — no synonyms later.
- Each topic-sentence placeholder: do its last 3–4 words name what the paragraph will develop?

---

## After drafting checklist

Revise from largest scale to smallest. Do not run language polishing until Steps 1–2 pass.

**Step 1 — Coherence and message:**
- Is the paper's most important question and most important result obvious throughout?
- Does the paper still carry the intended message? Is the reader-oriented order intact? Has the message drifted between title, abstract, Discussion opening, and Conclusion?
- Can the reader navigate — do they know where they are and where this is going?
- Does the abstract contain all seven moves?
- Is the so-what visible?
- Are claims sized to evidence? → Run `llm_polishing.md` Module A; human decides each hit.

**Step 2 — Structure and flow:**
- Does each section open by telling the reader what problem or task it addresses?
- Is every piece of content in the section that owns it (Methods says what was done; Limitations defends; Discussion interprets)?
- Does each paragraph have one coherent theme?
- Does each paragraph end on the point (clincher), not trail off?
- Does each paragraph make the next one feel expected?
- Is every H/RQ restated where it is tested?
- Does every citation say only what its source says?
- Is every concept introduced paid off later? Does anything first appear in Results?
- Do the main displays show the relationships that support the central claims?
- Paragraph flow, the Williams three-step (`llm_polishing.md` B9.H1–H3), on the paragraphs that feel off:
  1. Underline the first 5–6 words of every sentence; read them in a row. Do they form one topic string? A subject outside the set must pick up the previous sentence's end.
  2. Circle the last 3–4 words of every sentence. New information? Not metadiscourse, not a repeat?
  3. Do the last 3–4 words of the paragraph's first sentence recur in the paragraph? If the paragraph feels unfocused, read its last two sentences first — the real theme is usually there; move it up.
→ Run `figure_table_checklist.md` on each main display.

**Step 3 — Language tightening:**
→ Run `llm_polishing.md` Module B (B9.5 skip-list first, then gate rows, then style rows). Human accepts/rejects each suggestion.

**Step 4 — Proof:**
- Check citations match reference list.
- Check figure numbering and legends.
- Number formatting consistent; APA stats reporting; theory names lowercase, initialisms uppercase.
- Spellcheck / grammar check.
- Read hard copy for errors.
- Repeat until no errors found.
- Send out for comments, then revise and restart.

---

## Notes toward llm_polishing.md

Folded into `llm_polishing.md` on Days 3–4 (Lafferty → B1–B6, B8; Doumont → B5 and the figure checklist; advisor → A1–A7, B7; Williams → B9). Nothing left here.
