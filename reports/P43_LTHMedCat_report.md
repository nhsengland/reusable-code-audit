# Audit Report: P43_LTHMedCat

## Overview
P43_LTHMedCat (nhsengland, Wave 4) is a mostly-notebook project applying MedCAT
(CogStack) for clinical coding/NER on Leeds Teaching Hospitals neurology letters,
mapping text to SNOMED/ICD-10 with negation detection via negspacy. The repo is
four stripped Jupyter notebooks plus a single shared `notebooks/common.py`
holding the reusable Python; there is no installable package, no `src/`, and no
tests. Logic lives inline in notebook cells.

## SUL Adherence: Low
Almost all substantive code is embedded in notebook cells with hardcoded paths
and dataset filenames; `common.py` is the only factored module and it mixes a
catch-all `common_imports()` (an anti-pattern that imports ~15 libraries inside a
function) with genuinely reusable MedCAT setup/annotation helpers. Structural,
Utility and Logic concerns are not separated; reproducibility depends on local
`dir_root`-relative paths to specific model packs and CSV extracts.

## Extraction Candidates
No standalone extraction folder is created for this repo: the only reusable
units (`common_setupConfig`, `common_initialiseCAT`, `annotate_single` in
`notebooks/common.py:31-103`) are tightly bound to the MedCAT API and are better
captured as part of the cross-repo clinical free-text overlap than extracted as a
generic utility. `common_imports()` (notebook import boilerplate) is the kind of
common ML scaffolding to be handled centrally, not extracted. Flagged in the
signal matrix instead.

## Hardcoding Flags
- Dataset path: `dir_root + '/data/raw/neurology_letters_2023_03_18.csv'`
  (`01.1_..._stripped.ipynb` cell, `02_aa_annotation_stripped.ipynb` cell 26) —
  a specific dated trust extract.
- Model pack path:
  `models/mc_modelpack_snomed_int_16_mar_2022_25be3857ba34bdd5/{vocab.dat,cdb.dat}`
  (`02_aa_annotation_stripped.ipynb` cells 3-4) — magic-dated SNOMED model pack.
- Output paths with embedded dates: `data/interim/Annotated_Public/2023_05_15_*`
  (cells 157, 248).
- `negspacy` termset hardcoded to `"en_clinical"` (`common.py:66`); spaCy
  disabled-components list hardcoded then overwritten to `[]` (`common.py:38-52`).
- Credentials loaded via `dotenv` (`common.py:3-5`); no plaintext secrets found.

## Deduplication Candidates
- **Clinical free-text cleaning / NLP setup** — `evidence/deduplication_clinical_free_text_cleaning/`.
  `common.py` spaCy/MedCAT lowercase-tokenise-stopword + negation pipeline
  overlaps the spaCy tokenisation in nlp_renal_biopsy (`preprocessing/eda.py`)
  and the quanteda cleaning in stm-survey-text (`R/main/functions.R`). Partial,
  cross-library overlap of the same preprocessing recipe.
