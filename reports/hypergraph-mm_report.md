# Audit Report: hypergraph-mm

## Overview
hypergraph-mm (`hypmm` package) models multimorbidity as a directed hypergraph,
where nodes are diseases and hyperarcs encode disease-progression transitions.
The codebase is genuinely package-structured (`hypmm/build_model.py`,
`centrality_utils.py`, `utils.py`) with documented, single-purpose functions and
Numba-accelerated numerical kernels. Inputs are SAIL/Wales-style cohort extracts
(`FIRST_<disease>` onset dates, `WIMD2011` deprivation), but the analytical core
is mathematically generic. It is the most reusable of the five repositories in
this batch.

## SUL Adherence: High
Code is organised as an importable package with clear separation between cohort
construction (`build_model.filter_data`), combinatorial encoding (`utils.py`) and
centrality solvers (`centrality_utils.py`). Functions are documented with typed
INPUT/RETURNS docstrings and are mostly pure. The numerical modules carry no
dataset coupling at all. The only pull away from High is that `filter_data` hard
binds SAIL/Wales column names, and domain ("disease") naming is baked into
otherwise generic combinatorial/centrality utilities.

## Extraction Candidates
- **Directed-hypergraph centrality solvers** — `evidence/extraction_hypergraph_centrality_solvers/`.
  Degree/eigenvector/PageRank Numba kernels, irreducibility test and Brin–Page
  damping. Parameterise: rename `n_diseases`→`n_nodes`, expose the damping `alpha`
  (currently hardcoded `1 - 1e-6`); no dataset coupling otherwise.
- **Numba binary/powerset set-encoding** — `evidence/extraction_numba_binary_powerset_encoding/`.
  Integer↔binary set encoding, JIT powerset/worklist builders. Parameterise:
  neutralise `disease`-flavoured names, remove the `width=13` default, centralise
  the `-1` pad sentinel.
- **Cohort condition/date filter** — `evidence/extraction_cohort_condition_date_filter/`.
  `filter_data` cohort selection by onset date, residency break, exclusivity →
  binary matrix. Parameterise the `FIRST_` prefix and the demographic/death
  column maps; accept a `datetime.date` cut-off.

## Hardcoding Flags
- SAIL/Wales column names in `build_model.filter_data`: `FIRST_<disease>` prefix,
  death columns `["DOD","ADDE_DOD","ADDE_DOD_REG_DT","COHORT_END_DATE"]`,
  demographics `GNDR_CD`/`AGE_AT_INCEPTION`/`WIMD2011_QUINTILE_INCEPTION`/
  `COHORT_END_DESC`.
- Magic sentinel string `"Residency break"` as the residency-break filter value.
- `WIMD2011` (Welsh deprivation index) assumed — not portable to English IMD.
- `binary(num, width=13)` default width = 13 diseases (dataset-specific).
- Damping `alpha = 1 - 1e-6` and unused `alpha_ord=5` arg in
  `generate_irreducible_ptm`.
- No local file paths, trust/CCG codes or credentials found in the audited
  excerpts.

## Deduplication Candidates
- None within this batch. hypergraph-mm's contributions (centrality solvers,
  binary/powerset encoding, cohort filter) have no counterpart implementation in
  SynPath_Diabetes, ProcessMining, ESNEFT or commercial-data — they are unique
  extraction candidates rather than overlaps.
