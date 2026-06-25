# Extraction: Generic PyTorch Model Scaffold with Opt-In Differential Privacy (`Model` + `DPMixin`)

## What it is
Two small, composable classes in NHSSynth:
- `modules/model/common/model.py` (lines 18-191): an abstract `Model(nn.Module)` that standardises tabular-model training infrastructure — DataLoader construction from a DataFrame (with optional one-hot conditional vector), device selection, save/load, live tqdm metric dashboards (`_start_training`/`_record_metrics`/`_generate_metric_str`), early stopping with relative patience delta (`_check_patience`), and a declarative `get_args`/`get_metrics` contract used by the CLI.
- `modules/model/common/dp.py` (lines 12-102): `DPMixin`, which converts *any* such `Model` into a differentially private one by wrapping module/optimiser/dataloader with Opacus `PrivacyEngine.make_private_with_epsilon`, defaulting `target_delta = 1/nrows`, and adding a live "epsilon spent" metric.

## Why it is reusable
This is Structural code in SUL terms: a framework-quality training scaffold with zero dataset- or model-specific logic. Within NHSSynth alone it is reused by VAE, GAN, (DP)CTGAN and DPVAE — DP is added by multiple inheritance (`class DPVAE(DPMixin, VAE)`), which is exactly the composition pattern other NHS teams training torch models on sensitive data need. It is the direct, untangled successor of SynthVAE's `diff_priv_train` (where the Opacus integration was copy-pasted into each training method), demonstrating the value of the abstraction.

## Bespoke logic that must be parameterised/abstracted
1. **Bug to fix on extraction:** `setup_device` (model.py lines 88-95) sets `self.device = torch.device("cpu")` unconditionally on the last line, so `use_gpu=True` never takes effect (the cuda assignment is immediately overwritten). The early-return/else structure must be corrected.
2. **`MetaTransformer` coupling** (model.py lines 15, 62-65): `multi_column_indices`/`single_column_indices` are pulled from an NHSSynth `MetaTransformer`. Accept these index lists (or a thin protocol/interface) directly so the scaffold does not depend on the dataloader module.
3. **Hardcoded training cosmetics**: tqdm refresh interval `0.5`s (line 169), patience delta `self._min_metric / 1e4` (line 179) and `batch_size=32` default should be constructor parameters.
4. **DPMixin defaults** (`target_epsilon=3.0`, `max_grad_norm=5.0`) are policy choices; keep as parameters but document that delta defaults to `1/nrows`.
5. The `add_spaces_before_caps` import from `nhssynth.common.strings` is a trivial helper that should travel with the scaffold or be inlined.
