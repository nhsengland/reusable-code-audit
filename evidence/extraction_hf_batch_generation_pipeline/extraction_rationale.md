# Extraction Candidate: Batched HuggingFace text-generation pipeline

## What it is
The `Pipeline` class and `make_chunk` helper from priv-lm-health-extended
(`memorisation/run_metrics.py:25-114`). `Pipeline` wraps a causal LM: it loads a checkpoint
and a left-padded tokenizer (EOS as pad token), placing the model on a device or via
`device_map`, with `torch_dtype` and `low_cpu_mem_usage` controls. Its `generate_batches`
generator chunks an input list, runs batched sampling generation
(`do_sample`/`temperature`/`top_k`/`top_p`/`repetition_penalty`/`max_new_tokens`), and
yields either the full decoded text or just the generated continuation (computed by
measuring the decoded prompt length and slicing it off).

## Why it is reusable (Utility)
Batched generation over a list of prompts — with correct left-padding, pad-token handling,
and prompt-stripping of the output — is generic LLM infrastructure needed by any project
that runs a local HuggingFace model over many inputs. This wrapper is more careful than the
ad-hoc `model.generate` loops found elsewhere: it handles the pad-token-missing case, the
prompt-end offset, and memory-friendly loading.

## What must be parameterised to untangle it
- **`cache_dir`** — defaults to `os.environ.get("HF_HOME")`; keep as an argument so the
  utility has no environment-variable dependency baked in.
- **Generation hyperparameters** — already arguments with defaults; expose as-is.
- Decouple `make_chunk` (a trivial list-chunking generator) into the same shared module so
  it is not redefined per script.
- The bespoke `make_prefix_suffix` (Kassem-et-al. 33/67 prefix-suffix cutoff) that sits
  alongside in `run_metrics.py` is **memorisation-experiment logic, not part of the
  generation utility** — leave it behind.

## Relationship to deduplication
This is the single-file extraction of the same class that appears, copy-pasted, in
`evidence/deduplication_hf_generation_pipeline/` (also in `misc/attacker_LM/run.py`).
Extract the `run_metrics` superset variant once and both internal call-sites collapse onto
it.
