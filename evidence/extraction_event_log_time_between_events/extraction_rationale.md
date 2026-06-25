# Extraction Rationale: event_log_time_between_events

## What
`ProcessMining/Notebooks/6_Enhancements_TimeBetweenEvents.ipynb` (Cells 22, 24,
26, 28):

- `timebetweenevents(df, first_activity, second_activity)` — given a long event
  log (`Patient_ID`, `Activity`, `Timestamp`, `relativetime_s`), slices the two
  named activities, merges per patient, and returns the per-case elapsed time
  between them in minutes.
- `timedensityandboxplot(...)` — KDE + boxplot of those inter-event times with
  mean/median printout.
- `boxplot_time_between_activities_per_attribute(...)` — stratifies inter-event
  time by an arbitrary categorical attribute (optionally filtered by `Outcome`).
- `attributes_effect_on_mean_time_between_events(...)` — tabulates how each value
  of an attribute shifts the mean inter-event time relative to the overall mean.

## Why it is reusable
"Time between two events in a process/event log, overall and stratified by a
patient attribute" is a core process-mining / care-pathway analytic that applies
to any timestamped event log (ambulance, ED, outpatient pathways). The functions
are already parameterised by activity and attribute names, so the core is close
to a clean Utility — it is only tangled with plotting and dataset-specific column
names.

## Tangled bespoke logic to parameterise
1. **Hardcoded column names**: `'Patient_ID'`, `'Activity'`, `'Timestamp'`,
   `'relativetime_s'` (cell 22) and `'Outcome'` (cells 26, 28). Parameterise the
   case-id, activity, timestamp and relative-time column names; pass the
   filter-column instead of fixing `'Outcome'`.
2. **Minutes hardcoded** — `x / 60` (cell 22). Make the time unit configurable.
3. **Plotting tangled with computation**: the boxplot/KDE/`plt.show()` and the
   `print(...)` of mean/median are mixed into the analytic functions. Split the
   pure `timebetweenevents` computation from the visualisation layer.
4. **Magic sentinel** `specify_outcome_required != 'None'` uses the string
   `'None'` as a no-filter flag (cells 26, 28) — should be a real `None`/default.
5. **`relativetime_s` is assumed pre-computed** upstream; the extracted utility
   should either accept raw timestamps and derive relative time, or document the
   precondition.
