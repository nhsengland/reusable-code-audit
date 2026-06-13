# Audit Report: stm-survey-text

## Overview
stm-survey-text (nhsx, Wave 2) is an R project that applies Structural Topic
Modelling (STM) to free-text survey/patient-feedback responses, with VADER
sentiment as a covariate. Code is organised into `R/main/` (a linear pipeline:
`libraries.R` → `preprocess.R` → `model.R` → `visOutputs.R`, with reusable
functions in `functions.R`) and `R/experiments/` (exploratory sentiment, ngram,
wordnet, and model-evaluation scripts). It is script-driven rather than packaged,
but `functions.R` does factor out named, documented functions.

## SUL Adherence: Medium
`functions.R` shows reasonable separation: generic-ish Utility functions
(`text_length`, `clean_text`, `convert_to_stm`, `sentAnalysis`, `lemmatiser`)
are pulled out of the `preprocess.R`/`model.R` orchestration scripts. The pull
toward Low is that those utilities hardcode this dataset's column names
(`data$Response`, `data$row_index`, `df$feedback`) and that much logic lives in
top-level script side-effects (`set.seed(1)`, plotting, `sapply(data, class)`)
rather than functions. The `experiments/` scripts are exploratory and largely
non-reusable.

## Extraction Candidates
- **Survey free-text cleaning pipeline (tangled)** — `evidence/extraction_free_text_cleaning_pipeline/`.
  `R/main/functions.R` `clean_text` + `convert_to_stm` + `lemmatiser`: the
  lowercase → expand-contractions → strip punctuation/digits/short-tokens →
  lemmatise → tokenise → remove-stopwords → trim-by-frequency recipe.
  Parameterise: pass text and id column names instead of hardcoded
  `data$Response` / `data$row_index`; keep `min_termfreq` and stopwords as args
  (already done).

## Hardcoding Flags
- Text column hardcoded `data$Response` and id `data$row_index` in `clean_text`
  (`functions.R:46-47`); `df$feedback` in `sentiment_analyses.R:19,45,63`.
- Data file paths: `here::here("data","text_data.csv")`
  (`sentiment_analyses.R:9`) and `data/trainsetwithsentiment.csv` referenced in
  the pipeline — committed survey data lives in `data/`.
- `set.seed(1)` and a fixed 1/20 train/test split in `preprocess.R:30-33` (random
  seed handled centrally, not an extraction candidate).
- "Criticality" variable outlier clamp to [-4, 4] noted as dataset-specific in
  `preprocess.R` comments — bespoke logic.
- No credentials found.

## Deduplication Candidates
- **Clinical / survey free-text cleaning** — `evidence/deduplication_clinical_free_text_cleaning/`.
  `clean_text` (R/quanteda) overlaps the spaCy tokenisation in nlp_renal_biopsy
  (`preprocessing/eda.py`) and the MedCAT/spaCy setup in P43_LTHMedCat
  (`notebooks/common.py`). Cross-language semantic overlap of the same
  lowercase→tokenise→remove-stopwords→frequency-matrix preprocessing recipe.
- VADER sentiment scoring (`functions.R` `sentAnalysis`, `sentiment_analyses.R`)
  is a generic text-analytics utility other healthcare survey/feedback projects
  would duplicate (noted; no within-group counterpart in this batch).
