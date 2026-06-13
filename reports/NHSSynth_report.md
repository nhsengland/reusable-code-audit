# Audit Report: NHSSynth

## Overview
NHSSynth (nhsengland) is the matured, packaged successor to SynthVAE: a modular
toolkit for generating and evaluating synthetic tabular data. It is structured
as a proper `src/nhssynth/` package with a CLI, a declarative
config/metadata/transformer dataloader, pluggable generative models (VAE, GAN,
(DP)CTGAN, DPVAE) built on a shared `Model`/`DPMixin` scaffold, and an
evaluation module covering SDMetrics fidelity/privacy, downstream "train on
synthetic, test on real" tasks and group-fairness metrics. Because it grew out
of SynthVAE, it carries forward the same VAE, DP, preprocessing and metric
capabilities — generally in a cleaner, parameterised form.

## SUL Adherence: High
NHSSynth demonstrates strong Structure/Utility/Logic separation. The
`Model`/`DPMixin` scaffold is dataset- and model-agnostic and gains DP by
composition (`class DPVAE(DPMixin, VAE)`); the `MetaData`/`MetaTransformer`
layer drives preprocessing from declarative YAML rather than hardcoded column
lists; downstream tasks are discovered as drop-in plugins; fairness metrics are
pure pandas/numpy with no project coupling. Remaining weaknesses are minor: an
`eval()`-based transformer registry (a code-injection risk from YAML), a
`setup_device` bug that overrides GPU selection to CPU, CWD-relative plugin
imports, and some magic inference thresholds — all parameterisation/hardening
issues rather than structural tangle.

## Extraction Candidates
- **Generic PyTorch model scaffold with opt-in DP** — `evidence/extraction_dp_model_training_scaffold/`.
  `common/model.py` `Model` + `common/dp.py` `DPMixin`. Parameterise: accept
  column-index lists (or a thin protocol) instead of a `MetaTransformer`; expose
  tqdm interval, patience delta and batch size; fix the `setup_device` CPU
  override.
- **Tabular metadata inference + YAML round-trip** — `evidence/extraction_tabular_metadata_inference/`.
  `dataloader/metadata.py` `MetaData`. Parameterise: inject a transformer
  registry dict (replace `eval()`); expose categorical/boolean nunique
  thresholds; make the constraint graph and missingness strategies optional
  plug-ins.
- **Group fairness metrics for binary classifiers** — `evidence/extraction_fairness_metrics_binary_classification/`.
  `evaluation/fairness.py`. Parameterise: positive-class column/array;
  key-prefix or structured return; explicit index-alignment contract.
- **Downstream-task plugin loader** — `evidence/extraction_downstream_task_plugin_loader/`.
  `evaluation/tasks.py` `Task`/`get_tasks`. Parameterise: resolve task paths
  absolutely (not CWD-relative); make the expected attribute name configurable;
  validate loaded objects and drop the deprecated `supports_aequitas` alias.
- **Gower + SDV distribution/privacy metrics** — `evidence/extraction_gower_sdv_distribution_metrics/`
  (NHSSynth holds SynthVAE's original commented-out; its live `EvalFrame` is the
  successor but lacks the Gower-distance metric, which should be ported in).

## Hardcoding Flags
- **Dataset names**: convention-based task directories `tasks/support/` and
  `tasks/hypertension_synthetic/` tie example downstream tasks to named
  datasets; the SDV-metadata bridge is generic but the bundled tasks are
  SUPPORT/hypertension-specific.
- **Magic constants**: inference heuristics (categorical if `nunique() <= 10`,
  boolean if `<= 2`, metadata.py 95-100); rounding/sigma-floor and
  kurtosis-tracking constants in the continuous transformer (0.15, 99.9th
  percentile, kurtosis > 5); DP policy defaults `target_epsilon=3.0`,
  `max_grad_norm=5.0`, `target_delta = 1/nrows`; tqdm refresh `0.5`s, patience
  delta `_min_metric/1e4`, `batch_size=32`.
- **Code-smell flags**: `eval(transformer_name)(...)` in metadata.py (injection
  risk from user YAML); CWD-relative `spec_from_file_location` in tasks.py;
  fairness metric-name string templating (`dp_{attr}_max_diff`).
- No hardcoded local filesystem paths or plaintext credentials found; paths flow
  through the CLI/config layer.

## Deduplication Candidates
- **Tabular VAE architecture** — `evidence/deduplication_tabular_vae_architecture/`
  — vs **SynthVAE** (`VAE.py`). NHSSynth's `vae.py` is the canonical superset.
- **Opacus DP training integration** — `evidence/deduplication_opacus_dp_training/`
  — vs **SynthVAE**. NHSSynth's `DPMixin` is the deduplicated form (modern
  Opacus 1.x `make_private_with_epsilon` vs SynthVAE's vendored 0.x `attach`).
- **GMM + one-hot mixed-type preprocessing** — `evidence/deduplication_gmm_onehot_preprocessing/`
  — vs **SynthVAE**. NHSSynth's metadata-driven transformers supersede
  SynthVAE's hardcoded `support_pre_proc`/`mimic_pre_proc`.
- **SDV/SDMetrics quality metrics** — `evidence/deduplication_sdv_quality_metrics/`
  — vs **SynthVAE** (SynthVAE's `distribution_metrics` survives commented-out in
  NHSSynth's `evaluation/metrics.py`; `EvalFrame` is the live successor).
- **Random seed setting** — `evidence/deduplication_random_seed_setting/`
  — vs **SynthVAE** (`set_seed`); NHSSynth's version is the most complete and
  the recommended canonical copy; intent also appears inline in ELM4PSIR,
  txt-ray-align, mm-healthfair.
- **Experiment configuration loading** — `evidence/deduplication_experiment_config_loading/`
  — vs **nlp_renal_biopsy, evalsense, mm-healthfair**. NHSSynth's `write_config`
  reproducibility round-trip is the one extra worth keeping.
- **Correlation-matrix plotting** — `evidence/deduplication_correlation_plotting/`
  — vs **SynthVAE** (the SynthVAE correlation block sits commented-out in
  NHSSynth's `plotting/plots.py`; live code is the t-SNE plot).
