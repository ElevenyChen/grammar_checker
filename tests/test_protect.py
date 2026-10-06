import pytest

from checker.ingest.protect import spans_in

CASES = [
    ("contradict March et al.'s (2000) finding", ["March et al.'s (2000)"]),
    ("(March et al., 2000)", ["(March et al., 2000)"]),
    ("data (April to December 2020) here", []),
    ("(Lindblom 1959)", ["(Lindblom 1959)"]),
    ("(2018–2019)", []),
    ("(see Smith & Lee, 2019; Jones, 2020a)", ["(see Smith & Lee, 2019; Jones, 2020a)"]),
    ("Capano (2019) argues", ["Capano (2019)"]),
    ('called "problem absorption," here', ['"problem absorption,"']),
    ("see https://doi.org/10.1/x now", ["https://doi.org/10.1/x"]),
    ("H2a predicts", ["H2a"]),
]


@pytest.mark.parametrize("text,expected", CASES)
def test_spans(text, expected):
    assert [text[s.start:s.end] for s in spans_in(text, 0)] == expected


def test_base_offset():
    [s] = spans_in("Capano (2019)", 100)
    assert (s.start, s.end) == (100, 113)
