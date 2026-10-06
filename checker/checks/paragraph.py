"""1.4 paragraph checks. Step 2.

rule_id    severity  symptom
P.OPEN     style     first sentence starts with a list/time word (B6 list; regex row covers the word,
                     this adds the paragraph-level framing)
P.CLINCH   style     last sentence is only a citation or a display reference ("(Figure 3)", "see Table 2")
P.META     style     last sentence ends in metadiscourse (sentence.stress_words ∩ METADISCOURSE_LEMMAS)
P.SHORT    style     paragraph has <= thresholds.short_paragraph sentences
A6 / A7 / B9.9 live in rules/impl because they are appendix rows.
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document, Paragraph


def is_display_reference_only(p: Paragraph) -> bool:
    raise NotImplementedError


def run(doc: Document, config: Config) -> list[Finding]:
    raise NotImplementedError
