# Extraction Candidate: Clinical free-text cleaning pipeline

## What it is
The `clean_data` routine from ELM4PSIR (`utils/prepare_classification_datasets.py:72-134`
and the sibling `utils/prepare_notes_for_lm.py:70-138`), driven by the `LMTextData`
configuration class (`prepare_classification_datasets.py:31-70`). Given a notes DataFrame
and a text column, it: strips bracketed de-identification placeholders (`r"\[.*?\]"`),
applies an ordered list of `(original, replacement)` regex/string substitutions
(`replacement_map`), removes a list of "admin language" tokens, lower-cases and trims, then
collapses repeated whitespace and drops NA rows.

## Why it is reusable (Utility)
Normalising messy clinical free text — placeholder removal, boilerplate/admin-token
stripping, punctuation standardisation, whitespace collapse, lower-casing — is a recurring
need across every NLP-on-clinical-notes project in this batch. The recipe is generic;
nothing about it is specific to incident reports beyond the *data* (the replacement map and
admin-token list) passed in. It is the same family of cleaning seen in
`evidence/deduplication_free_text_cleaning/` and the survey/clinical cleaners elsewhere,
and is worth promoting to a shared, well-tested helper rather than re-copied per project.

## What must be parameterised to untangle it
- **Text column name** — currently read from `self.text_col`; make it an argument.
- **`replacement_map`** — the ordered substitution list must be passed in, not pulled from
  `self`; this is the project-specific data.
- **`admin_language`** — the boilerplate token list, likewise an argument (default `None`).
- **Flags** — `remove_punctuation` / bracket-stripping toggle (the two copies disagree on
  the default; expose it explicitly).
- **Bug to fix on extraction:** the final whitespace collapse uses `re.sub(r"\\s+", " ",
  x)` — a double-escaped pattern that matches a literal `\s+`, not whitespace. Fix to
  `r"\s+"` in the extracted version.
- Decouple from the `LMTextData` class so the cleaner is a free function operating on a
  DataFrame + config, with no dependency on the surrounding sampling/save scaffolding.
