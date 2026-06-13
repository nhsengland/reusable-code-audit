# Deduplication Rationale: reference_model_mia_scoring

**Repos:** priv-lm-health-extended, priv-lm-health
**Type:** Partial / Tangled (same membership-inference primitive — per-sequence likelihood
scoring under a target vs reference model — two implementations)

## What overlaps
Both repos implement the core membership-inference primitive of scoring a piece of text by
its likelihood/loss under a target model and (in the reference-based variant) calibrating
that against a second reference model.

- **priv-lm-health-extended** `memorisation/mimir.py:150-240`: a `Model` base with a
  no-grad `get_ll` (negative mean token log-probability), `load_model_properties` (resolve
  `max_length` from the config, set `stride = max_length // 2`), and `ReferenceModel` /
  `LanguageModel` subclasses that load causal LMs (4-bit, `device_map="auto"`,
  `cache_dir=os.environ["HF_HOME"]`). `LanguageModel.get_ref` computes
  `get_ll(text) - ref_model.get_ll(text)` — the classic reference-calibrated MIA score.
- **priv-lm-health** `privlm/mi_attack.py:149-198`: `return_lr` (pseudo-log-likelihood
  per sequence via a `MaskedLMScorer`, batched) and `return_loss` (per-sentence masked-LM
  loss from `RobertaForMaskedLM`, tokenising with `max_length=256, padding="max_length"`).

Both compute a **per-sequence membership statistic from a language model's likelihood/loss**
and feed it into the same downstream attack. That intent is shared.

## What is shared vs bespoke
**Shared (conceptually):** "load a target LM, score each sequence by its
likelihood/loss, optionally calibrate against a reference model". The reference-vs-target
difference scoring (`get_ref`) and the per-sequence loss loop (`return_loss`) are the same
membership signal computed two ways.

**Bespoke (tangled — state explicitly):**
- *Model family.* extended targets **causal** LMs (`AutoModelForCausalLM` /
  `AutoPeftModelForCausalLM`, 4-bit, PEFT-aware) and uses token-probability log-likelihood;
  priv-lm-health targets **masked** LMs (RoBERTa, `MaskedLMScorer` pseudo-log-likelihood
  and direct MLM loss). The scoring maths differs accordingly (autoregressive LL vs PLL/MLM
  loss).
- *extended:* the `silo`/`balanced`-name special-casing in `load_model_properties`, the
  4-bit/offload load options, and the stride windowing are bespoke.
- *priv-lm-health:* the `minicons` `MaskedLMScorer` dependency, the `max_length=256`
  tokenisation, and the per-batch `torch.cuda.empty_cache()` are bespoke.

## Deduplication proposal
Define a small `ScorerModel` interface with `get_ll(text) -> float` and an optional
`get_ref(text, ref_model) -> float` calibration, with two concrete implementations
(causal-LM and masked-LM/PLL). The reference-calibration arithmetic
(`score = ll_target - ll_ref`) is genuinely shared and should live once in the interface.
Parameterise: the model class/family (causal vs masked), `max_length`/stride, quantisation
and PEFT flags, and the cache directory (both hardcode `os.environ["HF_HOME"]`). Keep the
attack-level statistic aggregation out of this primitive — that belongs with the MIA
evaluation code (`evidence/extraction_mia_evaluation_metrics/`).
