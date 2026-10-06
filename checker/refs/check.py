"""Orchestrates 1.9 into Findings. Step 4.

rule_id              severity  source
R.DOI_FAIL           gate      compare() FAIL: DOI resolves to a different paper / does not resolve
R.DOI_WARN           style     compare() WARN: metadata drift
R.UNCONFIRMED        gate      non-DOI entry with no bibliographic hit above title_sim_warn (opt-in)
R.NO_DOI             style     non-DOI entry when lookup_non_doi is off: manual checklist line
R.CITED_NOT_LISTED   gate      orphans.match
R.LISTED_NOT_CITED   style     orphans.match
R.NEAR_MISS          style     orphans.match
Location for entry findings: section=references, paragraph=entry index, sentence=None.
Appends NotChecked("human", "each citation says only what the source says", "§3").
"""
from __future__ import annotations

from checker.config import Config
from checker.findings import Finding, NotChecked
from checker.model import Document


def run(doc: Document, config: Config, online: bool = True) -> tuple[list[Finding], list[NotChecked]]:
    raise NotImplementedError
