# Audit Report: LIME-XAI-Facial-Disease-Classification

## Overview
LIME-XAI-Facial-Disease-Classification is a notebook-only exploration that
fine-tunes an InceptionV3 transfer-learning model to classify facial-disease
images and then explains predictions with a from-scratch LIME superpixel
implementation. All code lives in Colab-style Jupyter notebooks under
`Investigations/` (e.g. `ffhqrffInceptionv3.ipynb`, `ffhqrff_Incepv3_con.ipynb`,
`Explain_working_con.ipynb`); there is no package, no module boundaries and no
tests. It is the least structured repo in the batch.

## SUL Adherence: Low
There is effectively no Structure/Utility/Logic separation: structural setup
(data generators, model definition), utility helpers (image loading/resize) and
core logic (training loop, LIME explainer) are all inlined in notebook cells,
several duplicated verbatim across notebooks (the augmentation cell is identical
in `ffhqrffInceptionv3.ipynb` and `ffhqrff_Incepv3_con.ipynb`). Reuse demands
lifting code out of cells entirely. Hence Low.

## Extraction Candidates
- **LIME superpixel explainer** — `evidence/extraction_lime_superpixel_explainer/`.
  `Explain_working_con.ipynb` (cells 5-19) a complete from-scratch image LIME.
  Parameterise: take the model `predict` callable, image, number of perturbations
  and superpixel algorithm as arguments rather than module-level globals.
- **Keras transfer-learning fine-tune** — `evidence/extraction_keras_transfer_learning_finetune/`.
  `ffhqrffInceptionv3.ipynb` (cell 6, duplicated in `ffhqrff_Incepv3_con.ipynb`)
  the InceptionV3 generator + fit block. Parameterise: expose base model, input
  size, augmentation config, class mode and train/val directories.

## Hardcoding Flags
- Absolute Google Drive paths: `train_dir = "/content/gdrive/My Drive/Incepv3con/train"`
  (`ffhqrff_Incepv3_con.ipynb`) — Colab-specific, non-portable.
- Local relative test image: `../data/test.jpeg` read directly in the explain
  notebook.
- Magic image constants: `target_size=(299,299)`, Inception rescale `(x-0.5)*2`,
  `batch_size=4`, `class_mode="binary"`, fixed augmentation ranges
  (rotation 40, shift/shear/zoom 0.2, horizontal flip), `steps_per_epoch=15`,
  `epochs=10` — all inline literals.

## Deduplication Candidates
- **Image pre-processing & augmentation** — `evidence/deduplication_image_preprocessing_augmentation/`.
  The Keras `ImageDataGenerator`/`flow_from_directory` resize-rescale-augment
  pipeline overlaps with **txt-ray-align**'s torchvision transform in
  `text_image_dm.py`/`resize.py` — a partial, tangled overlap (shared recipe,
  different framework and magic constants). No overlap with the MIMIC-focused
  repos, as this project handles facial-disease images rather than clinical
  tabular/text data.
