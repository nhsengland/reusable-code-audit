# Extraction Rationale: numba_binary_powerset_encoding

## What
`hypergraph-mm/hypmm/utils.py` lines 112–511 — a Numba-accelerated toolkit for
binary set encoding and powerset/worklist generation:

- `binary` / `num_2_disease` — convert integers to fixed-width binary arrays and
  back to the indexed set of "on" columns (a `numpy.binary_repr` reimplemented to
  be JIT-compatible).
- `compute_bin_to_int`, `compute_integer_repr`, `comp_pwset_prev` — map rows of a
  binary flag matrix to unique integer set-identifiers and accumulate prevalence
  counts over set-membership integers.
- `create_empty_list`, `create_set_union`, `concatenate`, `generate_powerset` —
  Numba-friendly set/list primitives and a JIT powerset generator (with
  options to include the full set and drop singletons).
- `reduced_powerset`, `compute_worklist`, `comp_edge_worklists` — pure-Python
  bounded powerset (`itertools`) and construction of padded integer "worklists"
  encoding hyperedges for the Numba kernels, under `power` / `exclusive` /
  `progression` weighting schemes.

## Why it is reusable
This is general combinatorial/bit-encoding machinery: representing rows of a
binary indicator matrix as integers, enumerating bounded powersets, and packing
variable-length sets into fixed-width padded arrays for Numba. None of it is
intrinsically clinical — it applies to any binary feature matrix where set
membership and co-occurrence enumeration matter. The Numba JIT primitives
(`create_empty_list`, `concatenate`, JIT `generate_powerset`) are independently
valuable since Numba lacks them natively.

## Tangled bespoke logic to parameterise
1. **`disease`-flavoured naming**: `num_2_disease`, `disease_cols`, `n_diseases`,
   the `<U24` disease-name dtype, and "hyperedge/hyperarc" comments are
   domain-specific labels over generic functionality. Rename to neutral terms
   (`num_2_set`, `col_names`, `n_cols`) for a reusable library.
2. **`width=13` default** in `binary` (line 11) is a dataset-specific magic
   number (13 diseases). Remove the default or make it required.
3. **`-1` sentinel** for padding in worklists (`elem[elem != -1]`, `dummy_var`
   construction) is an implicit contract spread across functions — document and
   centralise the pad value.
4. **Contribution-type strings** `"power"`/`"exclusive"`/`"progression"` in
   `comp_edge_worklists` carry hypergraph-MM-specific semantics; the `power`
   branch builds the full powerset while the others just list observed edges —
   keep the branching but expose it cleanly.
5. **`2**n_diseases` allocation** in `comp_pwset_prev`/`compute_integer_repr`
   grows exponentially; document the column-count ceiling as a usage constraint.
6. No paths, credentials, trust codes or dataset names — no hardcoding flags.
