# Deduplication: SDV/SDMetrics Synthetic-Data Quality and Privacy Metrics

## Shared functionality
Both repos evaluate synthetic vs real data using the SDV metrics ecosystem, including the same named metrics and the same SDV privacy-attack classes.

- SynthVAE `metrics.py` (10-114): `distribution_metrics()` wraps `sdv.evaluation.evaluate()` over a metric-name list (SVCDetection, GMLogLikelihood, CSTest, KSTest, KSTestExtended, Continuous/DiscreteKLDivergence — see `scratch_vae_expts.py` 160-168), plus optional Gower distance; `privacy_metrics()` wraps `NumericalMLP` / `CategoricalSVM` with key/sensitive fields.
- NHSSynth `modules/evaluation/metrics.py` (1-49): contains SynthVAE's `distribution_metrics` **verbatim, commented out** — direct, literal evidence of the copy lineage (including the `Metrics_SynthVAE_{}.csv` save line at its line 47). Its live successor is `common/constants.py` (21-100), which registers the SDMetrics single-table classes — including the *same* `ContinuousKLDivergence`, `DiscreteKLDivergence`, `CategoricalSVM`, `NumericalMLP` — into metric-group dicts, executed by `EvalFrame._compute_metric` in `modules/evaluation/utils.py` (160-226) with the same key-fields/sensitive-fields privacy-attack call signature (utils.py 200-225).

## State: Partial Overlap (one side vestigial)
**Shared:** metric selection by name from the SDV family; KL-divergence fidelity metrics; categorical/numerical privacy attacks parameterised by key + sensitive fields; categorical dtype coercion concerns for SDV's type inference (SynthVAE does it inline at metrics.py 33-36; NHSSynth solves it properly via `MetaData.get_sdv_metadata`, metadata.py 323-345).

**Bespoke:**
- SynthVAE: legacy `sdv.evaluation.evaluate` API (removed in modern SDV), Gower-distance augmentation (absent from NHSSynth), hardcoded `Metrics_SynthVAE_{}.csv` filename, per-seed aggregation loops duplicated across `scratch_vae_expts.py` (171-298) and `sdv_baselines.py` (110-225).
- NHSSynth: SDMetrics 1.x API, metric-group taxonomy (table/columnwise/pairwise/privacy), breakdown computation, integration with downstream tasks and fairness.

## Recommendation
Treat NHSSynth's `EvalFrame` + metric registries as the canonical implementation; delete the dead commented block in `modules/evaluation/metrics.py`; port the Gower-distance metric (the only SynthVAE capability not carried forward) into the registry as a custom metric so SynthVAE's `metrics.py` can be fully retired.
