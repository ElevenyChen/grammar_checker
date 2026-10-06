"""1.3 sentence checks on the dependency parse. All step 2, module NONE unless noted.

rule_id   severity  check
S.SUBJ    style     subject head token more than N words from sentence start (thresholds.subject_offset_words)
S.OPEN    gate      "It is … that" / "There are …" openers (regex row exists too; this one adds the
                    B9.2 exception: skip if the next sentence's subject lemma is the noun introduced)
S.STRESS  style     last 3–4 content words are metadiscourse (lemma list) or repeat the previous
                    sentence's last content words
S.NOM     style     light verb (conduct/perform/make/provide/carry out/undertake/engage in) + object
                    noun with nominal suffix; skip when subject is a B9.5 back-reference
S.GAP     style     root verb index − subject head index > thresholds.subject_verb_gap
S.THIS    style     bare this/these as nsubj with no noun child
S.PASS    style     run of >= thresholds.passive_run consecutive passive sentences outside METHODS;
                    one Finding at the first sentence of the run, extra["run"] = length

Helpers below are shared with paragraph.py and soft.py.
"""
from __future__ import annotations

from typing import Any

from checker.config import Config
from checker.findings import Finding
from checker.model import Document, Sentence

METADISCOURSE_LEMMAS = {"note", "show", "discuss", "mention", "above", "earlier", "below", "previously",
                        "analysis", "result", "data", "paper", "study", "section"}
LIGHT_VERBS = {"conduct", "perform", "make", "provide", "carry", "undertake", "engage"}
NOMINAL_SUFFIXES = ("tion", "sion", "ment", "ance", "ence", "ysis", "ity")


def subject_of(sentence: Sentence) -> Any | None:
    """nsubj/nsubjpass token of the root clause, or None."""
    raise NotImplementedError


def root_of(sentence: Sentence) -> Any | None:
    raise NotImplementedError


def is_passive(sentence: Sentence) -> bool:
    """nsubjpass or auxpass on the root clause."""
    raise NotImplementedError


def stress_words(sentence: Sentence, n: int = 4) -> list[str]:
    """Lemmas of the last n content words."""
    raise NotImplementedError


def run(doc: Document, config: Config) -> list[Finding]:
    raise NotImplementedError
