"""1.5 approximate checks, severity soft, reported in their own band. Step 2.

SOFT.LINK   old-before-new: subject phrase of sentence N vs last 3–4 content words of N−1.
            score = first of: lemma overlap (1.0) → spaCy vector similarity of the two phrases →
            sentence-encoder cosine of the two phrases. Flag when score < thresholds.soft_link.
            Until soft_link is set (0.0), emit nothing but write every pair's scores to
            Report.stats["soft_link_pairs"] so `checker label-pairs` can sample them.
SOFT.OUTLIER paragraph outlier: encoder embedding of each sentence vs paragraph centroid, paragraphs
            of >= thresholds.soft_min_sentences only. Report the minimum-cosine sentence with
            cosine and position; flag when below thresholds.soft_outlier. The outlier may be
            off-topic or may be the real message: the suggestion text says so.
No term dictionary (scope §4). Thresholds come from `checker tune` (calibrate/tune.py).
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document, Sentence

_ENCODER = None


def load_encoder(config: Config):
    raise NotImplementedError


def subject_phrase(sentence: Sentence) -> str:
    """Text of the subject subtree of the root clause."""
    raise NotImplementedError


def link_scores(prev: Sentence, cur: Sentence, encoder) -> dict[str, float]:
    """{'lemma': 0/1, 'vector': cos, 'encoder': cos}"""
    raise NotImplementedError


def run(doc: Document, config: Config) -> tuple[list[Finding], dict]:
    """Returns (findings, stats) so the pipeline can store pair scores for labelling."""
    raise NotImplementedError
