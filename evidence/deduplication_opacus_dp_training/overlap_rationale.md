# Deduplication: Opacus Differential-Privacy Training Integration

## Shared functionality
Both repos solve "make this generative model's training loop (ε, δ)-differentially private using Opacus PrivacyEngine", with target-epsilon-driven noise calibration, gradient clipping, and live reporting of privacy spent.

- SynthVAE `VAE.py` lines 282-397 (`diff_priv_train`): constructs `PrivacyEngine(self, sample_rate=..., alphas=[1 + x/10 ...], noise_multiplier=..., max_grad_norm=C)` or the `target_epsilon/target_delta/epochs` variant, attaches it to the optimiser (line 314), then runs a *duplicated copy* of the non-private training loop (compare lines 316-397 with `train` lines 181-280 — they differ only in the engine setup). `get_privacy_spent` at 399-406.
- NHSSynth `modules/model/common/dp.py` lines 12-102 (`DPMixin`): wraps any `Model` via `privacy_engine.make_private_with_epsilon(module, optimizer, data_loader, epochs, target_epsilon, target_delta, max_grad_norm)` (lines 61-73), defaults `target_delta = 1/nrows` (line 45), and exposes ε-spent as a live training metric (lines 80-90).

Additionally, SynthVAE **vendors the entire Opacus library** into the repo (`SynthVAE/opacus/`, ~40 files: `privacy_engine.py`, `grad_sample/`, `layers/`, etc.) — a wholesale third-party copy committed as first-party code. It likewise vendors `rdt/` from SDV. NHSSynth consumes Opacus as a normal dependency.

## State: Tangled/Partial Overlap
**Shared:** PrivacyEngine construction targeting (ε, δ), max-grad-norm clipping, epsilon accounting surfaced to the user, early-stopped training afterwards.

**Bespoke:**
- SynthVAE: old Opacus 0.x `attach()` API; hardcoded RDP `alphas` list (line 300/308); the whole DP loop copy-pasted from `train()` (internal duplication); defaults `C=1e16`, `target_delta=1e-5`, `sample_rate=0.1` baked into the signature.
- NHSSynth: modern Opacus 1.x `make_private_with_epsilon`; mixin composition so any model gains DP (`DPVAE(DPMixin, VAE)`, `dpvae.py` lines 9-55 — including selective privatisation of the decoder only, lines 36-47); `secure_mode` support.

## Recommendation
NHSSynth's `DPMixin` is the deduplicated form and should be the shared utility (after fixing the `Model.setup_device` CPU-override bug it relies on). SynthVAE's vendored `opacus/` and `rdt/` trees should be deleted in favour of pinned dependencies — they are the largest dead-weight duplication found in this group (~10k lines of third-party code).
