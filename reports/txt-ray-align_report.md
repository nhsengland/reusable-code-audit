# Audit Report: txt-ray-align

## Overview
txt-ray-align aligns chest X-ray images with their radiology report text
(MIMIC-CXR / CheXpert), training a CLIP-style image-text model. The repo spans
report-section extraction (`data/section_parser.py`, `data/create_section_files.py`),
text cleaning (`chexpert/loader/load.py`), image resizing and augmentation
(`data/resize.py`, `data/text_image_dm.py`), dataset subsetting (`data/get_subset.py`),
sentence embedding (`embeddings.py`, `wrapper.py`) and batched retrieval
evaluation (`evaluate.py`). It is a script/module collection driven by argparse
rather than a packaged library; concerns are spread across reasonable file
boundaries but utilities are not isolated from CLI entry points.

## SUL Adherence: Medium
There is a sensible file-level separation of concerns (parsing, cleaning,
resizing, embedding, evaluation each have their own module), which lifts it above
notebook-only repos. But the code is argparse-script-shaped: reusable logic
(`get_sims_in_batches`, the section parser, the resizer Dataset) is interleaved
with `__main__` blocks, file globbing and path assumptions, so extraction requires
disentangling the helper from its CLI driver. Dataset specifics (CheXpert/MIMIC-CXR
folder layout, ResNet normalisation constants) are embedded rather than configured.
Hence Medium.

## Extraction Candidates
- **Radiology report section parser** — `evidence/extraction_radiology_report_section_parser/`.
  `section_parser.py` + `create_section_files.py` (adapted from MIT-LCP
  mimic-code) split reports into findings/impression sections. Parameterise: pass
  the section-header vocabulary and the input/output roots as arguments.
- **Recursive image-folder resizer** — `evidence/extraction_recursive_image_folder_resizer/`.
  `resize.py` (lines 28-98) DataLoader-parallelised bulk resize. Parameterise:
  expose the glob pattern (`**/*.jpg`), target size and output root.
- **Batched embedding kNN retrieval** — `evidence/extraction_batched_embedding_knn_retrieval/`.
  `evaluate.py` (lines 77-211) `load_embeddings` + `get_sims_in_batches`
  memory-bounded top-k cosine similarity. Parameterise: take embedding arrays and
  batch size as arguments rather than reading pickled shards from a fixed folder.

## Hardcoding Flags
- CheXpert/MIMIC-CXR specifics: `--chexpert_folder` path assumptions; the MIMIC-CXR
  patient-folder hierarchy (`p00`…`p19`) walked in `create_section_files.py`.
- Image constants: ResNet50 normalisation mean/std `(0.485,0.456,0.406)/(0.229,0.224,0.225)`
  and the commented CLIP stats in `text_image_dm.py`; default `resize_to=256`;
  `**/*.jpg` glob hardcoded in the resizer.
- Output naming: split files written as `train.csv`/`val.csv`/`test.csv` into a
  `len{N}_train{f}_test{f}` folder; split key fixed to `study_id`.

## Deduplication Candidates
- **MIMIC ingestion & standardisation** — `evidence/deduplication_mimic_ingestion_standardisation/`.
  txt-ray-align's `create_section_files.py` is one of five repos in this central
  case (with mm-healthfair, priv-lm-health, priv-lm-health-extended, SynthVAE);
  its bespoke contribution is radiology section extraction over the CXR hierarchy.
- **MIMIC free-text cleaning** — `evidence/deduplication_mimic_free_text_cleaning/`.
  `chexpert/loader/load.py` `clean` overlaps with **mm-healthfair**'s `clean_notes`
  on the shared whitespace-collapse step.
- **Image pre-processing & augmentation** — `evidence/deduplication_image_preprocessing_augmentation/`.
  `text_image_dm.py`/`resize.py` overlap with **LIME-XAI-Facial-Disease-Classification**'s
  Keras augmentation pipeline.
- **Train/val/test split with CSV export** — `evidence/deduplication_train_test_split_csv/`,
  with **mm-healthfair**.
- **Clinical text embedding** — `evidence/deduplication_clinical_text_embedding/`,
  with **mm-healthfair**.
- **Random seed setting** — `evidence/deduplication_random_seed_setting/`.
