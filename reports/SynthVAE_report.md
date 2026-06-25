# Audit Report: SynthVAE

## Overview
SynthVAE (nhsx) is a research codebase for generating synthetic tabular health
data with a variational autoencoder over mixed continuous/categorical columns,
plus differentially private training (Opacus) and SDV-based fidelity/privacy
evaluation. It is organised as a flat collection of top-level scripts
(`VAE.py`, `utils.py`, `metrics.py`, `plot.py`, `scratch_vae_expts.py`,
`sdv_baselines.py`) wired to two specific datasets — pycox's SUPPORT and an
internal NHSX MIMIC-III extract. It is the historical ancestor of NHSSynth, so
much of its code reappears there in matured form. Two third-party libraries
(`opacus/`, `rdt/`) are vendored wholesale into the repository as first-party
trees.

## SUL Adherence: Low
Structure, Utility and Logic are heavily tangled. Genuinely reusable utilities
are welded to dataset specifics: `support_pre_proc`/`mimic_pre_proc` hardcode
column lists and are ~80% copy-paste of each other; `constraint_filtering`
embeds MIMIC clinical rules inside an otherwise generic rejection-sampling loop;
the DP training loop is copy-pasted from the non-private loop inside `VAE.py`.
There is no package boundary, no dependency pinning (Opacus and RDT are
committed into the tree rather than depended upon), and module-level mutable
state (`gmm_seed = 0`). Several latent bugs follow from the tangle (OR-combined
constraints, `pre_proc_method` dropped on top-up, missing `random.seed`).

## Extraction Candidates
- **Constrained rejection sampling** — `evidence/extraction_constrained_rejection_sampling/`.
  `utils.py` `constraint_filtering` (406-495). Parameterise: pass a `generate(n)`
  model, an `inverse_transform` callable and a constraint predicate (with an
  explicit all/any combinator — current `|` is a bug); strip the hardcoded MIMIC
  rules and CUDA branching.
- **Gower + SDV distribution/privacy metrics** — `evidence/extraction_gower_sdv_distribution_metrics/`.
  `metrics.py` `distribution_metrics`/`privacy_metrics` (10-114). Parameterise:
  caller-supplied output path (drop `Metrics_SynthVAE_{}.csv` branding and the
  unused `pre_proc_method`), injectable attack-model map, configurable NaN
  imputation; port to an SDMetrics-era backend (legacy `sdv.evaluation` API).
- **Tabular VAE architecture (Encoder/Decoder/Noiser/ELBO)** — `evidence/deduplication_tabular_vae_architecture/`
  (extraction overlaps NHSSynth's superior copy). The reusable core is the
  encoder/decoder topology, reparameterisation and mixed-likelihood ELBO;
  parameterise on a column-grouping descriptor rather than the positional
  "categoricals-first/continuous-last" block convention.

## Hardcoding Flags
- **Dataset names**: pycox SUPPORT baked into `support_pre_proc` (`duration`,
  `event`, `x1`-`x14`, utils.py 29-50) and `plot.py` (`support.read_df()`);
  MIMIC-III column lists baked into `mimic_pre_proc` (`ETHNICITY`,
  `DISCHARGE_LOCATION`, `FIRST_CAREUNIT`, …, utils.py 155-164).
- **Magic columns/dates**: datetime columns `["ADMITTIME", "DISCHTIME", "DOB",
  "CHARTTIME"]` (utils.py 164) and the constraint rules referencing them
  (447-449); the data-cloning hack `data_supp["x14"] = data_supp["x0"]`
  (utils.py 29).
- **Magic constants**: module-level `gmm_seed = 0` (utils.py 21); DP defaults
  `C=1e16`, `target_delta=1e-5`, `sample_rate=0.1` baked into the
  `diff_priv_train` signature; latent dim literals (2 in `plot.py`).
- **Output-filename branding**: `*_SynthVAE_{pre_proc_method}.png/.csv`
  throughout (`metrics.py` 67; `utils.py` 527, 571, 619, 655); `actual_corr_{}`/
  `sample_corr_{}`/`diff_corr_{}` in `plot.py`.
- **Vendored third-party code**: entire `opacus/` and `rdt/` trees committed as
  first-party (~10k lines) instead of pinned dependencies.
- No plaintext credentials found.

## Deduplication Candidates
- **Tabular VAE architecture** — `evidence/deduplication_tabular_vae_architecture/`
  — vs **NHSSynth** (`vae.py`). NHSSynth's is a strictly more capable direct
  descendant (free bits, beta annealing, missingness head).
- **Opacus DP training integration** — `evidence/deduplication_opacus_dp_training/`
  — vs **NHSSynth** (`common/dp.py` `DPMixin`). NHSSynth's mixin is the clean
  successor; SynthVAE's vendored `opacus/` tree should be deleted.
- **GMM + one-hot mixed-type preprocessing** — `evidence/deduplication_gmm_onehot_preprocessing/`
  — vs **NHSSynth** (`dataloader/transformers/continuous.py`). NHSSynth's
  metadata-driven `ClusterContinuousTransformer` supersedes SynthVAE's
  per-dataset functions.
- **SDV/SDMetrics quality metrics** — `evidence/deduplication_sdv_quality_metrics/`
  — vs **NHSSynth** (`evaluation/metrics.py` — which contains SynthVAE's
  function verbatim but commented out; live successor is `EvalFrame`).
- **Random seed setting** — `evidence/deduplication_random_seed_setting/`
  — vs **NHSSynth** (`common/common.py` `set_seed`); also appears inline across
  ELM4PSIR, txt-ray-align, mm-healthfair.
- **MIMIC ingestion/standardisation** — `evidence/deduplication_mimic_ingestion_standardisation/`
  — vs **mm-healthfair, priv-lm-health, priv-lm-health-extended, txt-ray-align**.
- **Correlation-matrix plotting** — `evidence/deduplication_correlation_plotting/`
  — vs **NHSSynth** (`plotting/plots.py` — SynthVAE's block preserved
  commented-out; live code is t-SNE only).
