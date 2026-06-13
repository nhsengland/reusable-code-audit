# Extraction Rationale: icd9_to_icd10_ltc_mapping

## What
`mm-healthfair/src/utils/preprocessing.py` lines 25-239 (`preproc_icd_module`,
`get_ltc_features`) plus supporting helpers in `src/utils/functions.py` lines 168-190
(`read_icd_mapping`, `contains_both_ltc_types`):

- Maps ICD-9 diagnosis codes to ICD-10 via a mapping table (root-level 3-character matching,
  vectorised lookup dictionary), derived from the Gupta et al. MIMIC-IV-Data-Pipeline.
- Assigns each ICD-10 root to a long-term-condition (LTC) group from a JSON code dictionary.
- Builds patient-level multimorbidity features: per-LTC binary flags, count of unique
  conditions, multimorbidity / complex-multimorbidity flags at configurable cut-offs, and a
  physical+mental multimorbidity indicator.

## Why it is reusable
ICD-9 to ICD-10 harmonisation and LTC/multimorbidity flagging is a recurring need across NHS
data science (HES, SUS, GDPPR and MIMIC all carry mixed-version ICD coding). The LTC dictionary
is already externalised to JSON, and the multimorbidity definitions (count > 1, count > 3,
physical+mental) match common NHS definitions — this is a textbook Utility tangled inside a
project pipeline.

## Tangled bespoke logic to parameterise
1. **MIMIC column names hardcoded**: `"icd_code"`, `"icd_version"`, `"subject_id"`, `"hadm_id"`,
   `"seq_num"`, `"long_title"` (lines 77-98, 129-131, 195, 231). Parameterise code/version/id
   column names.
2. **Default relative paths**: `icd_map_path="../config/icd9to10.txt"`,
   `ltc_dict_path="../outputs/icd10_codes.json"` (lines 27, 30, 158) — note the two functions
   even default to *different* LTC dictionary paths; defaults should be removed and injected by
   the caller/config.
3. **LTC-type prefixes hardcoded**: `contains_both_ltc_types` assumes group names start with
   `"physltc_"` / `"menltc_"` (functions.py lines 188-189). Parameterise the prefix pair or
   accept two sets of group names.
4. **Mapping-file schema**: `read_icd_mapping` assumes tab-separated, `iso-8859-1`,
   with a `diagnosis_description` column (functions.py lines 172-173); `map_code_colname`
   default `"diagnosis_code"` is MIMIC-pipeline-specific.
5. **Per-row Python lambdas** (`.apply` in lines 92-107, 204-226) should be vectorised when
   extracted, but behaviour must be preserved first.
