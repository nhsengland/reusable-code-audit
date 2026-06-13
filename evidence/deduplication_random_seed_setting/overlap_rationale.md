# Deduplication Case: Random Seed Setting

**What it does:** Sets the random seed across the relevant random number generators (`numpy`, `torch`, and — in the NHSSynth variant — the Python `random` module) to make experiment runs reproducible.

**Why it is an overlap:** This is a **full semantic overlap**. `SynthVAE/utils.py` (lines 14–16) and `NHSSynth/src/nhssynth/common/common.py` (lines 10–20) both define a function named `set_seed` with identical intent and near-identical implementation. NHSSynth grew out of the SynthVAE work, and its version is simply the matured form of the same utility: it adds type hints, a docstring, an `Optional` guard so that passing no seed is a no-op, and seeding of Python's built-in `random` module. SynthVAE's version misses `random.seed()`, which is a latent reproducibility bug — code paths using the standard library RNG are not controlled.

Beyond these two repos, the same intent appears inline (unwrapped in any function) across the wider batch — e.g. `np.random.seed`/`torch.manual_seed` calls scattered through training scripts in ELM4PSIR, txt-ray-align and mm-healthfair — meaning every project re-solves reproducibility independently and inconsistently.

**Consolidation plan:** Promote the NHSSynth version (the most complete) into a shared `nhs-analytics-common` utility package and delete the SynthVAE copy. No bespoke logic is tangled here — this is a pure utility and the easiest possible consolidation win. Optionally extend it to seed CUDA (`torch.cuda.manual_seed_all`) and set `PYTHONHASHSEED`, which none of the current copies do.
