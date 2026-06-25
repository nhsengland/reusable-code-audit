# Deduplication Case: Train/Val/Test Split with CSV Export

**What it does:** Partitions a dataset into train/validation/test subsets at
configurable ratios and writes the resulting split (or its member IDs) to CSV so
the partition is reproducible across runs.

| Repo | File | Shared intent | Bespoke / tangled logic |
|---|---|---|---|
| mm-healthfair | `src/utils/preprocessing.py` (`generate_train_val_test_set`, lines 536-738) | Three-way split at given ratios with a fixed seed; persist split membership to CSV | sklearn `train_test_split` two-stage split; **stratification on outcome + `gender` + `race_group`**; `MinMaxScaler` fit on train and applied to val/test; a large hardcoded `disp_dict`/`nn_cols` prescription-column list; summary-statistics table generation; saves `subject_id` per split as `training_ids_<outcome>.csv` etc. |
| txt-ray-align | `data/get_subset.py` (lines 90-136) | Three-way split at given fractions with sampling; persist each split to CSV | splits on **unique `study_id`** (not rows) to avoid leakage across a patient's images; `random.sample` set arithmetic; optional `subset_fraction` down-sampling; disjointness asserts; writes `train.csv`/`val.csv`/`test.csv` into a fraction-named folder |

**Why it is an overlap:** Both answer the same need — *take a tabular dataset,
carve reproducible train/val/test partitions at configurable proportions, write
them to CSV* — but they are a **partial (tangled) overlap**. The split-and-export
skeleton is common; almost everything else diverges.

**Shared vs bespoke:**
- *Shared (extractable):* the three-way proportional split contract
  (`train_ratio`/`val_ratio`/`test_ratio` summing to 1), a **seed** for
  reproducibility, group-aware splitting to prevent leakage, and CSV
  serialisation of the partitions. The two-stage "split off train, then split the
  remainder" pattern is common to both.
- *Bespoke (must be parameterised):* the **split key / grouping column**
  (mm-healthfair splits rows by `subject_id`; txt-ray-align groups by `study_id`)
  — this must be a `group_col` argument; the **stratification columns**
  (`gender`, `race_group`, outcome) — a `stratify_on` argument, with stratify
  itself optional; the **outcome column name** (`outcome_col`,
  default `in_hosp_death`); the **library** (sklearn vs raw `random.sample`); and
  the heavy **mm-healthfair-specific payload** — `MinMaxScaler` feature scaling,
  the hardcoded `disp_dict` and `nn_cols` prescription list, and summary-stat
  reporting — which are *not* splitting concerns and must stay out of any shared
  splitter. txt-ray-align's `subset_fraction` down-sampling is likewise a bespoke
  pre-filter.

**Consolidation note:** A shared `split_to_csv(df, ratios, seed, group_col=None,
stratify_on=None, out_dir=...)` would absorb the common contract; the scaling,
display dictionary and summary statistics in mm-healthfair belong to a separate
reporting/preprocessing step, not the splitter. Both repos also feed the central
MIMIC ingestion case (`evidence/deduplication_mimic_ingestion_standardisation/`).
