"""The one record (scope 1.8) and its companions: Decision, NotChecked, Report.

`Finding.id` is a hash of rule_id + normalised sentence text, so a finding keeps its identity
across runs after unrelated edits and decisions can be re-attached.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from checker.model import Span


class Step(int, Enum):
    CLAIM = 1       # Module A
    STRUCTURE = 2   # 1.3–1.6 paragraph/sentence/soft/views
    LANGUAGE = 3    # Module B
    PROOF = 4       # 1.7 format, 1.9 refs


class Severity(str, Enum):
    GATE = "gate"
    STYLE = "style"
    SOFT = "soft"


class Action(str, Enum):
    REPLACE = "replace"
    DELETE = "delete"
    FLAG = "flag"


class Grade(str, Enum):
    WORD = "word"           # pure swap; batch-accept allowed per rule
    SENTENCE = "sentence"   # changes words outside the match (B9.3); one at a time


class Module(str, Enum):
    A = "A"
    B = "B"
    NONE = ""


class Choice(str, Enum):
    ACCEPT = "accept"
    SKIP = "skip"
    PICK = "pick"       # chose one of `candidates`; text in Decision.picked
    DELETE = "delete"   # one-key delete on flag rows that name deletion as an outcome
    SEEN = "seen"       # flag rows with nothing to accept


@dataclass
class Location:
    section: str
    section_kind: str
    paragraph: int
    sentence: int | None
    span: Span

    def as_dict(self) -> dict[str, Any]:
        return {"section": self.section, "section_kind": self.section_kind,
                "paragraph": self.paragraph, "sentence": self.sentence,
                "start": self.span.start, "end": self.span.end}


_WS = re.compile(r"\s+")


def normalise(text: str) -> str:
    return _WS.sub(" ", text.strip().lower())


def finding_id(rule_id: str, sentence_text: str, occurrence: int = 0) -> str:
    """Stable id: rule + normalised sentence (+ occurrence index when a rule hits one sentence twice)."""
    h = hashlib.sha1(f"{rule_id}|{normalise(sentence_text)}|{occurrence}".encode()).hexdigest()
    return h[:12]


@dataclass
class Decision:
    id: str
    rule_id: str
    location: dict[str, Any]
    evidence: str
    proposed: str | None
    choice: Choice
    picked: str | None = None
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


@dataclass
class Finding:
    id: str
    step: Step
    severity: Severity
    rule_id: str
    action: Action
    location: Location
    evidence: str                       # the matched text (or the sentence for flag rows)
    sentence: str                       # full sentence, for the report and for id re-attachment
    suggestion: str | None = None       # replacement text for replace/delete rows; note for flags
    candidates: list[str] = field(default_factory=list)  # pick rows
    module: Module = Module.NONE
    grade: Grade = Grade.WORD
    can_delete: bool = False            # flag rows whose rule names deletion as an outcome (-ly)
    score: float | None = None          # soft checks: cosine etc.
    decision: Decision | None = None
    extra: dict[str, Any] = field(default_factory=dict)  # second location for A7, counts, etc.

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["location"] = self.location.as_dict()
        d["step"] = int(self.step)
        for k in ("severity", "action", "module", "grade"):
            d[k] = getattr(self, k).value
        if self.decision:
            d["decision"]["choice"] = self.decision.choice.value
        return d


@dataclass
class NotChecked:
    """One line of the fixed 'Not checked by this tool' section (scope 1.8, §2, §3)."""
    stage: str      # "checker" | "window 1" ... | "human"
    item: str
    reason: str = ""


@dataclass
class View:
    """1.6 views: no judgment, just a table or list."""
    name: str       # "skeleton" | "hypotheses" | "numbers"
    rows: list[dict[str, Any]]


@dataclass
class Report:
    source: str
    generated_at: str
    findings: list[Finding]
    not_checked: list[NotChecked]
    views: list[View]
    stats: dict[str, Any] = field(default_factory=dict)   # per-rule counts, sentence totals (§5)
    module_a_cleared: bool = False                          # every gate A finding has a decision

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "generated_at": self.generated_at,
            "module_a_cleared": self.module_a_cleared,
            "findings": [f.as_dict() for f in self.findings],
            "not_checked": [asdict(n) for n in self.not_checked],
            "views": [asdict(v) for v in self.views],
            "stats": self.stats,
        }
