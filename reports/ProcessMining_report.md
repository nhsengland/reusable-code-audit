# Audit Report: ProcessMining

## Overview
ProcessMining is a notebook-driven analysis of ambulance/CAD (computer-aided
dispatch) data: it fabricates synthetic ambulance records, reshapes them into a
process-mining event log, enriches incident postcodes with LSOA/IMD deprivation,
and analyses inter-event timings across the care pathway. Everything lives in
`Notebooks/` as numbered, linear notebooks (`1_fake_data_gen`,
`2_CADData_to_EVlog`, `6_Enhancements_TimeBetweenEvents`,
`Add_postcodes_to_LSOAs_and_IMD`), with reusable logic embedded in cells rather
than a package. Notably it contains internal duplication (two postcode→LSOA→IMD
notebooks).

## SUL Adherence: Low
Logic is overwhelmingly cell-level script with side-effects (downloads, plotting,
`print` progress), not packaged functions. Where functions do exist
(`fetch`, `produce_LSOA_IMD`, `timebetweenevents`, `fake_data_generator`) they
are reasonable but hardcode column names, depend on module-global frames
(`postcode_LSOA_df`), and are duplicated across notebooks. Construction is often
inefficient (O(n²) per-patient loops with in-loop `concat`). The functions are
salvageable as extraction candidates, but as shipped the repo is script-shaped.

## Extraction Candidates
- **Wide record → event log** — `evidence/extraction_wide_record_to_event_log/`.
  Pivot per-patient timestamp columns into tidy (case, activity, timestamp), sort,
  parse datetime. Parameterise the activity-column list and id/timestamp names;
  replace the per-patient loop with a vectorised `melt` (also fixes the `*18`
  latent bug).
- **Postcode → LSOA → IMD enrichment** — `evidence/extraction_postcode_lsoa_imd_enrichment/`.
  Cached `fetch` + `produce_LSOA_IMD`. Parameterise postcode column, join keys,
  URLs/paths and IMD column allow-list; collapse the two duplicate notebooks into
  one function; pass the lookup frame in rather than via global.
- **Event-log time-between-events** — `evidence/extraction_event_log_time_between_events/`.
  `timebetweenevents` + stratified summaries. Parameterise case/activity/
  timestamp/filter column names and the time unit; split computation from
  plotting.

## Hardcoding Flags
- Local/relative paths and filenames: `cache_path = os.getcwd()/cache`,
  `'imd.csv'`, `PCD_OA_LSOA_MSOA_LAD_FEB20_UK_LU.csv`, the long
  `Postcode_to_Output_Area...November_2018...csv`, `source/` prefix,
  `'postcodes_east_mids.csv'`, output `"fake_outputs/..."`.
- Hardcoded download URLs: the ArcGIS postcode-lookup URL and the
  `assets.publishing.service.gov.uk` IMD 2019 File 7 URL.
- Hardcoded read spec: `usecols=[2,6,7,8,11]`, `skiprows=1`, `encoding='latin-1'`.
- Magic dates: incident window `'1/8/2032'`–`'1/8/2033'` in `fake_data_generator`;
  timestamp format `"%Y/%m/%d %H:%M:%S"`.
- Magic columns/constants: the 9-item `act` activity list with `*18` replicate
  count; `seed=42`; `n%100` progress; ambulance-specific categorical
  distributions; `drop_duplicates(subset=['patientID'])`.
- Region assumption: "east_mids" postcodes (East Midlands ambulance service).
- No credentials found.

## Deduplication Candidates
- **Postcode → LSOA → IMD linkage** — `evidence/deduplication_postcode_lsoa_imd_linkage/`.
  ProcessMining's two notebooks duplicate each other, and the same enrichment is
  needed by **ESNEFT_diabetes_StephenRicher** (via `esneft_tools`) and consumed
  by **commercial-data-healthcare-predictions** (its `imd_*`/`*_score` features).
- **Synthetic patient event timelines** —
  `evidence/deduplication_synthetic_patient_event_timelines/`. ProcessMining's
  `fake_data_generator` linear random-offset timeline overlaps the
  transition-driven event emission in **SynPath_Diabetes**.
