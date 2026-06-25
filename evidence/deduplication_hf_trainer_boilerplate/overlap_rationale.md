# Deduplication Rationale: hf_trainer_boilerplate

**Repos:** ELM4PSIR, priv-lm-health
**Type:** Partial / Tangled (shared HuggingFace `Trainer` scaffolding, different task heads)

## What overlaps
Both repos hand-roll the same HuggingFace `Trainer` setup boilerplate around different
objectives:

- **ELM4PSIR** `language_modelling/transformers/run_lm_pretraining.py:279-494` — LM
  pre-training (MLM or CLM, switched on `args.mlm`).
- **priv-lm-health** `downstream_tasks/finetune_roberta_30dayReadmission.py:89-166` —
  binary sequence-classification fine-tuning (30-day readmission).

The common spine is substantial and near-identical in shape:
- `AutoTokenizer.from_pretrained(...)` with a `pad_token = eos_token` fallback;
- a `tokenize_function` mapped over the dataset;
- construction of a `TrainingArguments` object with the same family of knobs
  (`output_dir`, per-device batch sizes, `learning_rate`, `weight_decay`,
  `evaluation_strategy="steps"`, `eval_steps`, `save_steps`, `save_total_limit=2`,
  `load_best_model_at_end=True`, `warmup_steps`, logging strategy/dir);
- a `compute_metrics` callback;
- a `Trainer(...)` assembled from model + args + collator/datasets + metrics, then
  `trainer.train()`.

## What is shared vs bespoke
**Shared (extractable):** the tokenizer-load-with-pad-fallback, the `TrainingArguments`
factory (every field above is the same concept in both, just with different literal
values), and the `Trainer` assembly + `train()` call. This is pure HuggingFace plumbing
that both teams wrote independently.

**Bespoke (stays per call-site) — this is a tangled overlap, state it explicitly:**
- *Task head / model loader.* ELM4PSIR branches between `AutoModelForMaskedLM` and
  `AutoModelForCausalLM` on `args.mlm`; priv-lm-health uses a `model_init` returning
  `AutoModelForSequenceClassification(..., num_labels=2)`.
- *Data preparation.* ELM4PSIR's `group_texts` block-chunking (concatenate-then-split into
  `block_size` windows, `labels = input_ids.copy()`) and `DataCollatorForLanguageModeling`
  are LM-specific. priv-lm-health pads to `max_length` per example, with no collator.
- *Metrics.* ELM4PSIR computes masked vs causal token-accuracy (`compute_mlm_accuracy` /
  `compute_clm_accuracy`, with the CLM shift) plus `preprocess_logits_for_metrics`;
  priv-lm-health computes AUROC via softmax + `roc_auc_score` and adds an
  `EarlyStoppingCallback` and a final `trainer.predict` test-set evaluation.

## Deduplication proposal
Extract a shared `build_training_args(**overrides)` factory and a `build_trainer(model,
tokenizer, train_ds, eval_ds, compute_metrics, data_collator=None, callbacks=None)` helper
that capture the common `TrainingArguments` defaults (the two share most of them) and the
`Trainer` wiring. Each repo keeps its bespoke pieces — the model loader, the data-prep
(LM block-grouping vs classification tokenisation), and the metric callback — and passes
them in. Parameterise: the model/task class, the collator, the metric function, the
early-stopping callback, and any `TrainingArguments` fields that differ
(`metric_for_best_model`, `fp16`, `max_steps` vs `num_train_epochs`). Do **not** try to
merge the metric or data-prep logic; only the scaffolding.
