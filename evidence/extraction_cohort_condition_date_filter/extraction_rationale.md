# Extraction Rationale: cohort_condition_date_filter

## What
`hypergraph-mm/hypmm/build_model.py` lines 21–204 (`filter_data`):

- Takes a wide DataFrame of individuals with `FIRST_<disease>` condition-onset
  date columns plus demographic/death columns, and applies a sequence of cohort
  filters: optionally remove residential breakers, drop individuals with any
  condition date earlier than a cut-off date, remove "healthy" individuals with
  no condition in the chosen disease set, and optionally restrict to individuals
  whose condition set is *exclusively* a subset of the chosen diseases.
- Returns the filtered condition-date DataFrame, a tidied demographic DataFrame,
  and a binary condition-flag matrix (`data_binmat`), with optional verbose
  progress/percentage-removed logging.

## Why it is reusable
Cohort construction by condition-onset dates, deprivation/demographic selection,
and conversion to a binary multimorbidity matrix is a recurring first step in
NHS/SAIL-style epidemiology and any disease-co-occurrence modelling. The filter
flags (remove-healthy, date cut-off, exclusivity, residency break) are generic
cohort operations; only the column naming ties them to this dataset. This is a
textbook Utility tangled inside a model-build module.

## Tangled bespoke logic to parameterise
1. **SAIL/Wales column names hardcoded**: `FIRST_<col>` prefix (lines 56, 163),
   death columns `["DOD", "ADDE_DOD", "ADDE_DOD_REG_DT", "COHORT_END_DATE"]`
   (line 61), demographic columns `GNDR_CD`, `AGE_AT_INCEPTION`,
   `WIMD2011_QUINTILE_INCEPTION`, `COHORT_END_DESC`, `COHORT_END_DATE` (lines
   62–68), and the rename targets `["SEX","AGE","DEPR",…]` (line 70). Parameterise
   the onset-column prefix, demographic-column map and death-column list.
2. **Magic sentinel string** `"Residency break"` used for the residential-break
   filter (lines 81, 84) — Wales-cohort-specific; should be an argument.
3. **`WIMD2011`** is the Welsh deprivation index — England equivalents use IMD;
   the deprivation column must be injected.
4. **`date_index` as a 3-tuple** `(y, m, d)` (lines 99–101) is an awkward API;
   accept a `datetime.date` directly.
5. **SettingWithCopy risk**: repeated `data[...]` slicing then column reassignment
   (lines 56–58, 182–183); behaviour must be preserved but tidied on extraction.
