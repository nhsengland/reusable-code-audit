# Extraction Rationale: keras_transfer_learning_finetune

## What
`LIME-XAI-Facial-Disease-Classification/Investigations/ffhqrffInceptionv3.ipynb` code cell 6
(duplicated verbatim in `ffhqrff_Incepv3_con.ipynb` code cell 6, differing only in the initial
learning rate 0.001 vs 0.01 and Drive folder): a two-phase Keras transfer-learning recipe —
ImageNet-pretrained InceptionV3 base, GlobalAveragePooling + Dense(1024) + sigmoid head,
phase 1 trains the head with the base frozen, phase 2 unfreezes the top two inception blocks
(layers 249+), with `ImageDataGenerator` augmentation and directory-based binary generators.

## Why it is reusable
Beyond generic boilerplate, the *recipe* (head-then-partial-unfreeze with a documented layer
boundary, paired augmentation/eval generators) is the standard pattern for small medical-image
datasets and is already duplicated verbatim across two notebooks in this one repository —
direct evidence of copy-paste reuse that a single parameterised
`build_finetune_model(base_arch, n_classes, unfreeze_from, ...)` function would eliminate.
Flagged with the caveat that generic Keras training boilerplate may also be handled by the
central boilerplate workstream; the unfreeze-boundary recipe is the part worth keeping.

## Tangled bespoke logic to parameterise
1. **Google Drive paths hardcoded** (cells 1, 5, 13): `/content/gdrive/My Drive/Inceptionv3/...`
   train/validation/test directories and the saved model path
   `/content/gdrive/MyDrive/inceptionv3.h5`. Parameterise data root and output path.
2. **Unfreeze boundary `249`** is InceptionV3-specific (cell 6); derive from a named layer or
   accept per-architecture config.
3. **Binary head hardcoded**: `Dense(1, activation="sigmoid")` and
   `loss="binary_crossentropy"`, `class_mode="binary"` — parameterise `n_classes`.
4. **Magic training numbers**: `batch_size=4`, `steps_per_epoch=15`, `epochs=10`,
   `validation_steps=10`, `target_size=(299, 299)`, augmentation values — surface in config.
5. **Inconsistent optimiser/learning rate**: phase 1 compiles with `RMSprop(0.001)` (or `0.01`
   in the `_con` variant) but is immediately recompiled with `Nadam()` before any training —
   a latent bug that parameterisation would force into the open.
6. Note: subsequent cells 15-19 reference undefined variables (`test_data_generator`,
   `nb_validation_samples`, `plot_confusion_matrix`, `tensorboard_callback`) and the literal
   `target_names = ["Cats", "Dogs"]` — dead copy-paste from a tutorial; exclude from extraction.
