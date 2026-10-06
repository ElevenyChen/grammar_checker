# Figure and Table Checklist

Run this on every main display during After-drafting Step 2 (see `scientific_writing_map.md`). It replaces `Figure_Graph_Table.docx`.

Source tags: [L] Lafferty pp. 7, 10 · [D] Doumont pp. 3, 13, 149 · [A] advisor comments (see `advisor_comments_digest.md`) · [APA] APA 7 §7.8–7.36. Rules tagged [A] are the ones the gate actually enforces.

---

## 0. The three-part contract

A display is three things that must each stand alone and must not depend on each other for anything essential:

```
TITLE     the claim        — what the reader should conclude
CAPTION   the instrument   — everything needed to read the display without the paper
TEXT      the argument     — claim + the one or two statistics that carry it + pointer
```

Test: could a reader recover the paper's motivation, findings, and interpretation from title + abstract + all figure/table captions alone? [A, 2025-04] If not, a caption is missing something. Could a reader follow the Results with every display deleted? [A, 2025-04] If not, the text is leaning on a display for evidence it should state.

Doumont's redundancy applies to the *message* (the claim appears in title and text), not to *information* (axis descriptions appear once, in the caption). [D]

---

## 1. Anatomy — which block is which

APA names the parts; the contract says what each part is for. Same anatomy, two title conventions.

### Table

```
Table 1                                   ← NUMBER   bold, own line
Rules Added Far Outnumber Rules Removed   ← TITLE    APA: italic, title case, label
                                                     house style: a claim sentence
──────────────────────────────────────────
              Additions      Deletions    ← COLUMN SPANNERS / DECKED HEADS   } HEADINGS:
Community     n     %        n     %      ← COLUMN HEADINGS (units, denominators)  every label
size (stub)                                ← STUB HEADING (what each row is)   } self-explanatory
──────────────────────────────────────────
  Small       12,431  74.2   4,318  25.8  ← BODY   numbers only; % always beside n
  Large        3,102  61.0   1,984  39.0
──────────────────────────────────────────
Note. Communities with ≥3 subscribers at   ← GENERAL NOTE  = the instrument (caption):
either snapshot, N = 130,851; April–         level of analysis, denominator, sample,
December 2020. Percentages are within        time frame, how to read cells, abbreviations,
row. Additions = rule present only in        the anomaly, key numbers not in the body
the second snapshot.
ᵃ Excludes 676 rules with edits < 5 chars. ← SPECIFIC NOTE   one cell / row / column
* p < .05. ** p < .01.                     ← PROBABILITY NOTE  thresholds only
```

### Figure

```
Figure 3                                   ← NUMBER
Younger Rules Are Deleted at More Than     ← TITLE   (same two conventions)
Twice the Rate of Older Rules
┌────────────────────────────────────────┐
│  [plot]                                │ ← IMAGE   axes labeled with meaning + units,
│   ● <1 yr   ○ ≥1 yr                    │           legend INSIDE the image decodes
│                                        │           symbols; large fonts; B&W-legible
└────────────────────────────────────────┘
Note. Bars = share of rules deleted by     ← GENERAL NOTE = the instrument: what is
rule age at first snapshot; error bars       plotted, encodings, uncertainty type,
= 95% CI. N = 26,939 changed rules in        level + denominator, sample, key numbers
6,948 communities. OR = 2.61, 95% CI         (the OR the reader cannot read off the
[2.40, 2.84]. The dip at age = 2 reflects    graphic), the anomaly explained
Reddit's 2018 rule-widget migration.
```

### Text (not part of the display)

```
Younger rules were removed far more often than older ones      ← CLAIM
(OR = 2.61, 95% CI [2.40, 2.84]; Figure 3).                    ← STATISTIC + POINTER
```
Never: "Figure 3 shows the distribution of deletions by rule age. The y-axis…" — that is Note content. [A, 2024-10]

### Where the claim goes: two conventions

| | Title | General note opens with |
|---|---|---|
| **House style** (advisor) [A 2025-04, 2026-01] | `**Figure 3. Younger rules are deleted at more than twice the rate of older rules.**` merged with the note, placed below the display | the description |
| **Strict APA** (if the journal enforces §7.10/§7.25) | italic label title above: *Rule Deletion by Rule Age* | **the claim sentence**, then the description |

Either way the claim exists in a place the reader sees before the numbers. Decide once per manuscript and check the target journal; do not let the template decide. [A, four rounds]

### Mapping to the checklist

| Block | Sections below | One-line test |
|---|---|---|
| Title | §3 | Could a reader disagree with it? |
| Headings + body | §2, §6 | Every label meaningful without the note; every % beside its n |
| General note | §4 | Title + abstract + notes → story recoverable |
| Specific / probability notes | §4, §8 | Cell-level facts and thresholds only, never the interpretation |
| Legend (in image) | §6 | Symbols decoded where the eye is |
| Text | §5 | Claim + statistic first, display second; no description |

---

## 2. Should this display exist?

