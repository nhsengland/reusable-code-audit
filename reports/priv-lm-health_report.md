# Audit Report: priv-lm-health

## Overview
priv-lm-health is a privacy-evaluation codebase for clinical language models: it
fine-tunes transformer models on MIMIC/i2b2 clinical notes and runs membership-inference
(MIA) attacks against them to measure training-data leakage. It is organised as a set of
task-oriented scripts (`downstream_tasks/`, `membership_inference/`, `privlm/`) rather than
an installable package — notebook/script-first, with experiment parameters threaded through
`argparse`/`typer` and module-level functions. It shares clear lineage with
priv-lm-health-extended (same research group; the "extended" repo is a later, broader
reworking of the same privacy-in-clinical-LM agenda).

## SUL Adherence: Low-to-Medium
Structure, Utility and Logic are tangled. The single `privlm/mi_attack.py` module mixes data
loading (`get_subject_ids`, `create_member_df`), generic sentence sampling
(`prep_mimic_for_MI`), model-scoring primitives (`return_loss`, `return_lr`), and the attack
evaluation maths (`return_auc_roc_over_alphas`, `calculate_results`) in one file with no
separation. Reusable helpers exist but are not isolated, and several carry latent bugs
(label arrays sized from the wrong population; a literal-`\s` cleaning regex). Hardcoding is
moderate but routed mostly through function arguments rather than scattered constants.

## Extraction Candidates
- **Membership-inference evaluation metrics** — `evidence/extraction_mia_evaluation_metrics/`.
  Threshold-sweep predictions + logistic-regression ROC-AUC + precision/recall/F1.
  Parameterise: accept named statistic arrays (drop the hardwired three-population shape);
  fix the label-length bug so populations need not be equal-sized.
- **Patient-level sentence sampling** — `evidence/extraction_patient_level_sentence_sampling/`.
  Patient-stratified, length-filtered, reproducible sentence pools from MIMIC DataFrames and
  i2b2 XML. Parameterise: column names, an explicit RNG/seed, and a `{subject_id: [text]}`
  core with thin per-source loaders.

## Hardcoding Flags
- `SUBJECT_ID` / `TEXT` column names hardcoded throughout `mi_attack.py`.
- Experiment magic numbers — `number_of_patients=90`, `number_of_sentences=4072`,
  `min_len_sentences=20` — as defaults, enforced by hard `assert len(...) == N` checks that
  crash on smaller corpora.
- `return_loss` hardcodes `max_length=256`, `padding="max_length"`.
- The clinical-text cleaner's whitespace regex is double-escaped (`r"\\s+"`) — matches a
  literal `\s+`, not whitespace.
- Uses the global `random` module (no seed threading) for shuffling.

## Deduplication Candidates
- **MIMIC notes loading** — `evidence/deduplication_mimic_notes_loading/`. Overlaps with
  **priv-lm-health-extended** (`data_processing/base_datasets/mimic.py`). Same intent —
  read MIMIC note CSVs into a subject/text working set — two implementations; the deepest
  pairwise duplication in the batch given the shared lineage.
- **Reference-model MIA scoring** — `evidence/deduplication_reference_model_mia_scoring/`.
  Overlaps with **priv-lm-health-extended** (`memorisation/mimir.py`): per-sequence
  likelihood/loss scoring (masked-LM PLL here vs causal-LM LL there).
- **HuggingFace Trainer boilerplate** — `evidence/deduplication_hf_trainer_boilerplate/`.
  Overlaps with **ELM4PSIR** (`run_lm_pretraining.py`): shared `TrainingArguments`/`Trainer`
  scaffolding (classification head here, LM pre-training there).
- **MIMIC ingestion & standardisation** — `evidence/deduplication_mimic_ingestion_standardisation/`.
  The central five-repo case (with priv-lm-health-extended, mm-healthfair, SynthVAE,
  txt-ray-align); priv-lm-health's `membership_inference/prepare_data_MIA.py` is one of the
  five independent MIMIC ingestion implementations to consolidate.
