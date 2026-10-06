"""Sentence segmentation and parse attachment (scope 1.0).

segment(doc, config, nlp=None):
- Load spaCy config.models.spacy once (module cache) unless `nlp` is given, and add the
  `boundary_guard` component before the parser.
- One spaCy Doc per body paragraph (not headings, not references, not the title block):
  Sentence.span = paragraph.span.start + sent.start_char .. + sent.end_char.
- boundary_guard forbids sentence starts (is_sent_start = False, which the parser respects):
  * after any token that is not terminal punctuation (. ? ! …, optionally followed by a closing
    quote or bracket). spaCy otherwise splits after "H2:", "OR =", or a comma.
  * after abbreviations: et al., e.g., i.e., vs., cf., Fig., Figs., p., pp., No., Eq., ca., approx.
    (spaCy tokenizes some as "al" + "." and some as "e.g."; both shapes are handled)
  * inside open parentheses or brackets, up to MAX_PAREN_TOKENS tokens (guards against an
    unclosed parenthesis swallowing the paragraph)
Mutates doc in place.
"""
from __future__ import annotations

from spacy.language import Language

from checker.config import Config
from checker.model import Document, Sentence, Span

_NLP: dict[str, object] = {}

ABBREV = {"al", "e.g", "i.e", "vs", "cf", "fig", "figs", "p", "pp", "no", "eq", "eqs", "ca", "approx", "resp"}
TERMINAL = {".", "?", "!", "…"}
CLOSERS = {'"', "”", "’", "'", ")", "]"}
OPEN = {"(", "["}
CLOSE = {")", "]"}
MAX_PAREN_TOKENS = 80


def _prev_word(doc, i: int):
    """Nearest non-space token before i, or None."""
    j = i - 1
    while j >= 0 and doc[j].is_space:
        j -= 1
    return doc[j] if j >= 0 else None


def _ends_sentence(doc, tok) -> bool:
    if tok.text in TERMINAL or (len(tok.text) > 1 and tok.text[-1] in ".?!"):
        return True
    if tok.text in CLOSERS:
        before = _prev_word(doc, tok.i)
        return before is not None and (before.text in TERMINAL or before.text[-1:] in (".", "?", "!"))
    return False


@Language.component("boundary_guard")
def boundary_guard(doc):
    depth = 0
    opened_at = 0
    for i, tok in enumerate(doc):
        if i == 0:
            continue
        prev = doc[i - 1]
        word = _prev_word(doc, i)
        if word is not None and not _ends_sentence(doc, word):
            tok.is_sent_start = False
        # abbreviation immediately before this token
        prev_word = prev.text.lower().rstrip(".")
        if prev.text.endswith(".") and prev_word in ABBREV:
            tok.is_sent_start = False
        elif prev.text == "." and i >= 2 and doc[i - 2].text.lower() in ABBREV and not doc[i - 2].whitespace_:
            tok.is_sent_start = False
        # parentheses
        if prev.text in OPEN:
            if depth == 0:
                opened_at = i
            depth += 1
        elif prev.text in CLOSE and depth > 0:
            depth -= 1
        if depth > 0 and i - opened_at > MAX_PAREN_TOKENS:
            depth = 0
        if depth > 0:
            tok.is_sent_start = False
    return doc


def load_nlp(config: Config):
    name = config.models.spacy
    if name not in _NLP:
        import spacy
        nlp = spacy.load(name)
        if "boundary_guard" not in nlp.pipe_names:
            nlp.add_pipe("boundary_guard", before="parser")
        _NLP[name] = nlp
    return _NLP[name]


def segment(doc: Document, config: Config, nlp=None) -> None:
    if nlp is None:
        nlp = load_nlp(config)
    elif "boundary_guard" not in nlp.pipe_names:
        nlp.add_pipe("boundary_guard", before="parser")

    paragraphs = doc.body_paragraphs()
    doc_index = 0
    for para, sdoc in zip(paragraphs, nlp.pipe(p.text for p in paragraphs)):
        para.sentences = []
        for sent in sdoc.sents:
            text = sent.text
            if not text.strip():
                continue
            span = Span(para.span.start + sent.start_char, para.span.start + sent.end_char)
            para.sentences.append(Sentence(
                index=len(para.sentences),
                doc_index=doc_index,
                text=text,
                span=span,
                paragraph=para,
                parsed=sent,
            ))
            doc_index += 1
    doc.meta["sentences"] = doc_index
