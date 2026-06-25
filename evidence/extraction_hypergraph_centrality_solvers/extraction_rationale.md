# Extraction Rationale: hypergraph_centrality_solvers

## What
`hypergraph-mm/hypmm/centrality_utils.py` lines 1–303 — a self-contained,
Numba-accelerated toolkit of directed-hypergraph centrality solvers:

- `degree_centrality` — weighted in/out node-degree and edge-degree centrality
  for a directed hypergraph given tail/head incidence matrices and edge/node
  weights.
- `iterate_pagerank_vector`, `matrix_mult`, `iterate_eigencentrality_vector` —
  hand-written Chebyshev/power-iteration kernels computing `vP` and
  `M·W·Mᵀ·v` (with diagonal removed) for eigenvector/PageRank centrality.
- `is_irreducible` — checks irreducibility of a stochastic matrix via the matrix
  exponential.
- `generate_irreducible_ptm` — Brin–Page damping transform converting a reducible
  row-stochastic matrix into an irreducible one.

## Why it is reusable
These are general directed-hypergraph / Markov-chain linear-algebra primitives.
The mathematics (degree centrality, eigenvector/PageRank iteration, irreducibility
testing, damping-factor regularisation) is wholly domain-independent — nothing in
these functions references diseases, patients or any dataset. They operate purely
on incidence matrices, weight vectors and stochastic matrices, and are already
JIT-compiled and documented. This is among the cleanest extraction candidates in
the batch: a reusable `hypergraph_centrality` numerical library.

## Tangled bespoke logic to parameterise
Minimal — the functions are already generic. On extraction:
1. **Domain-flavoured docstrings/identifiers**: parameters named `n_diseases`,
   `disease`-oriented comments, and the disease-progression narrative in
   `generate_irreducible_ptm`/`is_irreducible` should be renamed to neutral terms
   (`n_nodes`, "states") for a general-purpose library.
2. **Hardcoded damping** in `generate_irreducible_ptm`: `alpha = 1 - 1e-6` is set
   inside the function and the `alpha_ord=5` argument is unused (lines 265, 295).
   Expose `alpha` as the actual damping parameter and drop the dead argument.
3. **Performance/dtype assumptions**: incidence matrices assumed `np.uint8`,
   weights `np.float64`; keep these as documented contracts. The naive triple
   loops are deliberate for Numba — preserve, but note `matrix_mult` allocates a
   full `np.zeros_like(matrix)` which is a diagonal-scaling operation that could
   be tightened.
4. No paths, codes, or dataset names present — no hardcoding flags.
