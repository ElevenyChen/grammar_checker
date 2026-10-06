from checker.findings import finding_id, normalise


def test_id_is_stable_under_whitespace_and_case():
    a = finding_id("B1.1", "In order to  govern.")
    b = finding_id("B1.1", "in order to govern.")
    assert a == b and len(a) == 12


def test_id_differs_by_rule_and_occurrence():
    assert finding_id("B1.1", "x") != finding_id("B1.2", "x")
    assert finding_id("B1.1", "x", 0) != finding_id("B1.1", "x", 1)


def test_normalise():
    assert normalise("  A  b\n c ") == "a b c"
