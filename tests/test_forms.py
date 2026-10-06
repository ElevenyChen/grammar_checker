"""Inflection and case for replace rows (scope 1.1), driven by fixtures/forms.csv."""
import csv
from pathlib import Path

import pytest

ROWS = list(csv.DictReader((Path(__file__).parent / "fixtures" / "forms.csv").open(encoding="utf-8")))


@pytest.mark.xfail(raises=NotImplementedError, strict=False)
@pytest.mark.parametrize("row", ROWS, ids=[r["before"] for r in ROWS])
def test_render(row, polishing_md):
    from checker.rules import loader, regex_rules
    table = loader.load(polishing_md)
    rule = table.by_id(row["rule_id"])
    m = rule.compiled.search(row["before"])
    assert m, f"{rule.id} should match {row['before']!r}"
    from checker.rules.forms import render
    assert render(rule, m) == row["after"]
