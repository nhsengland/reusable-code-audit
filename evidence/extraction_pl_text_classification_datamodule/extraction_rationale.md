# Extraction Candidate: PyTorch Lightning text-classification DataModule

## What it is
The `IncidentDataset` and `IncidentDataModule` classes from ELM4PSIR
(`classification_tasks/models/transformer_plms/hf_transformer_classifier.py:83-169`).
`IncidentDataset` is a `torch.utils.data.Dataset` that wraps a pandas DataFrame with `text`
and `label` columns, tokenises each row with a HuggingFace tokenizer
(`padding="max_length", truncation=True, max_length=...`, returning flattened
`input_ids`/`attention_mask` and a `labels` tensor). `IncidentDataModule` is a
`pl.LightningDataModule` that holds train/valid/test DataFrames and a tokenizer, builds the
three datasets in `setup`, and exposes the standard `train_dataloader` /
`val_dataloader` / `test_dataloader` (train shuffled, batch size and max token length
configurable).

## Why it is reusable (Utility)
This is boilerplate PyTorch-Lightning + HuggingFace plumbing for any DataFrame-backed text
**classification** task — load three splits, tokenise to a fixed length, serve batched
loaders. None of it is specific to patient-safety incident reports beyond the class names; it
is the generic "text + label DataFrame → Lightning DataModule" adapter that recurs in every
transformer-classification project.

## What must be parameterised to untangle it
- **Column names** — `__getitem__` hardcodes `data_row["text"]` and `data_row["label"]`
  despite `IncidentDataset.__init__` accepting a `label_col` argument (which is stored but
  never used). Wire `label_col` through, and add a `text_col` argument.
- **Rename for generality** — `IncidentDataset`/`IncidentDataModule` → a neutral
  `TextClassificationDataset` / `TextClassificationDataModule`.
- **Already parameterised** — `tokenizer`, `max_token_len` (default 512), `batch_size`
  (default 2 — raise the default), and the three split DataFrames; keep as arguments.
- **Tidy-ups** — drop the unused `mode` argument and the commented-out `encode_plus` block;
  optionally expose `shuffle` and `num_workers` for the loaders. No project imports beyond
  torch / lightning / transformers, so extraction is clean.
