# Extraction: Gower + SDV Distributional and Privacy Metric Calculator

## What it is
`SynthVAE/metrics.py` (lines 10-114) contains two metric calculators for synthetic vs real tabular data:
- `distribution_metrics()` — wraps `sdv.evaluation.evaluate()` for a user-supplied list of fidelity metrics (SVCDetection, CSTest, KSTest, KL divergences, etc.), coerces categorical columns to `object` dtype so SDV does not misinfer them as numerical, optionally appends a mean Gower distance, and returns a tidy one-row DataFrame.
- `privacy_metrics()` — wraps SDV's `NumericalMLP`/`CategoricalSVM` privacy attacks, automatically choosing the attack type based on whether the named sensitive variable is continuous or categorical, and building the key-field set as "all other columns".

## Why it is reusable
Every synthetic-data project in the NHS portfolio needs exactly this: a single call that takes (real_df, synth_df, categorical_columns, metric names) and returns comparable scores. The dtype-coercion workaround for SDV's type inference and the sensitive-variable-driven attack selection are non-obvious, repeatedly reinvented details. Notably, NHSSynth carried this exact function forward only as a commented-out block (`modules/evaluation/metrics.py` lines 1-49) before rebuilding it as `EvalFrame` — i.e. the team itself wanted to reuse it but had no shared library to take it from. The Gower-distance augmentation does not exist in NHSSynth's replacement, so this code is still the only home of that capability.

## Tangled bespoke logic that must be parameterised
1. **Hardcoded output filename branding** (lines 64-68): `"{}Metrics_SynthVAE_{}.csv".format(saving_filepath, pre_proc_method)` bakes the project name and a SynthVAE-specific preprocessing label into the artefact name. Parameterise as a caller-supplied output path; remove `pre_proc_method` entirely (it is otherwise unused in the function).
2. **`fillna(0)` imputation policy** in `privacy_metrics()` (lines 93, 108-110) is a silent analytic choice; expose as an `impute_value`/strategy parameter.
3. **Attack model choice** is fixed to `NumericalMLP`/`CategoricalSVM`; lift into a mapping argument so other SDV privacy attackers can be used.
4. `fairness_metrics()` (lines 120-130) is an empty stub and should be dropped on extraction (NHSSynth's `modules/evaluation/fairness.py` is the working successor).
5. Pin/adapt to a stated SDV/SDMetrics version: `sdv.evaluation.evaluate` and `sdv.metrics.tabular` are legacy APIs (removed in modern SDV), so the extracted utility needs an SDMetrics-era backend.
