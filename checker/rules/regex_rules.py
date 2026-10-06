"""Run regex rows over sentences (scope 1.1).

run(doc, table, config):
1. B9.5 skip set first: sentences whose start matches a skip row. B9.1–B9.3 do not fire there
   (a backward-referring nominalization such as "This analysis…" is doing cohesion work).
2. Gate rows, then style rows, over every body sentence. Anchors ^ and $ are sentence anchors.
3. Row qualifiers: `paragraph_start` rows test only a paragraph's first sentence.
   B4.1 ("we found that …") is exempt in Introduction and Conclusion, where the announcement is
   conventional (llm_polishing.md B4).
4. Part-of-speech qualifiers: a `(verb)` row keeps a hit only if a token in it is a verb that is
   not a modifier: spaCy dep amod / compound never count, and a reduced clause (acl) counts only
   when it names an agent ("patterns driven by the interplay", not "communities established
   before 2017"). An `(adverb)` row keeps a hit only if a token is ADV.
   A named group `hit` sets the reported span (A4.2 looks at the whole sentence).
5. Protected spans: a replace/delete hit is dropped if it overlaps any protected span (never
   edit a quotation or citation); a flag hit is dropped only if it lies wholly inside one
   (so "H1 … no difference" still fires A2, and a stacked hedge across a citation still fires).
6. Findings: replace/delete rows carry the rendered replacement, or `candidates` when the row
   offers a choice; flag rows carry the row note. occurrence counts hits of one rule in one
   sentence so ids stay distinct.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Action, Finding, Severity
from checker.model import Document, SectionKind, Sentence, Span
from checker.rules import emit, forms
from checker.rules.loader import RuleRow, RuleTable

SKIP_PROTECTS = {"B9.1", "B9.2", "B9.3"}
INTRO_CONCLUSION_EXEMPT = {"B4.1"}
EXEMPT_KINDS = {SectionKind.INTRODUCTION, SectionKind.CONCLUSION}
MODIFIER_DEPS = {"amod", "compound"}


def _pos_ok(sentence: Sentence, span: Span, pos: str) -> bool:
    base = sentence.paragraph.span.start
    for tok in sentence.parsed:
        a = base + tok.idx
        if not (a < span.end and span.start < a + len(tok.text)):
            continue
        if pos == "adverb" and tok.pos_ == "ADV":
            return True
        if pos == "verb" and tok.pos_ in ("VERB", "AUX") and tok.dep_ not in MODIFIER_DEPS:
            if tok.dep_ != "acl" or any(c.dep_ == "agent" for c in tok.children):
                return True
    return False


def skip_set(doc: Document, table: RuleTable) -> set[int]:
    """doc_index of sentences protected by B9.5."""
    out: set[int] = set()
    for row in table.skip_rows:
        if row.compiled is None:
            continue
        for s in doc.sentences():
            if row.compiled.search(s.text):
                out.add(s.doc_index)
    return out


def _blocked(sentence: Sentence, span: Span, row: RuleRow) -> bool:
    if row.action in (Action.REPLACE, Action.DELETE):
        return sentence.is_protected(span)
    return any(p.start <= span.start and span.end <= p.end for p in sentence.protected)


def run_row(sentence: Sentence, row: RuleRow, config: Config) -> list[Finding]:
    out: list[Finding] = []
    occurrence = 0
    for m in row.compiled.finditer(sentence.text):
        a, b = m.span("hit") if "hit" in m.re.groupindex and m.group("hit") is not None else m.span()
        if b == a:
            continue
        span = Span(sentence.span.start + a, sentence.span.start + b)
        if _blocked(sentence, span, row):
            continue
        if row.pos and (sentence.parsed is None or not _pos_ok(sentence, span, row.pos)):
            continue
        if row.action in (Action.REPLACE, Action.DELETE):
            cands = forms.render_candidates(row, m)
            if len(cands) > 1:
                f = emit.finding(row, sentence, span, occurrence, candidates=cands)
            else:
                f = emit.finding(row, sentence, span, occurrence, suggestion=cands[0])
        else:
            f = emit.finding(row, sentence, span, occurrence)
        out.append(f)
        occurrence += 1
    return out


def run(doc: Document, table: RuleTable, config: Config) -> list[Finding]:
    skipped = skip_set(doc, table)
    rows = sorted(table.regex_rows, key=lambda r: 0 if r.severity == Severity.GATE else 1)
    out: list[Finding] = []
    for sentence in doc.sentences():
        kind = sentence.section.kind
        for row in rows:
            if row.paragraph_start and sentence.index != 0:
                continue
            if row.id in SKIP_PROTECTS and sentence.doc_index in skipped:
                continue
            if row.id in INTRO_CONCLUSION_EXEMPT and kind in EXEMPT_KINDS:
                continue
            out.extend(run_row(sentence, row, config))
    return out
