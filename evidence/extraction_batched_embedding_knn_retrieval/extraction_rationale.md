# Extraction Rationale: batched_embedding_knn_retrieval

## What
`txt-ray-align/evaluate.py` lines 77-211: `load_embeddings()` (concatenate pickled embedding
shards from a folder) and `get_sims_in_batches()` — a memory-bounded top-k cosine-similarity
retrieval that iterates over embedding "bank" shards on disk, computes query-vs-shard
similarity matrices, keeps the per-shard top-k, then merges shard-level top-k lists into a
global top-k with the matching metadata rows.

## Why it is reusable
This is a small, dependency-light (numpy/pandas/sklearn) approximate "vector store" for
cross-modal or semantic retrieval evaluation. Any project that embeds documents, report
sentences or images (semantic search over clinical coding, retrieval-augmented evaluation,
image-text alignment) needs exactly this shard-wise top-k merge when the bank does not fit in
memory. Nothing in the algorithm is chest-X-ray-specific.

## Tangled bespoke logic to parameterise
1. **DataFrame column contract hardcoded**: `embs_query["embs"]` and `embs_bank["embs"]`
   (lines 153, 169) and dedup on `subset="target"` (line 165). Parameterise `emb_col` and
   `dedup_col` (or accept plain numpy arrays + metadata frame).
2. **Shard discovery hardcoded to `**/*.pkl`** (lines 80, 163-164): expose the glob pattern and
   ideally support parquet as well.
3. **Similarity metric fixed to cosine** (line 170): inject the similarity function.
4. The surrounding `eval()` function (lines 214+) tangles this retrieval with
   CheXpert-label-based hit/precision/recall scoring (`add_chex`, `mimic_id`, `sents` columns)
   — that part is bespoke Logic and should stay behind, consuming the extracted retriever.
5. `max_k` is already a parameter; the magic `10` passed at line 375 of the caller should come
   from config.
