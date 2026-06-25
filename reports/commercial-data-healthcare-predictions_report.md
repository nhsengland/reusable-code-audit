# Audit Report: commercial-data-healthcare-predictions

## Overview
commercial-data-healthcare-predictions predicts a local healthcare-demand count
(`cnt`) from commercial point-of-sale data (cold/flu OTC product sales) combined
with area-level covariates — IMD deprivation, demographics, housing, land use and
weather — using a random forest, and interprets it with Model Class Reliance (MCR)
including a grouped-feature variant. The audited surface (`MCR_for_op_rf.py`) is a
single linear script: assemble the feature matrix, fit/tune the forest, run MCR
and grouped MCR, save scores.

## SUL Adherence: Low
The file is a top-to-bottom modelling script with no function decomposition: the
feature list, group definitions, model fit, MCR call and CSV export are all
sequential side-effecting statements. The one genuinely reusable idea — grouped
MCR via a group→column-index mapping — is expressed as inline lists and a loop
rather than a function. Column names are hardcoded throughout. There is reusable
*method* here, but no reusable *unit* as shipped.

## Extraction Candidates
- **Grouped MCR / Rashomon variable importance** —
  `evidence/extraction_grouped_mcr_rashomon/`. Fit-then-MCR scaffold plus the
  `{group_name: column_indices}` construction for grouped reliance bounds.
  Parameterise: accept a `{group: [columns]}` mapping instead of the eight
  hardcoded lists; expose `random_state`/`num_times`/output path; remove the
  `[:45844]` row cap; document the dependency on a forest implementation exposing
  `plot_mcr`.

## Hardcoding Flags
- Hardcoded feature matrix: the ~56-column `X` list and target `'cnt'`
  (`MCR_for_op_rf.py:44-58`).
- Hardcoded feature groups: `sales_cols`, `imd_cols`, `age_cols`, `demo_cols`,
  `housing_cols`, `land_use_cols`, `weather_cols`, `week_col` and `grouping_names`
  — entirely PADRUS-dataset-specific.
- Magic row slice `[:45844, :]` capping training rows.
- Magic constants: `random_state = 42`, `n_jobs = -1`, `num_times = 10`.
- Hardcoded output path `"fake_outputs/mcr_padrus_scores.csv"`.
- Dataset name "padrus" embedded in output filename; deprivation columns
  (`imd_rank`/`imd_score`/`liv_env_score`/`crime_score`/`housing_score`) are
  LSOA/IMD-derived.
- No credentials found.

## Deduplication Candidates
- **Postcode → LSOA → IMD linkage** —
  `evidence/deduplication_postcode_lsoa_imd_linkage/`. This repo is the *downstream
  consumer* of LSOA/IMD deprivation features — its `imd_*` and `*_score` columns
  are exactly the output that **ProcessMining** produces via `produce_LSOA_IMD` and
  that **ESNEFT_diabetes_StephenRicher** obtains via `esneft_tools`. It shares the
  deprivation-feature contract rather than duplicating the linkage code itself.
- No other within-batch overlaps: the grouped-MCR method has no counterpart in the
  other four repositories.
