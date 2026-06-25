# Deduplication Case: Postcode → LSOA → IMD Deprivation Linkage

**What it does:** Takes a patient/incident record carrying a UK postcode and
enriches it with area-level deprivation: postcode is matched to a 2011 Lower
Layer Super Output Area (LSOA11CD) via an ONS postcode-to-output-area lookup,
then the LSOA is joined to the English Indices of Multiple Deprivation (IMD 2019)
scores/ranks/deciles. The end product is a record annotated with IMD decile and
sub-domain deciles (health, crime, income, education, barriers, etc.).

**Why it is an overlap:** Three (arguably four) repositories perform the same
postcode→LSOA→IMD enrichment, two of them with nearly identical code:

| Repo | File | Implementation |
|---|---|---|
| ProcessMining | `Notebooks/2_CADData_to_EVlog.ipynb` (Cells 20–36) | Downloads ONS `PCD_OA_LSOA_MSOA_LAD` lookup + IMD 2019 File 7, `fetch()` caching helper, `produce_LSOA_IMD(df)` merging on `Incident_Postcode`→`PCDS`→`LSOA11CD`→IMD deciles |
| ProcessMining | `Notebooks/Add_postcodes_to_LSOAs_and_IMD.ipynb` (Cells 4–7) | Same `fetch()` and `produce_LSOA_IMD(df)` — an almost verbatim sibling (differs only in `Incident Postcode` vs `Incident_Postcode`, source paths, and column casing) |
| ESNEFT_diabetes_StephenRicher | `scripts/deprivation-analysis.md` + `scripts/utils.py` (lines 299–331) | Obtains LSOA-level deprivation via the external `esneft_tools` package (`download.getData`, `process.getLSOAsummary`) and supplements with `load_adult_skills` / `load_english_language` LSOA11 census loaders |
| commercial-data-healthcare-predictions | `MCR_for_op_rf.py` (lines 44–58) | Consumes the *output* of this linkage — features `imd_rank`, `imd_score`, `imd_extent`, `liv_env_score`, `crime_score`, `housing_score` are LSOA/IMD-derived deprivation columns |

ProcessMining's two notebooks are a near-literal internal duplication. ESNEFT
reaches the same destination (LSOA-level IMD/deprivation) but delegates the heavy
lifting to the `esneft_tools` package and only hand-rolls the supplementary
census indicators. commercial-data is the downstream consumer demonstrating the
same deprivation feature set is needed elsewhere.

**Shared vs bespoke (Partial / tangled overlap):**
- *Shared core:* the canonical pipeline — normalise postcode casing/spacing →
  merge to LSOA11CD via ONS lookup → left-join IMD 2019 by `LSOA code (2011)` →
  return deprivation deciles. The `fetch()` download-cache helper is generic.
- *Bespoke (parameterise / keep out of shared utility):*
  - Postcode column name varies per dataset (`Incident_Postcode`,
    `Incident Postcode`); join key casing varies (`PCDS`/`pcds`,
    `LSOA11CD`/`lsoa11cd`). Must be parameters.
  - The explicit IMD sub-domain column allow-list in ProcessMining cell 36 is
    hardcoded; should be a configurable column selection.
  - The de-duplication `drop_duplicates(subset=['patientID'])` step is
    ambulance-CAD-specific business logic, not part of generic enrichment.
  - ESNEFT's reliance on `esneft_tools` means it cannot simply call the
    ProcessMining function; consolidation here is "adopt one canonical
    enrichment utility" rather than literal code reuse.

**Consolidation plan:** A single `enrich_with_imd(df, postcode_col,
lookup_path=None, imd_path=None, imd_columns=None)` utility wrapping the cached
ONS-lookup download and IMD join, with postcode/LSOA column names and the desired
IMD sub-domain columns passed in. ProcessMining collapses two notebooks into one
call; ESNEFT could adopt it in place of (or alongside) `esneft_tools`;
commercial-data documents the feature contract it expects.
