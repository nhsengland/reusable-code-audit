# Extraction Rationale: grouped_mcr_rashomon

## What
`commercial-data-healthcare-predictions/MCR_for_op_rf.py` lines 102–160:

- Fits a `RandomForestRegressor` with tuned hyperparameters and computes Model
  Class Reliance (MCR) — the Rashomon-set-based measure of how much *any*
  well-performing model in the model class could rely on a feature
  (`model.plot_mcr(...)`, producing lower/upper reliance bounds).
- Builds **grouped** MCR by partitioning features into named semantic groups
  (`week`, `sales`, `imd`, `age`, `demo`, `housing`, `land_use`, `weather`),
  mapping each group name to its feature-column indices
  (`grouping_names2indexes`), then computing MCR over feature groups rather than
  single features.

## Why it is reusable
Grouped MCR / Rashomon-set variable-importance is a generic interpretability
technique: define semantic feature groups, map them to column indices, and obtain
per-group reliance bounds for any fitted estimator exposing `plot_mcr`. The
group-to-index construction and the fit-then-MCR scaffold are dataset-agnostic
plumbing worth extracting; only the specific group membership is bespoke.

## Tangled bespoke logic to parameterise
1. **Hardcoded feature groups**: the eight column lists (`sales_cols`, `imd_cols`,
   `age_cols`, `demo_cols`, `housing_cols`, `land_use_cols`, `weather_cols`,
   `week_col`) and `grouping_names` (lines 119–153) are entirely specific to the
   PADRUS cold-and-flu sales dataset. Accept a `{group_name: [columns]}` mapping
   as input.
2. **Hardcoded row slice** `[:45844, :]` (line 9/11) — a dataset-specific cap on
   training rows; must be a parameter or removed.
3. **Magic constants** `random_state = 42`, `n_jobs = -1`, `num_times = 10`
   (lines 4–6, 11, 57) — expose as arguments.
4. **Hardcoded output path** `"fake_outputs/mcr_padrus_scores.csv"` (line 17) —
   inject the output path.
5. **`grouping_names2indexes` index lookup** assumes `X_train.columns` ordering;
   the extracted helper should derive group→index from the supplied column names
   robustly. The MCR call itself depends on a forest implementation exposing
   `plot_mcr` (a fork-specific dependency) — document this requirement.
