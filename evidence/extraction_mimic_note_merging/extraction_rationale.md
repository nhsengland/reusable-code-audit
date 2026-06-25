# Extraction Candidate: MIMIC-III/IV note merging and matching utilities

## What it is
Two complementary pieces from priv-lm-health-extended:
- **`data_processing/base_datasets/mimic.py:1-71`** (`MIMIC.process`) — reads the MIMIC-III
  and MIMIC-IV note CSV exports, filters MIMIC-III to rows with a HADM_ID, selects the
  relevant columns, and harmonises the III schema onto the IV schema via an explicit rename
  map (`ROW_ID`→`note_id`, `SUBJECT_ID`→`subject_id`, `CATEGORY`→`note_type`,
  "Discharge summary"→"DS", dtype coercions, `note_seq`/`source` markers), then concatenates
  the two into a single HuggingFace `Dataset`, optionally length-filters, and adds a
  match-key column.
- **`data_processing/utils.py:1-54`** — `aho_corasick_search` (fast multi-substring search
  of partial texts within full texts via `pyahocorasick`), `process_span_annotations` (map
  `note_id`→span-annotation lists onto note text, slicing `start:end` and serialising to
  JSON per note), and the `del_map` "scrunching" translation table (strip everything
  non-alphanumeric, used to build the lower-cased no-whitespace match key).

## Why it is reusable (Utility)
The III→IV schema-harmonisation rename map is the single most reusable artefact: anyone
merging MIMIC-III and MIMIC-IV notes must reconcile exactly these column-name and dtype
differences, and re-deriving the map is error-prone. The `utils.py` helpers are generic
text-matching infrastructure — Aho-Corasick multi-pattern search, span-to-text slicing, and
the alphanumeric "scrunch" normaliser — useful for any note-linkage or annotation-projection
task.

## What must be parameterised to untangle it
- **Decouple from the package imports** — `mimic.py` imports `BaseDataset`, `del_map`, and
  `NOTE_MATCH_COL` from sibling modules; the merge logic should be a free function returning
  a DataFrame/`Dataset`, with the match-key column name as an argument.
- **Expose the rename map and column selection** as data (a default `MIMIC3_TO_MIMIC4`
  mapping) rather than inline literals, so projects needing a different column subset can
  override.
- **`max_length_chars`** — already optional; keep.
- The Aho-Corasick and span-annotation helpers are already generic; only `process_span_annotations`'
  expectation of `'note_id'`/`'text'` keys should be parameterised.

## Relationship to the wider audit
This is the note-specific facet of the batch-wide MIMIC ingestion overlap — see the central
`evidence/deduplication_mimic_ingestion_standardisation/` case, where this rename map is
nominated as the canonical notes-loader to lift.
