# Extraction Rationale: wide_record_to_event_log

## What
`ProcessMining/Notebooks/2_CADData_to_EVlog.ipynb` (Cells 11, 13):

- Transforms a wide one-row-per-patient record (with many timestamp columns —
  `Incident_Time`, `Originated`, `Mobile`, `Arrive_scene`, `First_NEWS_Time`,
  `LAST_NEWS_Time`, `Depart_scene`, `Arrive_dest`, `Care_transfer`) into a long
  **event log**: one row per (`Patient_ID`, `Activity`, `Timestamp`), dropping
  null timestamps.
- Then sorts the event log by patient and time, resets the index, and parses the
  timestamp column to `datetime` — yielding a process-mining-ready event log.

## Why it is reusable
Pivoting a wide record whose columns are activity timestamps into a tidy
(`case_id`, `activity`, `timestamp`) event log is *the* entry step for any
process-mining workflow, and applies to any pathway dataset (ED, outpatient,
referral). The reshape-and-sort recipe is generic; only the activity column list
and ID/timestamp names are bespoke.

## Tangled bespoke logic to parameterise
1. **Hardcoded activity list**: the `act` list of nine timestamp column names
   (Cell 11) is ambulance-CAD-specific. Accept the timestamp-column list as an
   argument (better: derive event log via `pd.melt` over the supplied columns
   rather than the manual per-patient loop).
2. **Hardcoded column names**: `'patientID'` (input) vs output `'Patient_ID'`,
   `'Activity'`, `'Timestamp'`. Parameterise input id column and output names.
3. **Magic `*18`**: `pi=[...]*18` and the `range...18` comments assume up to 18
   activities while only 9 are listed (Cell 11) — a latent bug; the replicate
   count should equal the activity-list length.
4. **Inefficient construction**: the per-patient Python loop with
   `pd.concat(..., ignore_index=True)` inside the loop is O(n²). Replace with a
   single vectorised `melt`/`stack` on extraction (behaviour preserved).
5. **Hardcoded timestamp format** `format="%Y/%m/%d %H:%M:%S"` (Cell 13) — make
   the parse format configurable or rely on inference.
6. **Progress `print` every 100 patients** is tangled side-effect output — route
   through logging or drop.
