# Extraction Rationale: longitudinal_measure_patient_summary

## What
`ESNEFT_diabetes_StephenRicher/scripts/utils.py` lines 143–268 (`removeOutlier`,
`summariseByPatient`, `_summarise`):

- `removeOutlier` — per-measure IQR outlier removal (3×IQR fences) over a long
  event table, nulling out-of-range `RecordingValue`s.
- `summariseByPatient` / `_summarise` — collapses a per-patient longitudinal
  event log into a one-row-per-patient feature summary: per-measure mean wait
  between observations; T1D/T2D flags; first referral date; date of diagnosis and
  days-to-referral; total appointments, time at centre and mean days between
  appointments; and, for each clinical measure, the initial/final/mean value and
  the rate of change (only over records spanning more than 90 days).

## Why it is reusable
Reducing a longitudinal clinical event log to a per-patient feature row —
first/last/mean values, change rates, inter-event waits, appointment counts — is
a generic feature-engineering step for any time-stamped patient record system,
not just diabetes. The IQR outlier method and the longitudinal-summary skeleton
are reusable; only the measure vocabulary and column names are bespoke.

## Tangled bespoke logic to parameterise
1. **Hardcoded column names**: `'CTV3Desc'`, `'RecordingValue'`, `'patientID'`,
   `'CodeEventDate'`, `'ReferralDate'`, `'RecodingLabel'` (note the apparent typo
   for "RecordingLabel"), throughout. Parameterise the measure/value/id/date
   column names.
2. **Hardcoded measure vocabulary**: the `measures` lists (`'BMI'`,
   `'HbA1c (IFCC)'`, `'GFR'`, `'HbA1c'`, `'Diastolic BP'`, `'Urine Microalbumin'`
   at lines 99–102; a longer default at lines 8–12) and the `type1_default` /
   `type2_default` diabetes label lists are ESNEFT-specific — overlaps the
   `deduplication_diabetes_measure_vocabulary` case; should be injected.
3. **Magic constants**: IQR multiplier defaults to `3` but `removeOutlier`'s
   `threshold` argument is ignored (it hardcodes `* 3` and `Q1 - IQR*3` at lines
   18–20); the 90-day minimum span for computing change (line 121); the sentinel
   event string `'Date of diagnosis'` and `'None'` recoding label. Parameterise
   all of these and fix the dead `threshold` argument.
4. **`.head(1)[0]` / `.tail(1)[0]` positional access** (lines 118–119) is fragile
   to non-default indices — should use `.iloc[0]`/`.iloc[-1]` on extraction
   (behaviour preserved).
5. **`groupby(...).apply` with nested dict-building** is slow; vectorise after
   extraction while preserving outputs.