- Every main claim has a display; every display exists because a claim needs it. [L p.10; A, 2025-02]
- Work backwards: claim → the comparison or relationship that would show it → the display that shows that comparison. If you cannot name the comparison, you do not have a figure yet. [L]
- A display the reader cannot connect to a claim is read as a main point and misleads. Ancillary displays go to an appendix. Methods or setting figures are the exception and may stay in the body. [L]
- Small amounts of data go in text, not a table. [L p.7]
- Related claims tested the same way share one figure with comparable panels. [A, 2025-02]

**Which form?**
- The relationship dictates the form: correlation → scatter; distribution → quantile or histogram; proportions across groups → table or bars with counts. [L]
- Show raw data where possible; add the regression line to make the point. [L]
- A chart asks to be compared visually, so the visual impression must match the numbers. If it cannot (log-scaled bars; differences that look small but are large), use a table. [A, Mako 2025-05; D p.13: the visual code prevails over the scale]
- A distribution the text refers to repeatedly should be visible, not described. [A, Mako 2025-05]

## 3. Title

- The title is a complete sentence stating the interpretation, not a label of the contents. "Rule additions are more common than deletions or alterations," not "Rule changes between snapshots." [D p.3 so-what caption; A ×4, 2024-10 to 2026-01]
- Test: could a reader disagree with the title? If not, it is a label.
- One title per display, one conclusion per title. If the display supports two conclusions, consider two panels or two displays.
- Under strict APA, the label title stays and the claim sentence opens the general note (see §1).

## 4. Note (caption)

The general note is the only place the display is described. Long notes are fine. [A, 2025-04] It should let a reader who has read only the title, abstract, and other notes understand and evaluate the display. Cover, in whatever order reads naturally:

- what is plotted or tabulated, and the level of analysis (communities? rules?) with the denominator stated
- sample and time frame
- how to read the encodings: axes, units, scale (log?), bars/boxes/whiskers, shading, symbols
- key numbers the reader cannot read off the graphic (exact percentages, modal values, effect sizes, CIs)
- any anomaly or feature the reader will notice — explain it rather than let them wonder [A, 2025-12]
- abbreviations and secondary notes (*p* thresholds, what the CI shading is)

Interpretation belongs here too, briefly: the sentence that says what the pattern means may be repeated from the text. [A, 2025-04]

APA order within notes: general → specific (superscript letters) → probability (asterisks), each starting a new paragraph. [APA §7.14]

## 5. Text

- State the claim, give the statistic that carries it, then point to the display. [A, 2025-04; APA]
- Never describe the display in the text. That is note content. [A, 2024-10]
- Never let the display be the only evidence for a claim. The text must carry the claim on its own. [A, 2025-04]
- Restate the hypothesis or question the display answers, at the point where it is tested. Readers do not remember. [A, 2025-04; Mako 2025-05]
- Refer to displays in numerical order. [L p.7]

## 6. Honesty of the graphic

- Uncertainty shown consistently: confidence intervals on all comparable bars or on none. [A, 2026-01] CIs (preferred) or SEs when the point is a comparison; SDs when the point is variability. [L p.10]
- A figure shows a pattern; it does not demonstrate significance. Do not write as if it does. [A, Mako 2025-05]
- Percentages always with raw counts; counts with their denominator. [A, 2024-10, 2025-04]
- Meaningful labels: "PC1 (fish body size)," not "PC1"; panels labeled by the comparison ("fished" / "unfished"), not (A)/(B). [L p.10]
- Legible in black and white; colour sparingly and never as the only carrier of meaning. [L p.10; D]
- Large fonts, bold lines; no decorative ink (3-D, gradients, gridlines that do not help). [L; D p.9]
- No screenshots. Rebuild tables as tables; strip embedded titles from plot images and put the title in the document. [A, 2025-04]

## 7. Sequence

- Main displays before supporting ones. [course]
- The main finding's figure gets cited where the main finding is argued, including in the Discussion. [A, 2025-02]

## 8. Format

- Statistics reported in APA 7 style (test statistic, df, *p*, effect size, CI); numbers formatted consistently throughout (thousands separators, decimals, leading zeros per APA §6.36). [A, 2025-02, 2025-12; APA]
- Model results in a proper APA table (predictor, *b*, *SE*, *z*/*t*, *p*, CI), not a regression printout. [A, 2025-04]
- Greek or spelled-out test names, one convention throughout. [A, Mako 2025-05]

---

## Run it

For each main display, answer yes to all:

1. Can I name the claim it supports and the comparison it shows?
2. Is the title a sentence a reader could disagree with (or, under strict APA, is that sentence the first line of the note)?
3. Does the note state level of analysis, denominator, sample, time frame, encodings, and any anomaly?
4. Does the text state the claim and its key statistic before pointing here?
5. Does the text avoid describing the display?
6. Are counts and denominators present wherever there is a percentage?
7. Is uncertainty shown, and shown the same way across comparable elements?
8. Would the visual impression survive if the reader ignored the axis numbers?
9. Is it referenced in order, and is the main figure cited where the main argument is made?
10. Is it built as a table or a proper plot, not a screenshot?
