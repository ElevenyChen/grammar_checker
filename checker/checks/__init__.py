"""Parse-based, paragraph, soft, format and view checks (scope 1.3–1.7). Each module exposes
`run(doc, config) -> list[Finding]` (or `-> list[View]` for views). None of them reads the
appendix; their rule_ids are fixed here and listed in CLAUDE.md."""
