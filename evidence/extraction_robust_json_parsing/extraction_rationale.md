# Extraction Candidate: Robust JSON parsing of LLM output

## What it is
`parse_json_string` and `process_llm_response` from
`nlp_renal_biopsy/src/utils/json.py`. `parse_json_string` extracts the outermost
`{...}` substring from arbitrary LLM text, repairs unquoted keys with a regex,
and `json.loads` it. `process_llm_response` deep-copies a template dict and fills
only requested keys from the parsed response, swallowing parse errors gracefully.

## Why it is reusable (Utility)
LLMs frequently wrap JSON in prose or markdown fences and emit malformed keys.
Every LLM-extraction pipeline needs to recover a dict from such output. This is a
recurring problem across LLM healthcare repos (evalsense parses scores/answers;
the P43 MedCAT notebooks flatten model output to JSON). A shared "lenient JSON
recovery" helper is broadly valuable.

## What must be parameterised to untangle it
- `process_llm_batch` (same file) hardcodes the llama.cpp response shape
  `answer["choices"][0]["message"]["content"]` and a `use_llama_cpp` flag.
  Untangle by passing a `response_extractor` callable so the helper is not bound
  to one backend's envelope format.
- The unquoted-key repair regex is a heuristic; expose an optional "repair"
  toggle so callers can opt out for strict parsing.
- Otherwise `parse_json_string` is already domain-neutral.
