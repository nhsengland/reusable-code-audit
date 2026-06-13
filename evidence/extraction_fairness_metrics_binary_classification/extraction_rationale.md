# Extraction: Group Fairness Metrics for Binary Classifiers (Demographic Parity, Equalised Odds)

## What it is
`NHSSynth/src/nhssynth/modules/evaluation/fairness.py` (lines 1-254): pure-pandas/numpy implementations of
- `compute_demographic_parity()` — max difference in positive prediction rate across groups of a protected attribute;
- `compute_equalized_odds()` — max TPR and FPR differences across groups;
- `run_fairness_metrics()` — orchestrator that binarises probability predictions at a threshold, validates protected attributes, aligns indices between data/predictions/labels and returns a flat `dict[str, float]` of named metrics.

## Why it is reusable
Fairness assessment of models trained on (synthetic) health data is an explicit NHS England priority, and these implementations have *no* dependency on NHSSynth, synthetic data, or any specific dataset — inputs are just a DataFrame, a predictions Series/DataFrame, attribute names and a target column. It replaced the abandoned Aequitas integration (backward-compatibility shim at tasks.py lines 27-33), and fills the gap left by SynthVAE's never-implemented `fairness_metrics()` stub (SynthVAE/metrics.py lines 120-130) — two prior attempts at the same capability in this lineage alone. Defensive handling of empty groups, NaN rates and missing columns is already done.

## Bespoke logic that must be parameterised/abstracted
This is the cleanest candidate in the group; remaining tangle is minor:
1. **Prediction-format assumption**: `_binarize_predictions` (lines 25-38) takes `predictions.iloc[:, 0]` — i.e. assumes a single-column probability frame for the positive class. Parameterise the positive-class column / accept arrays.
2. **Metric-name templating** (`f"dp_{attr}_max_diff"` etc.) is a reporting convention; allow a key-prefix or return structured records instead of flat strings.
3. **Index-alignment dead code** (lines 230-238): the `if not predictions.index.equals(data.index)` block does nothing (`pass`) — alignment semantics for test-set-only predictions must be made explicit (e.g. require pre-aligned inputs or accept an index mapping).
4. Threshold default `0.5` is already a parameter — keep it.
5. Binary-outcome assumption (labels in {0,1}) should be validated or generalised to multi-class via a `positive_label` argument.
