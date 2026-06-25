# Extraction Rationale: bootstrapped_fairness_metrics

## What
A pair of functions in `mm-healthfair/src/utils/fairness_utils.py` (lines 80-201):

- `bias_corrected_ci()` — a generic implementation of the bias-corrected and accelerated (BCa)
  bootstrap confidence interval (bias-correction factor via the normal quantile of the empirical
  CDF, acceleration factor via jackknife resampling, adjusted percentiles).
- `get_bootstrapped_fairness_measures()` — stratified bootstrap (resampling within each
  sensitive-attribute group) of three Fairlearn group-fairness ratios (Demographic Parity,
  Equalized Odds, Equal Opportunity), returning point estimate plus BCa 95% CI for each.

## Why it is reusable
Any NHS analytics project that reports group-fairness metrics needs uncertainty estimates, and
Fairlearn does not provide confidence intervals out of the box. The stratified-bootstrap +
BCa-CI pattern here is model-agnostic and dataset-agnostic: it operates purely on
`y_test`, `y_hat` and a sensitive-attribute frame. `bias_corrected_ci()` on its own is a
general statistics utility applicable to any bootstrapped metric (AUC, calibration error,
synthetic-data quality scores, etc.).

## Tangled bespoke logic to parameterise
1. **Metric set is hardcoded** (lines 141-145): the `global_metrics` dict is fixed to the three
   Fairlearn ratios and the three are then re-invoked by literal name (lines 167-183).
   Parameterise as a caller-supplied `dict[str, Callable]` and loop over it, removing the
   triplicated call/append blocks.
2. **Confidence level is hardcoded** (line 104): `alpha = [0.025, 0.975]` inside
   `bias_corrected_ci`. Expose `confidence_level: float = 0.95`.
3. **Division-by-zero floor** (lines 176-178): `max(metric, 0.001)` is applied only to two of
   the three metrics. Make the epsilon a parameter and apply uniformly or via the metrics dict.
4. **Return shape** (lines 197-201): the fixed 3-tuple `(dpr_full, eor_full, eop_full)` should
   become `dict[str, tuple[float, float, float]]` keyed by metric name.
5. `n_boot`, `seed` are already parameters — keep them.
