# Deduplication Overlap: LLM-as-a-judge boolean comparison

## Repos involved
- nlp_renal_biopsy — `src/evaluate/laaj.py` `use_llm_to_compare`
- evalsense — `evalsense/utils/text.py` `extract_ternary_answer` (+ G-Eval scorer)

## What overlaps (Partial / Tangled)
Both repos implement "ask an LLM a yes/no question, then parse the boolean reply".
- nlp_renal_biopsy prompts a model to judge whether two entity strings are
  equivalent and decides the result with a substring check (`"True" in
  response["response"]`). It hand-rolls provider branching for ollama and
  llama-cpp.
- evalsense provides a robust, regex-based ternary-answer extractor
  (`yes|no|true|false|unknown`) and a full G-Eval LLM-judge scorer
  (`evaluators/g_eval.py`) with logprob-weighted scoring.

## Shared vs bespoke
Shared: the LLM-judge pattern (prompt → call model → parse boolean/score).
Bespoke in nlp_renal_biopsy and tangled:
- The comparison prompt hardcodes `"You are a renal biopsy expert."` and the
  equivalence question.
- The model is hardcoded (`gemma2:2b`, `Phi-3.5-mini-instruct-Q5_K_M.gguf`).
- Provider dispatch (ollama / llama-cpp) is hardcoded inline.
- The boolean parse is a fragile `"True" in response` substring test that
  evalsense's `extract_ternary_answer` does properly.
nlp_renal_biopsy's judge would be far more robust reusing evalsense's parsing
and a parameterised prompt/model. This is the strongest within-group LLM-eval
overlap.
