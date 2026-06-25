# Extraction Rationale: pathway_transition_engine

## What
`SynPath_Diabetes/t2dm/manager/intelligence/intelligence.py` lines 1–62
(`get_next_environment_id`, `select_interaction`, `intelligence`):

- A stochastic care-pathway state machine. At each step it selects an interaction
  for the patient in the current environment, executes it to obtain record
  updates plus a `next_environment_id_to_prob` (a `{environment_id: probability}`
  map) and `next_environment_id_to_time` (a `{environment_id: timedelta}` map),
  then draws the next environment by probability and advances `patient_time` by
  the corresponding delta. Returns the updated patient/environment, new time, the
  record-update payload and the chosen next environment.

## Why it is reusable
This is a generic probabilistic discrete-event / Markov-pathway engine: "pick the
next state by a probability map, advance simulated time by a state-dependent
delta, collect side-effects". The control logic is independent of diabetes — it
would drive any patient-flow or care-pathway simulation. The
`select_interaction` / `get_next_environment_id` / time-advance loop is the
extractable kernel.

## Tangled bespoke logic to parameterise
1. **`select_interaction` is buggy/hardcoded**: it loops `range(15)` choosing a
   random interaction, `continue`s on `"death"` but never breaks or stores, so it
   simply returns the *last* sampled interaction (lines 11–16). The magic `15`
   and the `"death"` sentinel string must become parameters, and the loop logic
   fixed/clarified on extraction (behaviour documented first).
2. **`np.random.choice(environment.interactions)`** assumes a specific
   `environment` object API (`.interactions`, `.name`); the engine should depend
   on an injected interface, not the SynPath domain class.
3. **Side-effecting `print`** of the intelligence-layer state (lines 24–30) is
   debug output tangled into the engine — strip or route through logging.
4. **Interaction contract**: each interaction must return the exact 5-tuple
   `(patient, environment, update_data, next_env_to_prob, next_env_to_time)` —
   this implicit contract should be formalised (e.g. a dataclass) when extracted.
5. **No global seed control** here — reproducibility relies on the caller seeding
   `np.random`; the engine should accept an injected RNG.
6. No paths/codes/dataset names — no hardcoding flags beyond the magic `15` and
   `"death"`.
