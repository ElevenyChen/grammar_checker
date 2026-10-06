"""1.7 format checks that are not appendix rows. Step 4, severity style.

F.THEORY   theory names capitalised mid-sentence ("Punctuated Equilibrium Theory") → lowercase;
           initialisms (PET, ILT) uppercase. The appendix has the manuscript-bound replace row;
           this one generalises on the pattern "<Cap> <Cap> Theory".
F.STATS    APA stats shape: p = .05 not p = 0.05; spaces around = and <; italic markers are not
           visible in text, so only spacing and leading-zero rules apply.
Citations vs reference list are in refs/orphans.py (1.9).
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding
from checker.model import Document


def run(doc: Document, config: Config) -> list[Finding]:
    raise NotImplementedError
