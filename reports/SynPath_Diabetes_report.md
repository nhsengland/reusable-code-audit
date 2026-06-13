# Audit Report: SynPath_Diabetes

## Overview
SynPath_Diabetes is a Type 2 diabetes care-pathway *simulator*: synthetic
patients move between care environments (GP, community, outpatient, hospital)
driven by a probabilistic "intelligence" layer, accumulating FHIR-style
Encounter/Observation records. The code is module-structured under `t2dm/`
(`manager/intelligence/`, `create_patients.ipynb`) and a transition engine is
cleanly separated from the per-interaction definitions, though interaction
payloads carry hardcoded clinical/simulation stubs and the patient-build notebook
is exploratory.

## SUL Adherence: Medium
There is real separation of concerns: `intelligence.py` factors out a generic
state-machine engine (`select_interaction`, `get_next_environment_id`,
`intelligence`) distinct from the domain interactions in `interactions/gp0.py`.
That engine is reusable. Pulling toward Low: `select_interaction` contains a
latent bug (loops 15 times but returns the last sample), `print` debug output is
tangled into the engine, interaction return-contracts are implicit 5-tuples, and
`create_patients.ipynb` is notebook-style with hardcoded column lists, magic loop
bounds and an off-by-one indexing bug.

## Extraction Candidates
- **Pathway transition engine** — `evidence/extraction_pathway_transition_engine/`.
  Probabilistic state machine: pick next environment by probability map, advance
  simulated time by a per-state `timedelta`. Parameterise: inject the environment
  interface and RNG, fix/expose the `range(15)` retry and `"death"` sentinel,
  route `print` through logging, formalise the interaction return contract.
- **Patient CSV → FHIR-style JSON** — `evidence/extraction_patient_csv_to_fhir_json/`.
  Wide→long melt, nested condition/observation grouping, JSON emit. Parameterise:
  pass `idVars`/`observationsVars`/`conditionsVars` and I/O paths; iterate over
  actual records (drop the `range(0,10000)` and `[jj-1]` bug); make FHIR field
  defaults a template.

## Hardcoding Flags
- Input/output paths `'./patients.csv'`, `'./patient_infos.json'`.
- Column-group lists `idVars`/`observationsVars`/`conditionsVars`
  (`create_patients.ipynb` Cell 1) — diabetes schema baked in.
- Magic loop bound `range(0, 10000)` assuming exactly 10,000 patients.
- Placeholder/magic values: dummy codes `'99999999'` and `'19191919'`, fixed
  observation date `'01/04/2021'`.
- In-interaction simulation magic numbers: `cost: 4`, `glucose: 0`, `carbon: 6`,
  transition probabilities `{0: 0.9, 29: 0.1}`, environment IDs `0`/`29`, fixed
  `timedelta(minutes=15)` / `days=10` / `days=20` in `gp0.measure_hba1c`.
- Retry magic `range(15)` and `"death"` sentinel in `select_interaction`.
- No credentials or local trust codes found.

## Deduplication Candidates
- **Diabetes measure / observation vocabulary** —
  `evidence/deduplication_diabetes_measure_vocabulary/`. SynPath's
  `observationsVars`/`conditionsVars` encode the same diabetes measure panel that
  **ESNEFT_diabetes_StephenRicher** declares as CTV3 rename maps and Type 1/2
  label lists — the same clinical vocabulary in two incompatible key spaces.
- **Synthetic patient event timelines** —
  `evidence/deduplication_synthetic_patient_event_timelines/`. SynPath's
  transition-driven per-patient event emission overlaps the linear random-offset
  timeline generator in **ProcessMining** (`1_fake_data_gen.ipynb`); shared
  primitive is "next event = base time + delta, iterated per patient".
