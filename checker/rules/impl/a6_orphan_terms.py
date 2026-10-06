"""A6 orphan terms (scope 1.4, appendix row A6): a term whose first occurrence is in Results or
later (Discussion, Limitations, Conclusion, Appendix) was never introduced where the reader
could learn it. One finding per term, at that first occurrence. Severity from the row (gate).

Two candidate kinds, both approximate (the row says so):
- capitalised runs: one or more consecutive capitalised tokens that are not sentence-initial and
  not inside a protected span ("Wayback Machine", "AIC", "Rules Widget"). First occurrence is
  searched case-sensitively, sentence-initial positions included.
- method bigrams: <word> + analysis/model/test/procedure ("bootstrapping analysis",
  "binomial test"), matched on lemmas so singular and plural count as one term. The modifier
  must be a content word that is not a generic adjective ("final model", "same test" are not
  terms).
Excluded: terms in the known-terms list (llm_polishing.md, "Known terms (A6 exemptions)"), terms
defined where they first appear ("OR = Odds Ratio", "Odds Ratio (OR)"),
months, display and section words, the draft's own heading texts ("Analytic Plan"),
H labels (protected), author names (protected). Hyphen and en-dash compounds are joined
("chi–square test", "signed–rank tests"), so a fragment is never reported as a term.
Drop rather than guess: a term that also occurs before Results in any case form is not flagged.
"""
from __future__ import annotations

import re

from checker.config import Config
from checker.findings import Finding
from checker.model import Document, Sentence, Span
from checker.rules import emit
from checker.rules.loader import RuleRow, known_terms
from checker.rules.registry import rule

HEADS = {"analysis", "model", "test", "procedure"}
GENERIC_MODIFIERS = {
    "same", "final", "full", "separate", "main", "primary", "secondary", "first", "second", "third",
    "additional", "following", "above", "further", "initial", "simple", "single", "current",
    "present", "overall", "basic", "alternative", "new", "previous", "original", "larger", "smaller",
    "two", "both", "each", "other", "our", "this", "that", "these", "those", "reverse", "combined",
}
DEFINED_BEFORE_RE = re.compile(r"(=|:)\s*$")
DEFINED_AFTER_RE = re.compile(r"^\s*(\([A-Z][A-Za-z]{1,7}\)|=)")


def _defined_here(text: str, a: int, b: int) -> bool:
    """'OR = Odds Ratio', 'Odds Ratio (OR)', 'AIC = …': the term is defined at this occurrence."""
    return bool(DEFINED_BEFORE_RE.search(text[max(0, a - 4):a]) or DEFINED_AFTER_RE.match(text[b:b + 12]))
EXCLUDE_WORDS = {
    "January", "February", "March", "April", "May", "June", "July", "August", "September",
    "October", "November", "December", "Table", "Tables", "Figure", "Figures", "Fig", "Appendix",
    "Section", "Note", "Panel", "Panels", "Part", "I", "Introduction", "Methods", "Method",
    "Results", "Discussion", "Conclusion", "Limitations", "Abstract", "Model", "Step",
}


def _protected(sentence: Sentence, start: int, end: int) -> bool:
    return any(p.start <= start and end <= p.end for p in sentence.protected)


def _tok_span(sentence: Sentence, tok) -> tuple[int, int]:
    base = sentence.paragraph.span.start
    return base + tok.idx, base + tok.idx + len(tok.text)


def _cap_runs(sentence: Sentence) -> list[str]:
    runs, cur = [], []
    first = sentence.parsed.start
    toks = list(sentence.parsed)
    for k, tok in enumerate(toks):
        a, b = _tok_span(sentence, tok)
        in_compound = (k >= 1 and toks[k - 1].text in DASHES and not toks[k - 1].whitespace_)
        ok = (tok.i != first and tok.is_alpha and len(tok.text) >= 2 and tok.text[0].isupper()
              and not in_compound
              and tok.text not in EXCLUDE_WORDS and not _protected(sentence, a, b))
        if ok:
            cur.append(tok.text)
        else:
            if cur:
                runs.append(" ".join(cur))
            cur = []
    if cur:
        runs.append(" ".join(cur))
    return runs


