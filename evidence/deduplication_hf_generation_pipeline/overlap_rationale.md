# Deduplication Rationale: hf_generation_pipeline

**Repos:** priv-lm-health-extended (internal duplication — two modules)
**Type:** Near-identical copy/paste

## What overlaps
Both files define the same `Pipeline` class — a thin wrapper around a HuggingFace causal
LM that loads a checkpoint, configures a left-padded tokenizer with the EOS token as pad,
and exposes a `generate_batches` generator that chunks input, runs batched sampling
generation, and yields either full text or just the newly generated continuation.

- **`misc/attacker_LM/run.py:20-134`** (`Pipeline` + `make_chunk`)
- **`memorisation/run_metrics.py:25-114`** (`Pipeline` + `make_chunk`)

The `__init__` and `generate_batches` signatures and bodies are essentially identical:
same `model_class=AutoModelForCausalLM` default, same `padding_side="left"`,
`cache_dir=os.environ.get("HF_HOME")`, the same `pad_token = eos_token` /
`generation_config.pad_token_id` setup, and the same generation defaults
(`batch_size=48, temperature=0.9, top_k=50, top_p=0.9, max_new_tokens=200`). The
prompt-end offset trick (decode the inputs to measure prompt length, then slice it off the
decoded output) is copied verbatim. `make_chunk` is duplicated character-for-character in
both files.

## What is shared vs bespoke
**Shared (extractable, the bulk):** the entire `Pipeline` class and `make_chunk`. The
`run_metrics` copy is a strict superset of the `attacker_LM` copy — it adds
`torch_dtype=torch.float16` and `low_cpu_mem_usage=True` to the constructor and the model
load. Converging on the superset loses nothing.

**Bespoke (stays per call-site):** the surrounding experiment scaffolding, which lives
outside the duplicated block —
- `attacker_LM/run.py`: the `PromptScorer` (beta/gamma-weighted membership + overlap
  score), the zephyr-template `make_init_attack_prompt` / `make_attack_prompt` builders,
  and `compute_rougeL`.
- `run_metrics.py`: `make_prefix_suffix` (the Kassem-et-al. 33/67 prefix-suffix cutoff)
  and the memorisation-metric harness.

These are genuinely distinct experiment logic and should not be merged — only the
generation wrapper underneath them.

## Deduplication proposal
Promote a single `Pipeline` (the `run_metrics` superset variant, with `torch_dtype` and
`low_cpu_mem_usage` as parameters that default to today's values) and `make_chunk` into a
shared `generation` module; both experiment scripts import it. Parameterise the model id,
device/device-map, dtype, and the generation hyperparameters (already arguments). Note this
also overlaps with the single-file extraction candidate
`evidence/extraction_hf_batch_generation_pipeline/` — the extraction there targets the same
`run_metrics` class; this dedup case is the in-repo justification for lifting it once.
