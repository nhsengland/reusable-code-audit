# Deduplication Case: Image Pre-processing & Augmentation

**What it does:** Takes raw images off disk and turns them into model-ready
tensors/arrays: resize to a fixed input size, rescale/normalise pixel values, and
(for training) apply geometric augmentation. Two repos implement this
independently with different frameworks:

| Repo | File | Shared intent | Bespoke / tangled logic |
|---|---|---|---|
| LIME-XAI-Facial-Disease-Classification | `Investigations/ffhqrffInceptionv3.ipynb` (cell 6) and `Explain_working_con.ipynb` (cell 5) | Resize to a square input, rescale pixels, apply a standard augmentation suite (rotation/shift/shear/zoom/flip) | Keras `ImageDataGenerator` + `flow_from_directory`; `target_size=(299,299)` and the `(x-0.5)*2` Inception-specific rescale; `class_mode="binary"`; `batch_size=4` |
| txt-ray-align | `data/text_image_dm.py` (lines 71-85) and `data/resize.py` (lines 28-49) | Resize, convert to tensor, normalise with ImageNet-style channel stats, apply a random resized crop for training | torchvision `T.Compose`; ResNet50 mean/std `(0.485,0.456,0.406)/(0.229,0.224,0.225)`; `RandomResizedCrop(scale=(resize_ratio,1.0), ratio=(1.0,1.0))`; CLIP-style stats left commented as an alternative |

**Why it is an overlap:** Both implement the same conceptual pipeline — *load →
resize → rescale/normalise → (train-time) augment* — but this is a **partial,
tangled overlap** rather than copy-paste duplication. The recipe is shared; the
framework (Keras vs torchvision) and the magic constants are bespoke.

**Shared vs bespoke:**
- *Shared (extractable):* the pipeline shape — a configurable resize size, a
  choice of normalisation scheme, and a toggle between a train transform (with
  augmentation) and an eval transform (deterministic). This is the reusable core.
- *Bespoke (must be parameterised):* the **input resolution** (299 for Inception,
  256/variable for txt-ray-align); the **normalisation constants** (Inception
  `(x-0.5)*2` vs ResNet/ImageNet channel mean-std vs the commented CLIP stats);
  the **augmentation parameter block** (rotation/shift/shear/zoom/flip ranges, or
  `RandomResizedCrop` scale/ratio); the **batch size** and **class mode**; and the
  **framework backend** itself.

**Consolidation note:** A shared helper should expose `image_size`,
`normalisation` (a named preset such as `inception`/`imagenet`/`clip` or an
explicit mean/std pair), and an `augment: bool`/augmentation-config argument, with
the framework selected behind a thin adapter. Because the two repos use different
ML stacks, full code-level deduplication is lower-value than agreeing a single
parameterised transform spec; the win is removing the hardcoded resolutions and
normalisation magic numbers from the model code. Note that txt-ray-align's
`resize.py` is also a standalone extraction candidate
(`evidence/extraction_recursive_image_folder_resizer/`) and the LIME notebook's
transfer-learning cell feeds `evidence/extraction_keras_transfer_learning_finetune/`.
