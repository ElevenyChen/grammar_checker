"""A7 repeated passages (scope 1.4, appendix row A7): a run of config.thresholds.ngram words
shared by two body paragraphs. "Flag both locations": one finding at each paragraph, each with
extra["other"] pointing at the other one and extra["pair"] grouping the two.

Words are the paragraph's alphanumeric tokens, lowercased; punctuation is ignored. A token
inside a protected span (citation, quotation, URL, H label) breaks the run, so a repeated
citation list is not a repeated passage. Overlapping shared windows merge into one run.
Severity from the row (gate).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from checker.config import Config
from checker.findings import Finding
from checker.model import Document, Paragraph, Sentence, Span
from checker.rules import emit
from checker.rules.loader import RuleRow
from checker.rules.registry import rule


@dataclass
class Word:
    text: str
    start: int
    end: int
    sentence: Sentence


def _words(p: Paragraph) -> list[Word | None]:
    """None marks a break (protected token)."""
    out: list[Word | None] = []
    base = p.span.start
    for s in p.sentences:
        for tok in s.parsed:
            if not (tok.is_alpha or tok.like_num):
                continue
            a, b = base + tok.idx, base + tok.idx + len(tok.text)
            if any(pr.start <= a < pr.end for pr in s.protected):
                out.append(None)
                continue
            out.append(Word(tok.text.lower(), a, b, s))
    return out


def _runs(starts: list[int], n: int) -> list[tuple[int, int]]:
    """Merge window starts into [first, last_word_exclusive) runs."""
    runs: list[list[int]] = []
    for i in sorted(set(starts)):
        if runs and i <= runs[-1][1]:
            runs[-1][1] = max(runs[-1][1], i + n)
        else:
            runs.append([i, i + n])
    return [(a, b) for a, b in runs]


@rule("A7")
def repeated_passages(doc: Document, row: RuleRow, config: Config) -> list[Finding]:
    n = config.thresholds.ngram
    paras = [p for p in doc.body_paragraphs() if p.sentences]
    words = [_words(p) for p in paras]

    index: dict[tuple[str, ...], list[tuple[int, int]]] = defaultdict(list)
    for pi, ws in enumerate(words):
        seen_here: set[tuple[str, ...]] = set()
        for i in range(len(ws) - n + 1):
            window = ws[i:i + n]
            if any(w is None for w in window):
                continue
            key = tuple(w.text for w in window)
            if key in seen_here:
                continue
            seen_here.add(key)
            index[key].append((pi, i))

    # pair (pa, pb) -> list of (start in pa, start in pb)
    pairs: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for occ in index.values():
        if len(occ) < 2:
            continue
        for x in range(len(occ)):
            for y in range(x + 1, len(occ)):
                (pa, ia), (pb, ib) = occ[x], occ[y]
                if pa != pb:
                    pairs[(pa, pb)].append((ia, ib))

    out: list[Finding] = []
    counter: dict[int, int] = defaultdict(int)

    def emit_at(pi: int, a: int, b: int, other: dict, pair_id: str) -> None:
        first, last = words[pi][a], words[pi][b - 1]
        span = Span(first.start, last.end)
        occ = counter[first.sentence.doc_index]
        counter[first.sentence.doc_index] += 1
        out.append(emit.finding(row, first.sentence, span, occ,
                                evidence=doc.text[span.start:span.end],
                                extra={"other": other, "pair": pair_id, "words": b - a}))

    for (pa, pb), starts in sorted(pairs.items()):
        offset = {ia: ib for ia, ib in starts}
        for a, b in _runs([ia for ia, _ in starts], n):
            ja = offset[a]
            jb = ja + (b - a)
            if jb > len(words[pb]) or any(w is None for w in words[pb][ja:jb]):
                jb = ja + n
            loc_a = {"paragraph": paras[pa].index, "section": paras[pa].section.name,
                     "start": words[pa][a].start, "end": words[pa][b - 1].end}
            loc_b = {"paragraph": paras[pb].index, "section": paras[pb].section.name,
                     "start": words[pb][ja].start, "end": words[pb][jb - 1].end}
            pair_id = f"{paras[pa].index}:{a}-{paras[pb].index}:{ja}"
            emit_at(pa, a, b, loc_b, pair_id)
            emit_at(pb, ja, jb, loc_a, pair_id)
    return out
