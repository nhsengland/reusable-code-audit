# Extraction Rationale: patient_csv_to_fhir_json

## What
`SynPath_Diabetes/t2dm/create_patients.ipynb` (Cells 1, 4, 5):

- Reads a wide patient CSV, generates a random name per gender, then **melts**
  the wide condition and observation columns into long per-patient records,
  groups them back into nested `conditions` / `observations` lists, and merges
  with the core demographic block to emit one JSON record per patient
  (`to_json(orient='records')`).
- A second pass (Cell 4) walks every patient and decorates each condition with
  FHIR-style scaffolding fields (`real_start_time`, `end`, `real_end_time`,
  `active`, `count`, `record_index`, `code`) and each observation with `start`,
  `end`, `code`.
- Cell 5 writes the assembled list to `patient_infos.json`.

## Why it is reusable
"Reshape a wide tabular patient extract into nested per-patient JSON resources"
is a common simulation/interoperability step — the wide→long melt, group-to-dict,
core-merge, and JSON-serialise recipe is dataset-agnostic. It is the standard
bridge from a flat CSV to a FHIR-ish nested document.

## Tangled bespoke logic to parameterise
1. **Hardcoded column groups**: `idVars`, `observationsVars`, `conditionsVars`
   (Cell 1, lines 12–44) are the SynPath diabetes schema. Accept these as
   arguments / a schema config.
2. **Hardcoded input/output paths**: `'./patients.csv'` (line 45),
   `'./patient_infos.json'` (Cell 5). Inject paths.
3. **Magic loop bound** `range(0, 10000)` (Cell 4) assumes exactly 10,000
   patients — must iterate over the actual records, not a literal count.
4. **Off-by-one indexing bug**: Cell 4 writes to `[jj-1]` while iterating `jj` in
   `range(len(...))`, so it mutates the *previous* element (wrapping to the last
   on `jj=0`). Behaviour must be documented and corrected on extraction.
5. **Hardcoded placeholder values**: dummy SNOMED-ish codes `'99999999'` /
   `'19191919'`, the fixed observation `start` date `'01/04/2021'`, and the
   `end/active/count/record_index` defaults (Cell 4) are simulation stubs — these
   FHIR field defaults should be a parameterised template, not literals.
6. **`names` library** generates Western names — locale assumption; keep name
   generation pluggable.
