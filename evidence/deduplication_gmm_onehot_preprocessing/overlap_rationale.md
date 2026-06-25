# Deduplication: Bayesian-GMM + One-Hot Mixed-Type Preprocessing and Inverse Transform

## Shared functionality
Both repos prepare mixed-type tabular data for a VAE the same way: continuous columns are encoded with a **Bayesian Gaussian Mixture** (a normalised value column + one-hot component-assignment columns, the CTGAN-style "mode-specific normalisation"), categorical columns are one-hot encoded, datetimes are converted to numeric first, and a matching **inverse transform** maps generated output back to the original schema.

- SynthVAE `utils.py`: `support_pre_proc` (24-144) and `mimic_pre_proc` (151-328) both loop per-column fitting `rdt` `BayesGMMTransformer(random_state=gmm_seed)` / `OneHotEncodingTransformer` / `DatetimeTransformer`, track `num_categories`/`num_continuous`, generate `.normalized` and `.component` columns, and reorder the frame (categoricals first, continuous last). `reverse_transformers` (334-400) walks the transformer dicts in reverse, slicing column names out of dict keys by magic offsets (`transformer_name[12:]`, `[11:]`, `[9:]`).
- NHSSynth `modules/dataloader/transformers/continuous.py`: `ClusterContinuousTransformer.apply` (77-267) fits sklearn `BayesianGaussianMixture` directly, emits `<col>_normalised` + `<col>_c{i}` columns and `revert` (269-439) inverts via component sampling — the same semantic operation, generalised and metadata-driven through `MetaTransformer`/`MetaData` instead of hardcoded column lists. `OHECategoricalTransformer` and `DatetimeTransformer` parallel the rdt ones.

## State: Tangled Overlap
**Shared:** GMM mode-specific normalisation of continuous columns; one-hot encoding of categoricals and of GMM component indices; datetime-to-numeric conversion; fit-store-invert transformer lifecycle; "normalised value + component columns" naming scheme (SynthVAE `.normalized`, NHSSynth `_normalised` — same idea, incompatible spellings).

**Bespoke in SynthVAE (the tangle):**
- `support_pre_proc` hardcodes SUPPORT columns (`duration`, `event`, `x1`-`x14`, lines 29-50) and even a data-cloning hack (`data_supp["x14"] = data_supp["x0"]`, line 29);
- `mimic_pre_proc` hardcodes MIMIC columns (`ETHNICITY`, `DISCHTIME`, `ADMITTIME`, `DOB`, `CHARTTIME`, `SUBJECT_ID`, ..., lines 155-164);
- the two functions are ~80% copy-paste of each other (internal duplication);
- module-level `gmm_seed = 0` (line 21);
- `reverse_transformers` relies on dict-key string offsets tied to the `"continuous_"`/`"categorical_"`/`"datetime_"` prefixes.

**Bespoke in NHSSynth:** missingness pseudo-cluster handling, constraint-adherence columns, sigma floors / safety clipping / kurtosis tracking (magic numbers 0.15, 99.9th percentile, kurtosis > 5), DEBUG_VERBOSE instrumentation.

## Recommendation
NHSSynth's transformer stack is the deduplicated, parameterised successor: SynthVAE's per-dataset functions are exactly what the `MetaData`-driven design eliminates. A shared library should adopt NHSSynth's `ColumnTransformer` interface, standardise the column-suffix convention (one spelling), and externalise the magic constants. SynthVAE's `support_pre_proc`/`mimic_pre_proc` should be reduced to metadata YAML files consumed by that library.
