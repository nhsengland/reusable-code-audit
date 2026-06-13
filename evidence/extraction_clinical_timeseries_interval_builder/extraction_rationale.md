# Extraction Rationale: clinical_timeseries_interval_builder

## What
The time-series preprocessing block of `mm-healthfair/src/utils/preprocessing.py`
(lines 887-1325): `add_time_elapsed_to_events`, `convert_events_to_timeseries`,
`generate_interval_dataset` and its private helpers (`_prepare_feature_map_and_freq`,
`_process_patient_events`, `_validate_event_count`, `_handle_missing_features`,
`_impute_missing_values`, `_add_dynamic_mean`, `_resample_timeseries`, `_standardize_data`,
`_print_summary`). Together they convert long-form clinical event records
(`subject_id, charttime, label, value, source`) into per-patient, regularly-resampled,
imputed wide-form tensors ready for sequence models.

## Why it is reusable
Long-to-wide pivoting, per-source resampling frequencies, event-count gating, four imputation
strategies ("value"/-1 fill, forward, backward, missingness mask), elapsed-time windowing
relative to an index event, and min-max standardisation are the standard preprocessing steps
for *any* EHR time-series problem (vitals + labs is the canonical NHS secondary-care shape).
The logic is dataset-agnostic in structure but is currently welded to the MIMIC-IV ED cohort
pipeline, so other teams (e.g. deterioration prediction on local trust data) cannot import it.

## Tangled bespoke logic to parameterise
1. **Column-name contract hardcoded**: `"subject_id"`, `"charttime"`, `"label"`, `"value"`,
   `"linksto"` appear as literals throughout (e.g. lines 924, 931-935, 996, 1010-1017).
   Parameterise as `id_col`, `time_col`, `label_col`, `value_col`, `source_col`.
2. **Index-event column is MIMIC-specific**: `edregtime` (ED registration time) is used as the
   reference time (lines 1011, 1018-1023, 1159). Parameterise as `index_time_col`.
3. **Source-to-frequency rule hardcoded** (line 1100): `freq[src] = vitals_freq if
   src == "vitalsign" else lab_freq` — a literal MIMIC table name decides resampling frequency.
   Replace with a caller-supplied `dict[source_name, freq]`.
4. **Output dictionary keys** (lines 1062-1064): `"dynamic_0"`/`"dynamic_1"` are assigned by
   comparing column lists against a `vitals_lkup` list passed in from the calling script —
   brittle ordering logic; key by source name instead.
5. **Outcome columns** are dropped/re-attached by literal list (`outcomes` parameter is already
   present — keep, but document the contract).
6. **Magic defaults**: `vitals_freq="5h"`, `lab_freq="1h"`, `max_events=1e6`, fill value `-1`
   should be surfaced in a config object rather than scattered defaults.
