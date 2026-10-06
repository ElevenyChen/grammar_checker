"""Shared fixtures. Real spaCy is slow to load; tests that need it use the `nlp` fixture (session
scope) and are marked `slow`. Everything else uses the small markdown fixture."""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_md() -> Path:
    return FIXTURES / "sample.md"


@pytest.fixture
def polishing_md() -> Path:
    return Path(__file__).resolve().parents[1] / "llm_polishing.md"


@pytest.fixture(scope="session")
def nlp():
    spacy = pytest.importorskip("spacy")
    try:
        return spacy.load("en_core_web_lg")
    except OSError:
        pytest.skip("en_core_web_lg not installed")
