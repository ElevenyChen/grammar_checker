"""`checker label-pairs report.json --n 50 --out pairs.csv`: sample sentence pairs with their
three link scores (lemma, vector, encoder) from Report.stats["soft_link_pairs"], stratified across
the score range so the cut is well covered. CSV columns:
prev_sentence, cur_sentence, lemma, vector, encoder, label
`label` is empty; the human fills link / no-link (1 / 0). 40–60 pairs per the scope.
"""
from __future__ import annotations

from pathlib import Path


def run(report_path: Path, n: int, out: Path, seed: int = 0) -> None:
    raise NotImplementedError
