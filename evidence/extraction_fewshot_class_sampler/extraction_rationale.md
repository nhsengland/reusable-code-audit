# Extraction Candidate: Few-shot, class-balanced dataset sampler

## What it is
The `FewShotSampler` class from ELM4PSIR
(`classification_tasks/data_utils/dataset_processing.py:14-281`), together with the small
label-handling helpers in the same module (`encode_classes`, `convert_to_binary_classes`,
`balance_dataset`). `FewShotSampler` supports two sampling strategies — a fixed total
number of examples (`num_examples_total`) or a fixed number per label
(`num_examples_per_label`) — with optional, separately-sized sampling of a dev/validation
split, seeded reproducibility via `np.random.RandomState`, and support for both
`torch.utils.data.Dataset` (returns `Subset`) and plain `List`/DataFrame inputs.

## Why it is reusable (Utility)
Class-stratified few-shot subsampling is a generic experimental need for any text- or
tabular-classification project doing low-resource or data-efficiency studies — it is in no
way specific to patient-safety incident reports. The implementation is already carefully
written: it validates mutually-exclusive strategy arguments, warns when a label has too few
examples, and reproducibly shuffles. The companion helpers (`encode_classes` builds the
`idx_to_class` / `class_to_idx` maps; `convert_to_binary_classes` thresholds an N-class
label into 0/1) are equally generic label utilities.

## What must be parameterised to untangle it
- **`label_col`** — already a constructor argument (default `"label"`); good. Ensure all
  call paths honour it (a couple of internal asserts still hardcode the string `'label'`
  in their error messages — cosmetic, but the logic uses `self.label_col`).
- **`balance_dataset`** — currently hardcodes `groupby("hospital_expire_flag")` and takes a
  stray `self` first argument despite being module-level. Generalise: pass the grouping
  column as a parameter and drop the `self`. This is the only domain-specific (MIMIC
  mortality flag) coupling in the module.
- **Fix the dev-sampling TODO** — `_sample` notes it uses `num_examples_per_label` rather
  than `num_examples_per_label_dev` for the dev split in one branch; resolve on extraction.
- Otherwise self-contained: depends only on numpy and torch `Subset`; no project imports
  in the core sampler.
