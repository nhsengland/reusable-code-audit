# Audit Report: nlp_renal_biopsy

## Overview
nlp_renal_biopsy (nhsengland, Wave 7) is a Python project for LLM-assisted
named-entity extraction and annotation of renal histopathology reports. It uses
local LLMs (Ollama, llama.cpp) plus alternative models (GLiNER, spaCy, BERT-QA,
NuExtract) to fill a fixed entity schema from segmented reports, with Streamlit
annotation/comparison apps and an LLM-as-a-judge evaluation harness. Structure
is a `src/` package with ABC base classes (`QABase`, `MedicalReportProcessor`)
subclassed for the renal domain, plus a partly-separate `src/ner/` sub-project
with pydantic config and its own utils.

## SUL Adherence: Medium
Good use of abstract base classes to separate the generic processing skeleton
from renal-specific subclasses (`preprocessor_base` vs `preprocessor`,
`qa_base` vs `qa.py`). However Utility and Logic are frequently tangled:
utilities embed hardcoded models, prompts, file paths and the renal entity
schema; and there is internal duplication (two `load_json`/`save_json` pairs,
two `calculate_entity_accuracy` implementations). The `src/ner/` sub-project
duplicates utilities already present in `src/utils/`.

## Extraction Candidates
- **Robust JSON parsing of LLM output** — `evidence/extraction_robust_json_parsing/`.
  `src/utils/json.py` `parse_json_string` / `process_llm_response`. Parameterise:
  pass a `response_extractor` callable instead of the hardcoded llama.cpp
  envelope; make the key-repair regex optional.
- **Header-based clinical report segmenter (tangled)** — `evidence/extraction_medical_report_segmenter/`.
  `src/renal_biopsy/preprocessor.py` Levenshtein fuzzy header matching.
  Parameterise: inject canonical header list, distance threshold, pre-substitution
  map, specimen-keyword filter, and conclusion-splitting regexes (all currently
  hardcoded to renal biopsies).
- **Prompt-template load/validate/save helper** — `evidence/extraction_prompt_template_validator/`.
  `src/ner/src/config/prompt_template_handler.py`. Parameterise: drop the
  domain-specific wrapper functions; expose the JSON field name.

## Hardcoding Flags
- Models hardcoded in utilities: `gemma2:2b`, `gemma2:2b-instruct-fp16`
  (`evaluate/laaj.py`, `evaluate/report.py`), `models/Phi-3.5-mini-instruct-Q5_K_M.gguf`,
  `bert-base-nli-mean-tokens` (`evaluate/laaj.py:45,62`).
- Paths: `f"{root_dir}/data/guidelines.xlsx"` repeated across `qa_base.py:35`,
  `comparison_app.py:15`, `annotation_app_base.py:36`; `"../models"` download dir
  in `ner/src/utils.py:161`; `src/renal_biopsy/data/...` literals in
  `annotation_app_base.py:204`.
- Renal entity schema hardcoded: header list in `preprocessor.py:22`; JSON schema
  with renal entity names (`cortex_present`, `n_global`, …) in `renal_biopsy/qa.py:31-46`.
- NER config (`experimental_config.yaml`) hardcodes `county: 'West Yorkshire'`,
  `nhs number` identifier, specific HF repo IDs and GGUF filenames.
- Default system prompt `"You are a biomedical expert…"` embedded in `qa_base.py:20`.
- No plaintext credentials found (`.env` loaded via dotenv).

## Deduplication Candidates
- **JSON load/save helpers** — `evidence/deduplication_json_io_helpers/`.
  `src/utils/json.py` vs `src/ner/src/utils.py` — two near-identical
  `load_json`/`save_json` pairs within the repo.
- **Per-entity accuracy scoring** — `evidence/deduplication_entity_accuracy_scoring/`.
  `qa_base.py` `calculate_entity_accuracy` vs `evaluate/entity.py`
  `calculate_entity_accuracy` — same accumulate→percentage→print-table logic.
- **LLM-as-a-judge boolean comparison** — `evidence/deduplication_llm_judge_comparison/`.
  `evaluate/laaj.py` hand-rolled judge overlaps evalsense's robust
  `extract_ternary_answer` / G-Eval scorer.
- **Clinical free-text cleaning** — `evidence/deduplication_clinical_free_text_cleaning/`.
  `preprocessing/eda.py` spaCy tokenise/stopword recipe overlaps stm-survey-text
  (R quanteda) and P43_LTHMedCat (MedCAT/spaCy).
