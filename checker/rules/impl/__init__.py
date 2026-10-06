"""Python implementations for non-regex appendix rows. Importing this package registers them.
Ids must match the id column in llm_polishing.md once it is added (build step 2)."""
from checker.rules.impl import (  # noqa: F401
    a6_orphan_terms,
    a7_repeated_passages,
    b9_7_term_in_topic,
    b9_8_elegant_variation,
    b9_9_first_sentence_promise,
    misc_language,
    number_format,
)
