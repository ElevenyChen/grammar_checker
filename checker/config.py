"""Configuration (scope 1.0 sidecar). Loaded from checker.toml; every value has a default from the scope."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Paths:
    rules_dir: Path = Path(".")
    polishing_md: str = "llm_polishing.md"
    map_md: str = "scientific_writing_map.md"
    cache_dir: Path = Path(".checker_cache")

    @property
    def polishing(self) -> Path:
        return self.rules_dir / self.polishing_md

    @property
    def map(self) -> Path:
        return self.rules_dir / self.map_md


@dataclass
class Models:
    spacy: str = "en_core_web_lg"
    sentence_encoder: str = "all-MiniLM-L6-v2"


@dataclass
class Refs:
    crossref_contact: str = "you@example.edu"
    lookup_non_doi: bool = False
    title_sim_fail: float = 0.55
    title_sim_warn: float = 0.80


@dataclass
class Thresholds:
    subject_offset_words: int = 6
    subject_verb_gap: int = 8
    passive_run: int = 3
    short_paragraph: int = 2
    ngram: int = 8
    of_density_per_words: int = 12
    soft_link: float = 0.0        # 0 = unset; soft checks report but do not flag until tuned
    soft_outlier: float = 0.0
    soft_min_sentences: int = 4


DEFAULT_SECTION_NAMES: dict[str, list[str]] = {
    "abstract": ["abstract"],
    "introduction": ["introduction", "background"],
    "literature": ["literature review", "related work", "theory"],
    "methods": ["methods", "method", "data and methods", "materials and methods"],
    "results": ["results", "findings"],
    "discussion": ["discussion"],
    "limitations": ["limitations"],
    "conclusion": ["conclusion", "conclusions", "concluding remarks"],
    "appendix": ["appendix", "supplementary", "supplemental"],
    "references": ["references", "bibliography", "works cited"],
}


@dataclass
class Config:
    paths: Paths = field(default_factory=Paths)
    models: Models = field(default_factory=Models)
    refs: Refs = field(default_factory=Refs)
    thresholds: Thresholds = field(default_factory=Thresholds)
    sections: dict[str, list[str]] = field(default_factory=lambda: dict(DEFAULT_SECTION_NAMES))

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        """Read checker.toml if present. Unknown keys are ignored; missing keys keep defaults."""
        cfg = cls()
        if path is None:
            candidate = Path("checker.toml")
            path = candidate if candidate.exists() else None
        if path is None:
            return cfg
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        for section_name, target in (("paths", cfg.paths), ("models", cfg.models),
                                     ("refs", cfg.refs), ("thresholds", cfg.thresholds)):
            for k, v in data.get(section_name, {}).items():
                if hasattr(target, k):
                    cur = getattr(target, k)
                    setattr(target, k, Path(v) if isinstance(cur, Path) else v)
        if "sections" in data:
            cfg.sections.update({k: list(v) for k, v in data["sections"].items()})
        return cfg
