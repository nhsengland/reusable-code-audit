# Deduplication Case: Synthetic Patient Event Timelines

**What it does:** Generates synthetic patients and a timeline of timestamped
clinical events for each one — an initial event time, then a chain of subsequent
events each offset from the previous by a (random or modelled) time delta —
producing a per-patient sequence of (event name, timestamp) records suitable for
process mining or simulation.

**Why it is an overlap:** Two repositories build synthetic patient event
timelines, differing in mechanism but sharing the same intent and output shape:

| Repo | File | Implementation |
|---|---|---|
| ProcessMining | `Notebooks/1_fake_data_gen.ipynb` (Cells 7, 11) | `fake_data_generator(size, seed)` fabricates demographics by sampling categorical distributions, sets an `Incident_Time`, then derives a fixed chain of downstream timestamps (`Originated`→`Mobile`→`Arrive_scene`→`First_NEWS_Time`→…) via `_randomDate(base, (min,max))` minute-offsets |
| SynPath_Diabetes | `t2dm/manager/intelligence/interactions/gp0.py` + `intelligence.py` (lines 18–55, 1–62) | Each interaction (e.g. `measure_hba1c`) emits an Encounter/Observation entry offset from `patient_time` by a `timedelta`, and `intelligence()` advances `patient_time` by `next_environment_id_to_time[...]` to build the next event — a stochastic state-machine of patient events |

Both produce, per patient, a temporally ordered sequence of clinical events where
each event's timestamp is the previous timestamp plus a delta. ProcessMining does
this with a hardcoded linear chain of random minute-offsets; SynPath does it with
a probabilistic transition engine. The **outcome** (synthetic per-patient event
timelines) is the overlap.

**Shared vs bespoke (Partial overlap — tangled):**
- *Shared core:* the timeline-construction primitive — given a base time and a
  delta distribution, emit the next timestamped event; iterate to build a
  per-patient ordered event sequence; seedable for reproducibility.
- *Bespoke (must stay project-specific / be parameterised):*
  - ProcessMining's event *names* (`Arrive_scene`, `Care_transfer`) and the
    ambulance-specific categorical distributions (clinician grade, NEWS scores,
    outcome probabilities reflecting real ambulance data) are domain content.
  - ProcessMining hardcodes the incident window (`1/8/2032`–`1/8/2033`) and an
    18-long activity list — magic constants.
  - SynPath's transition probabilities, environment IDs, and the FHIR-style
    Encounter/Observation resource payloads (with `cost`/`carbon`/`glucose`
    fields) are diabetes-pathway business logic.
  - The two differ fundamentally in control flow (fixed chain vs probabilistic
    state machine), so consolidation is at the *primitive* level, not whole-file.

**Consolidation plan:** Extract a small reusable timeline kernel —
`next_event(base_time, delta_distribution, rng)` plus a
`build_timeline(start, steps)` driver — parameterised by a list of event
definitions (name + delta spec). ProcessMining supplies its linear ambulance
chain; SynPath supplies its transition-driven steps. Demographic sampling and
the pathway/transition probabilities remain in each project as injected
configuration.
