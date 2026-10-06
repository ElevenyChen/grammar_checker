"""Rule table loader (build step 2). Marked xfail until the appendix has an id column and the loader
is implemented; the tests state the contract."""
import pytest

from checker.rules import loader


@pytest.mark.xfail(raises=NotImplementedError, strict=False)
def test_appendix_requires_ids(polishing_md):
    table = loader.load(polishing_md)
    ids = [r.id for r in table.rows + table.skip_rows]
    assert len(ids) == len(set(ids)), "rule ids must be unique"
    assert all(ids), "every row needs an id"


@pytest.mark.xfail(raises=NotImplementedError, strict=False)
def test_regex_rows_compile(polishing_md):
    table = loader.load(polishing_md)
    for r in table.regex_rows:
        assert r.compiled is not None, r.id


@pytest.mark.xfail(raises=NotImplementedError, strict=False)
def test_python_rows_have_implementations(polishing_md):
    from checker.rules import registry
    import checker.rules.impl  # noqa: F401
    registry.check_coverage(loader.load(polishing_md))


def test_non_regex_markers():
    assert not loader.looks_like_regex("≥3 of {change, modification} in one section")
    assert loader.looks_like_regex(r"\bin order to\b")
