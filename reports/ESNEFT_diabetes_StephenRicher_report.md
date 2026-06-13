# Audit Report: ESNEFT_diabetes_StephenRicher

## Overview
ESNEFT_diabetes_StephenRicher analyses diabetes care at ESNEFT (East Suffolk and
North Essex NHS Foundation Trust), combining a per-patient longitudinal summary of
clinical measures (HbA1c, BMI, GFR, etc.) with area-level deprivation analysis. A
key structural fact: the deprivation/demographic side **mainly wraps the external
`esneft_tools` package** (nhsx/p24-diabetes-inequal) — `download.getData`,
`process.getLSOAsummary`, `process.getGPsummary` do the heavy lifting. The repo's
own code (`scripts/utils.py`) contributes the patient summarisation, IQR outlier
removal, the diabetes measure vocabulary, and a couple of supplementary census
loaders.

## SUL Adherence: Medium
The bespoke `utils.py` does factor out named, documented functions
(`summariseByPatient`, `removeOutlier`, `load_english_language`,
`load_adult_skills`) with default vocabularies pulled out as module constants —
better than pure script. But these hardcode ESNEFT column names and CTV3
vocabularies throughout, `removeOutlier` ignores its own `threshold` argument, and
the deprivation workflow is a notebook (`deprivation-analysis.md`) of side-effects
over `esneft_tools`. Because the most reusable area-level work is delegated to an
external package, the repo's own reusable surface is modest.

## Extraction Candidates
- **Longitudinal measure patient summary** —
  `evidence/extraction_longitudinal_measure_patient_summary/`. `summariseByPatient`
  /`_summarise`/`removeOutlier`: per-patient first/last/mean/change, waits,
  appointment counts, IQR outlier nulling. Parameterise the measure/value/id/date
  column names and the measure vocabulary; fix the ignored `threshold` arg and the
  90-day magic span; replace `.head(1)[0]` with `.iloc`.
- **LSOA census indicator loaders** —
  `evidence/extraction_lsoa_census_indicator_loaders/`. `load_english_language` /
  `load_adult_skills`: parse `LSOA11CD:` census CSVs into per-LSOA proportions.
  Parameterise `skiprows`/`nrows`, numerator column indices and dtype map; collapse
  the two near-identical functions into one.

## Hardcoding Flags
- ESNEFT column names: `'CTV3Desc'`, `'RecordingValue'`, `'patientID'`,
  `'CodeEventDate'`, `'ReferralDate'`, `'RecodingLabel'` (typo for Recording).
- CTV3 vocabulary baked in: `CTV3Desc_rename` map and `measures` list; Type 1/2
  diabetes label lists `type1_default`/`type2_default`.
- Magic constants: IQR multiplier `3` (with the `threshold` arg dead-coded);
  90-day minimum span for change; sentinel strings `'Date of diagnosis'`,
  `'None'`.
- Census-CSV magic shape: `skiprows=11`, `nrows=34753` (count of 2011 English
  LSOAs); hardcoded numerator column indices `[3,4]` / `[0,1]`.
- Relative data paths in `deprivation-analysis.md`: `'../data/.data-cache'`,
  `'../data/HigherEducation-LSOA11.csv'`, `'../data/EnglishLanguage-LSOA11.csv'`.
- Trust scope: ESNEFT-specific extract; external dependency on `esneft_tools`
  (nhsx/p24-diabetes-inequal) for LSOA/GP deprivation summaries.
- No credentials found.

## Deduplication Candidates
- **Diabetes measure / observation vocabulary** —
  `evidence/deduplication_diabetes_measure_vocabulary/`. ESNEFT's CTV3 rename map
  and T1D/T2D label lists encode the same diabetes panel that **SynPath_Diabetes**
  declares as `observationsVars`/`conditionsVars`.
- **Postcode → LSOA → IMD linkage** —
  `evidence/deduplication_postcode_lsoa_imd_linkage/`. ESNEFT reaches LSOA-level
  IMD/deprivation via `esneft_tools`, the same destination that **ProcessMining**
  hand-rolls (`produce_LSOA_IMD`) and that **commercial-data-healthcare-predictions**
  consumes as deprivation features — consolidation here means adopting one
  canonical enrichment utility rather than literal code reuse.
