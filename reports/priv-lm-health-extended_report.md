# Audit Report: priv-lm-health-extended

## Overview
priv-lm-health-extended is a broader reworking of the privacy-in-clinical-LM agenda begun in
priv-lm-health (same research-group lineage). It covers MIMIC note ingestion
(`data_processing/`), memorisation measurement (`memorisation/`), a privacy-in-context
generation study (`privacy_in_context/`), and an attacker-LM experiment
(`misc/attacker_LM/`). It is better modularised than its predecessor — there are explicit
`base_datasets`, `utils`, and `config` modules and a `BaseDataset` abstraction — but it is
still a research codebase rather than an installable package, and it contains notable
internal copy/paste duplication (the `Pipeline` generation class appears twice).

## SUL Adherence: Medium
Concerns are partially separated: data ingestion, text-matching utilities, and generation
are in distinct modules, and the `MIMIC(BaseDataset)` pattern shows real structural intent.
However Utility is undermined by internal duplication (two near-identical `Pipeline`/`make_chunk`
copies) and by an absolute, machine-specific cache path baked into a module top-level. The
multi-provider `LLMGenerator` and the MIMIC merge/match utilities are the cleanest, most
extractable pieces.

## Extraction Candidates
- **Multi-provider LLM generator** — `evidence/extraction_multi_provider_llm_generator/`.
  Anthropic/OpenAI/HuggingFace facade behind one `generate(prompt) -> (text, stop_reason)`.
  Parameterise: refactor the closed `if/elif` provider dispatch into a handler registry; keep
  keys from kwargs/env. No model ids are hardcoded (good).
- **Batched HuggingFace generation pipeline** — `evidence/extraction_hf_batch_generation_pipeline/`.
  The `run_metrics.py` `Pipeline` (superset variant). Parameterise: `cache_dir` as an
  argument (currently `HF_HOME`); leave `make_prefix_suffix` behind as experiment logic.
- **MIMIC note merging & matching** — `evidence/extraction_mimic_note_merging/`. The III→IV
  rename map plus Aho-Corasick search / span-projection / scrunch helpers. Parameterise:
  decouple from `BaseDataset`/`config` imports; expose the rename map and match-column name.

## Hardcoding Flags
- **`CACHE_DIR = "/import/hf-cache/"`** in `misc/attacker_LM/run.py` — an absolute,
  machine-specific path assigned to `HF_HOME` at import time. Must become an env-var/argument.
- `cache_dir=os.environ["HF_HOME"]` and `os.environ.get("HF_HOME")` scattered across the
  generation and scoring modules — fine as a convention, but should be a single config knob.
- `mimir.py` `load_model_properties` special-cases model names containing `"silo"`/`"balanced"`
  and defaults `max_length=1024`.
- Generation defaults (`batch_size=48`, `temperature=0.9`, `top_k=50`, `top_p=0.9`,
  `max_new_tokens=200`) duplicated across both `Pipeline` copies.

## Deduplication Candidates
- **HuggingFace generation pipeline** — `evidence/deduplication_hf_generation_pipeline/`.
  **Internal** duplication: `Pipeline` + `make_chunk` are copy-pasted between
  `misc/attacker_LM/run.py` and `memorisation/run_metrics.py` (the latter a strict superset).
- **MIMIC notes loading** — `evidence/deduplication_mimic_notes_loading/`. Overlaps with
  **priv-lm-health** (`privlm/mi_attack.py`) — same MIMIC-notes loading intent, shared
  lineage, the deepest pairwise duplication in the batch.
- **Reference-model MIA scoring** — `evidence/deduplication_reference_model_mia_scoring/`.
  Overlaps with **priv-lm-health** (`privlm/mi_attack.py`): per-sequence likelihood/loss
  scoring (causal-LM LL / reference calibration here vs masked-LM PLL there).
- **MIMIC ingestion & standardisation** — `evidence/deduplication_mimic_ingestion_standardisation/`.
  The central five-repo case (with priv-lm-health, mm-healthfair, SynthVAE, txt-ray-align).
  This repo's `data_processing/base_datasets/mimic.py` rename map is nominated as the
  canonical notes-loader to lift into the proposed shared `mimic-tools` package.