DASHES = {"-", "–", "‐"}


def _compound_start(toks, i: int) -> int:
    """Index of the first token of a dash compound ending at toks[i] ("chi–square" -> "chi")."""
    j = i
    while (j >= 2 and toks[j - 1].text in DASHES and not toks[j - 1].whitespace_
           and not toks[j - 2].whitespace_ and toks[j - 2].is_alpha):
        j -= 2
    return j


def _bigrams(sentence: Sentence):
    toks = list(sentence.parsed)
    for i in range(1, len(toks)):
        head, mod = toks[i], toks[i - 1]
        if head.lemma_.lower() not in HEADS:
            continue
        j = _compound_start(toks, i - 1)
        if j < i - 1:
            words = [t.text.lower() for t in toks[j:i] if t.text not in DASHES]
            modifier = "-".join(words)
        else:
            if (not mod.is_alpha or mod.is_stop or mod.lemma_.lower() in GENERIC_MODIFIERS
                    or mod.text.lower() in GENERIC_MODIFIERS):
                continue
            if mod.pos_ not in ("NOUN", "PROPN", "ADJ", "VERB"):
                continue
            modifier = (mod.lemma_ if mod.pos_ in ("NOUN", "PROPN") else mod.text).lower()
        a, _ = _tok_span(sentence, toks[j])
        _, b = _tok_span(sentence, head)
        if _protected(sentence, a, b):
            continue
        yield f"{modifier} {head.lemma_.lower()}", a, b


@rule("A6")
def orphan_terms(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    sentences = list(doc.sentences())

    # method bigrams: first occurrence by lemma pair, in document order
    first_bigram: dict[str, tuple[Sentence, int, int]] = {}
    for s in sentences:
        for term, a, b in _bigrams(s):
            first_bigram.setdefault(term, (s, a, b))

    # capitalised runs: candidates from mid-sentence positions, first occurrence anywhere
    headings = {p.text.strip().rstrip(".:").lower() for p in doc.paragraphs if p.is_heading}
    cap_terms: list[str] = []
    seen: set[str] = set(h for h in headings)
    for s in sentences:
        for run in _cap_runs(s):
            if run not in seen and run.lower() not in headings:
                seen.add(run)
                cap_terms.append(run)
    first_cap: dict[str, tuple[Sentence, int, int]] = {}
    lower_seen_before_results: set[str] = set()
    for term in cap_terms:
        rx = re.compile(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])")
        rx_any = re.compile(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", re.I)
        for s in sentences:
            m = rx.search(s.text)
            if m:
                a = s.span.start + m.start()
                first_cap[term] = (s, a, a + len(term))
                break
        for s in sentences:
            if s.section.kind.after_results:
                break
            if rx_any.search(s.text):
                lower_seen_before_results.add(term)
                break

    known = known_terms(config.paths.polishing)
    out: list[Finding] = []
    occurrences: dict[int, int] = {}
    hits = [(t, v) for t, v in first_cap.items() if t not in lower_seen_before_results]
    hits += list(first_bigram.items())
    for term, (s, a, b) in sorted(hits, key=lambda h: h[1][1]):
        if not s.section.kind.after_results:
            continue
        if term.lower() in known or _defined_here(doc.text, a, b):
            continue
        occ = occurrences.get(s.doc_index, 0)
        occurrences[s.doc_index] = occ + 1
        out.append(emit.finding(
            row, s, Span(a, b), occ,
            evidence=doc.text[a:b],
            suggestion=f"{row.note}: first use is in {s.section.name or s.section.kind.value}",
            extra={"term": term},
        ))
    return out
