# Audit Report: evalsense

## Overview
evalsense (nhsengland, Wave 8) is a Python package for evaluating LLM-generated
clinical text (e.g. summarisation of ACI-BENCH clinical dialogues). It is built
on `inspect_ai` and is the most mature, properly-engineered repo in this group:
a clean `evalsense/` package with separated `datasets`, `evaluation/evaluators`
(BLEU, ROUGE, BERTScore, G-Eval, QAGS), `generation`, `workflow/analysers`, a
`webui`, a CLI, typed config objects, tests, and CI. Structure is
package-first, not notebook-first.

## SUL Adherence: High
Concerns are cleanly separated. Structural code (pipeline/project/workflow
orchestration) is distinct from Utility helpers (`utils/files.py`,
`utils/text.py`, `utils/huggingface.py`, `utils/dict.py`) and from Logic
(individual evaluator scorers). Utilities are mostly generic and well
parameterised with docstrings and type hints. Hardcoding is minimal and routed
through `constants.py` and environment variables. This is the reference standard
for the batch.

## Extraction Candidates
- **Resumable, hash-verified file downloader** — `evidence/extraction_resumable_file_download/`.
  `utils/files.py` streaming download with retry, HTTP-range resume, and
  size/hash verification. Parameterise: replace the `USER_AGENT` /
  `DEFAULT_HASH_TYPE` constant imports with arguments to remove the package
  dependency.
- **LLM answer/score extraction helpers** — `evidence/extraction_llm_answer_extraction/`.
  `utils/text.py` `extract_ternary_answer` / `extract_score` / `extract_lines`.
  Parameterise: expose the ternary answer vocabulary; abstract the inspect_ai
  `ModelOutput` logprob access behind an adapter for the weighted variants.

## Hardcoding Flags
- `constants.py`: `APP_AUTHOR = "NHS"`, `USER_AGENT = "EvalSense/0"` — benign,
  centralised; overridable storage path via `EVALSENSE_STORAGE_DIR`.
- `dataset_config/ACI-BENCH.yml` and `datasets/managers/aci_bench.py` hardcode
  the ACI-BENCH dataset specifics — expected (logic), not tangled into utilities.
- No credentials, no local absolute paths, no magic dates found.

## Deduplication Candidates
- **LLM-as-a-judge boolean comparison** — `evidence/deduplication_llm_judge_comparison/`.
  evalsense's `extract_ternary_answer` and G-Eval scorer overlap with
  nlp_renal_biopsy's hand-rolled `use_llm_to_compare` substring-parse judge.
  evalsense's regex parser is the robust version the renal repo should reuse.
- Free-text handling: evalsense operates on already-clean clinical text and does
  not duplicate the survey/clinical token-cleaning recipe seen in the other
  three repos (noted for completeness; no shared evidence folder warranted).
