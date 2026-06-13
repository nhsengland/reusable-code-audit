# Audit Report: ELM4PSIR

## Overview
ELM4PSIR (Embedding Language Models for Patient Safety Incident Reports) is an NLP codebase
for pre-training and fine-tuning transformer models on free-text patient-safety incident
reports (CRIS-derived clinical notes). It spans language-model pre-training
(`language_modelling/`), downstream classification (`classification_tasks/`), and data
preparation (`utils/`). It is script- and class-first rather than an installable package,
with configuration carried through `argparse` and per-task data classes. It does not share
code lineage with the priv-lm-health repos, but it touches the same generic capabilities
(clinical-text cleaning, HuggingFace Trainer scaffolding).

## SUL Adherence: Low-to-Medium
There is some structural intent — a `LMTextData` config class, a `FewShotSampler`, a
Lightning `DataModule` — but Utility and Logic are entangled and there is conspicuous
**internal** duplication: the `clean_data` cleaning routine is copy-pasted verbatim across
two `utils/` modules. Reusable helpers (the few-shot sampler, the classification DataModule,
the cleaning recipe) are embedded in task scripts and coupled to project-specific column
names and label flags rather than isolated as parameterised utilities. Several latent
issues (unused `label_col`/`text_col` arguments not wired through, a literal-`\s` regex)
indicate copy-driven drift.

## Extraction Candidates
- **Few-shot, class-balanced sampler** — `evidence/extraction_fewshot_class_sampler/`.
  `FewShotSampler` (total- or per-label strategies, dev split, seeded). Parameterise:
  generalise `balance_dataset` away from the hardcoded `hospital_expire_flag` group column;
  resolve the dev-split TODO.
- **Clinical free-text cleaning** — `evidence/extraction_clinical_text_cleaning/`.
  `clean_data` (placeholder strip, replacement map, admin-token removal, normalise).
  Parameterise: text column, replacement map, admin-token list as arguments; fix the
  double-escaped `r"\\s+"` whitespace regex.
- **PyTorch Lightning text-classification DataModule** —
  `evidence/extraction_pl_text_classification_datamodule/`. `IncidentDataset`/`IncidentDataModule`.
  Parameterise: wire the stored-but-unused `label_col`, add `text_col`, rename to neutral
  names, raise the default `batch_size`.

## Hardcoding Flags
- `clean_data` whitespace regex double-escaped (`r"\\s+"`) — matches literal `\s+` (appears
  in both duplicated copies).
- `balance_dataset` hardcodes `groupby("hospital_expire_flag")` (MIMIC mortality flag) and
  takes a stray `self` despite being module-level.
- `IncidentDataset.__getitem__` hardcodes `data_row["text"]`/`data_row["label"]` while
  accepting (and ignoring) a `label_col` argument.
- `dataset_names_map` (`Key.PD09`→`severity`, etc.) and `max_token_len=512` /
  `mlm_probability=0.15` carried as literals in the data/Trainer config.

## Deduplication Candidates
- **Clinical note cleaning (internal)** — `evidence/deduplication_clinical_note_cleaning/`.
  **Internal** duplication: `clean_data` is copy-pasted between
  `utils/prepare_classification_datasets.py` and `utils/prepare_notes_for_lm.py` (only
  cosmetic differences). Consolidate to one shared cleaner.
- **HuggingFace Trainer boilerplate** — `evidence/deduplication_hf_trainer_boilerplate/`.
  Overlaps with **priv-lm-health** (`downstream_tasks/finetune_roberta_30dayReadmission.py`):
  shared `TrainingArguments`/`Trainer` scaffolding (LM pre-training here, classification
  fine-tuning there).
- **Free-text cleaning (cross-repo)** — `evidence/deduplication_free_text_cleaning/`.
  ELM4PSIR's `utils/preprocess_utils.py` overlaps with nlp_renal_biopsy and stm-survey-text:
  the same clinical/survey token-cleaning recipe reimplemented across repos.
- **Random-seed setting** — referenced in `evidence/deduplication_random_seed_setting/`
  (primary participants NHSSynth, SynthVAE): ELM4PSIR's seed-setting fits the same
  set-all-RNGs utility pattern noted there.
