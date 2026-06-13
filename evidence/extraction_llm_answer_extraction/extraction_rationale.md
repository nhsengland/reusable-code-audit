# Extraction Candidate: LLM answer/score extraction helpers

## What it is
A family of parsing helpers from `evalsense/utils/text.py` that turn free-text
LLM output into structured values:
- `extract_lines` — split text into trimmed lines (strips bullets/list numbers)
  with an optional include filter.
- `extract_ternary_answer` — pull a yes/no/true/false/unknown answer via regex.
- `extract_score` — pull the first integer score within a min/max range.
(The accompanying logprob-weighted variants `extract_weighted_*` depend on
`inspect_ai.model.ModelOutput` and are more framework-coupled — see note below.)

## Why it is reusable (Utility)
Parsing an LLM's natural-language reply into a boolean, a category, or a numeric
score is a near-universal need in any LLM-as-a-judge or LLM-extraction pipeline.
nlp_renal_biopsy re-implements the same idea inline (`"True" in response`,
bespoke JSON regex parsing); a shared, regex-robust, range-checked implementation
would replace those fragile substring checks across LLM healthcare projects.

## What must be parameterised to untangle it
- `extract_ternary_answer`: the valid-answer vocabulary is hardcoded in the
  regex (`yes|no|true|false|unknown|i don't know`). Expose the answer
  vocabulary / mapping as an argument to support other label sets.
- `extract_score`: already parameterised by `min_score`/`max_score`; no change.
- The `extract_weighted_binary_answer` / `extract_weighted_score` functions are
  tied to `inspect_ai`'s `ModelOutput` logprob structure — to untangle, abstract
  the logprob access behind a small adapter (token, logprob) so they are not
  bound to the inspect_ai type.
