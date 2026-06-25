# Deduplication Rationale: clinical_text_embedding

**Repos:** mm-healthfair, txt-ray-align
**Type:** Partial / Tangled

## What overlaps
Both repositories independently implement "embed clinical free text with a HuggingFace
clinical-BERT checkpoint" with near-identical mechanics:

- **mm-healthfair** `src/utils/preprocessing.py:766-832` (`process_text_to_embeddings`):
  loads `emilyalsentzer/Bio_Discharge_Summary_BERT` via `AutoTokenizer`/`AutoModel`, moves to
  CUDA if available, tokenises sentences with `truncation=True, padding=True, max_length=128,
  return_tensors="pt"`, runs `torch.no_grad()` forward pass, mean-pools
  `last_hidden_state` over tokens to get sentence embeddings.
- **txt-ray-align** `models/wrapper.py:658-694` (`init_txt_model`) loads
  `emilyalsentzer/Bio_ClinicalBERT` (same model family, sibling checkpoint) via
  `AutoTokenizer`/`AutoModel`; `VariableSizeBERTModel.forward` (wrapper.py:57-81) performs
  attention-mask-weighted mean pooling of the sequence output — the same mean-pooled-BERT
  embedding, implemented more carefully. The inference path in `embeddings.py:286-300`
  tokenises with the identical argument set (`padding=True, truncation=True, max_length=128,
  return_tensors="pt"`), runs under `torch.no_grad()`, L2-normalises and moves to CPU/numpy.

## What is shared vs bespoke
**Shared (extractable):** checkpoint loading from a name, device placement, tokenise with
max_length 128, no-grad forward, mean pooling (mm-healthfair's unmasked mean is a degraded
version of txt-ray-align's masked mean — converge on the masked version), output to numpy.

**Bespoke (stays per-repo):**
- mm-healthfair: spaCy `en_core_sci_md` sentencisation, per-`subject_id` aggregation into a
  `{subject_id: [(sentence, embedding)]}` dict, the zero-vector `(768,)` fallback, and the
  averaging of sentence embeddings per note (note: lines 821-827 zip sentences with the
  *averaged* dimension array — a latent bug worth fixing during extraction).
- txt-ray-align: optional projection layer to `embed_dim`, layer-freezing controls, the CLIP
  contrastive wrapper, L2 normalisation for retrieval.

## Deduplication proposal
One `ClinicalTextEmbedder(model_name, pooling="masked_mean", max_length=128, device=None,
projection_dim=None)` utility; both repos become thin callers. Parameterise the model name
(both hardcode `emilyalsentzer/*` checkpoints), max token length, pooling strategy and
normalisation.
