# Extraction: Constrained Rejection Sampling for Synthetic Data Generation

## What it is
`constraint_filtering()` in `SynthVAE/utils.py` (lines 406-495, with its dependency `reverse_transformers()` at lines 334-400) is a generate-filter-top-up loop: it draws synthetic rows from a trained generative model, inverse-transforms them back to the original schema, filters out rows that violate domain constraints, and keeps generating until exactly `n_rows` valid rows exist (trimming any surplus).

## Why it is reusable
Constraint-respecting sampling is needed by *every* tabular synthetic-data project (e.g. "discharge date must be after admission date", "age must be positive"). The outer loop — sample, invert, filter, count, top-up — is entirely model- and dataset-agnostic; it only needs a `generate(n)` callable, a reverse-transform callable and a row-validity predicate. NHSSynth later re-solved the same problem differently (constraint graphs in `modules/dataloader/constraints.py`), confirming recurring demand for this capability.

## Tangled bespoke logic that must be parameterised
This is a textbook Tangled Overlap: a generic rejection-sampling loop with MIMIC-III business rules hardcoded inside it.

1. **The nested `constraint_check()` (lines 443-452)** hardcodes MIMIC column names (`age`, `DISCHTIME`, `ADMITTIME`, `DOB`, `CHARTTIME`) and four clinical rules. It must be lifted out and passed in as a `constraints: Callable[[pd.DataFrame], pd.DataFrame]` (or a declarative list of predicates).
2. **Probable logic bug to fix on extraction:** the rules are combined with `|` (OR), so a row passes if it satisfies *any one* constraint, not all of them — almost certainly `&` was intended. The extracted utility should accept an explicit combinator (`all`/`any`).
3. **Transformer plumbing** (`cont_transformers`, `cat_transformers`, `date_transformers`, `pre_proc_method`) is specific to the SynthVAE preprocessing convention; abstract to a single `inverse_transform: Callable[[pd.DataFrame], pd.DataFrame]`.
4. The top-up branch (line 480-486) silently drops `pre_proc_method` when calling `reverse_transformers`, defaulting back to "GMM" — a latent bug when using the "standard" scaler path; parameterisation removes the whole class of error.
5. `vae` should be generalised to any object exposing `generate(n) -> tensor/frame`; the `torch.cuda.is_available()` branching (lines 421-430) should live behind the model, not the sampler.
