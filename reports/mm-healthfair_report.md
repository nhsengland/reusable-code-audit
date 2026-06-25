# Audit Report: mm-healthfair

## Overview
mm-healthfair is a research codebase for multimodal fairness evaluation on
MIMIC-IV: it ingests the MIMIC-IV hospital and note data, builds static EHR plus
clinical-timeseries features, trains classifiers for in-hospital outcomes, and
evaluates them with bootstrapped fairness metrics across sensitive attributes
(gender, race group). The code lives in a structured `src/` package with a
`utils/` layer (`mimiciv.py`, `preprocessing.py`, `eval_utils.py`,
`fairness_utils.py`, `functions.py`), which is more disciplined than a
notebook-first project, but the utility modules are large and carry substantial
hardcoded MIMIC-specific configuration inline.

## SUL Adherence: Medium
Structure, Utility and Logic are partially separated. There is a real Structural
layer (`src/` with `prepare_data.py`/`extract_data.py` entry points and dataset
classes) and a recognisable Utility layer (`utils/`), which earns it above the
notebook-only repos. However, the Utility functions tangle genuinely reusable
logic with bespoke MIMIC specifics: `generate_train_val_test_set` embeds an
800+-line wall of display dictionaries, prescription-column lists and summary
reporting alongside the actual split; `mimiciv.py` bakes column/dtype lists and
the extended-stay outcome threshold into function bodies. Reusable helpers exist
but are not cleanly extractable without parameterisation, hence Medium rather than
High.

## Extraction Candidates
- **Bootstrapped fairness metrics** — `evidence/extraction_bootstrapped_fairness_metrics/`.
  `fairness_utils.py` (lines 80-201) bootstrap CI over subgroup performance gaps.
  Parameterise: pass the metric function, the sensitive-attribute column(s) and
  bootstrap count instead of assuming fixed MIMIC group columns.
- **Binary-classifier CI evaluation** — `evidence/extraction_binary_classifier_ci_evaluation/`.
  `eval_utils.py` (lines 190-341) bootstrapped confidence intervals for binary
  metrics. Parameterise: take y_true/y_score and a metric list as arguments,
  decoupled from the project's outcome naming.
- **Clinical timeseries interval builder** — `evidence/extraction_clinical_timeseries_interval_builder/`.
  `preprocessing.py` event-to-timeseries / time-elapsed builders. Parameterise:
  expose the timestamp, event and id column names rather than MIMIC defaults.
- **ICD-9 to ICD-10 / LTC mapping** — `evidence/extraction_icd9_to_icd10_ltc_mapping/`.
  `functions.py` / `preprocessing.py` diagnosis-code mapping. Parameterise: supply
  the mapping table and target vocabulary as inputs.

## Hardcoding Flags
- Output paths default to relative `../outputs/processed_data`,
  `../outputs/exp_data`, `../outputs/reference` (`prepare_data.py`).
- Dataset name **MIMIC-IV** baked into class/module names (`MIMIC4Dataset`,
  `mimiciv.py`) and ingestion column/dtype lists.
- Magic columns and outcome labels: `in_hosp_death` default outcome, `gender`,
  `race_group` as fixed stratification/sensitive columns; `ext_stay > 7 days`
  threshold; a large hardcoded `nn_cols` prescription list and `disp_dict`
  display map inside `generate_train_val_test_set` (the source itself flags
  `## TODO: would need to move this to an appropriate config file`).

## Deduplication Candidates
- **MIMIC ingestion & standardisation** — `evidence/deduplication_mimic_ingestion_standardisation/`.
  mm-healthfair's `mimiciv.py` is one of five repos independently implementing
  MIMIC ingestion; central case names priv-lm-health, priv-lm-health-extended,
  SynthVAE and txt-ray-align alongside it. Deepest pairwise tie: SynthVAE
  (both do column-type-driven tabular standardisation of MIMIC hospital data).
- **MIMIC free-text cleaning** — `evidence/deduplication_mimic_free_text_cleaning/`.
  `clean_notes` overlaps with **txt-ray-align**'s report cleaner on the shared
  whitespace-collapse recipe.
- **Train/val/test split with CSV export** — `evidence/deduplication_train_test_split_csv/`.
  `generate_train_val_test_set` overlaps with **txt-ray-align**'s `get_subset.py`.
- **Clinical text embedding** — `evidence/deduplication_clinical_text_embedding/`,
  with **txt-ray-align**.
- **Experiment config loading** — `evidence/deduplication_experiment_config_loading/`.
- **Random seed setting** — `evidence/deduplication_random_seed_setting/`.
