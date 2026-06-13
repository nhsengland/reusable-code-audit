# Deduplication Rationale: mimic_notes_loading

**Repos:** priv-lm-health-extended, priv-lm-health
**Type:** Partial / Tangled (same intent — load MIMIC note CSVs into a working set — two
implementations)

## What overlaps
Both repos turn raw MIMIC note CSV exports into an in-memory working set for a privacy
experiment, written independently in different styles:

- **priv-lm-health-extended** `data_processing/base_datasets/mimic.py:9-71`
  (`MIMIC.load_or_process` / `.process`): `pd.read_csv` the MIMIC-III and MIMIC-IV note
  files (`keep_default_na=False`), filter to rows with a HADM_ID, select the relevant
  columns, rename/harmonise to a common schema, concatenate into a single HuggingFace
  `Dataset`, optionally filter by `max_length_chars`, and cache to disk.
- **priv-lm-health** `privlm/mi_attack.py:26-84` (`get_subject_ids`, `create_member_df`,
  `create_non_member_df`): walk a list of MIMIC note CSV files, `pd.read_csv` each, pull
  `SUBJECT_ID` / `TEXT`, and accumulate into member / non-member DataFrames.

The shared kernel is "read one-or-more MIMIC note CSVs and assemble a `SUBJECT_ID` + `TEXT`
working frame". Both hardcode the MIMIC upper-case column names (`SUBJECT_ID`, `TEXT`,
`HADM_ID`).

## What is shared vs bespoke
**Shared (extractable):** the CSV read + column selection + concatenation into a single
notes table keyed by subject. This is the same MIMIC-notes loader both teams reimplemented.

**Bespoke (stays per call-site) — tangled, state explicitly:**
- *extended:* the III↔IV schema-harmonisation rename map (`ROW_ID`→`note_id`,
  `CATEGORY`→`note_type`, "Discharge summary"→"DS", etc.), the HuggingFace `Dataset`
  caching (`load_or_process` / `save_to_disk`), and the `NOTE_MATCH_COL` scrunching
  (`text.lower().translate(del_map)`) used only for substring matching downstream.
- *priv-lm-health:* the **membership-inference split semantics** — member vs non-member vs
  external partitioning by `SUBJECT_ID` — which is attack logic, not loading, and must stay
  in `mi_attack.py`.

## Deduplication proposal
Lift a shared `load_mimic_notes(paths, columns=("SUBJECT_ID","TEXT"), id_col="SUBJECT_ID")`
loader that reads and concatenates note CSVs into a single frame, with the column set and
ID column as parameters (defaulting to the MIMIC names both repos hardcode). The extended
repo's III↔IV rename map should be an optional `schema_map=` argument; priv-lm-health's
member/non-member partitioning stays in the attack code and consumes the loader's output.

This is the notes-specific slice of the broader, batch-wide MIMIC ingestion overlap — see
`evidence/deduplication_mimic_ingestion_standardisation/`, the central five-repo case, of
which this priv-lm-health ↔ priv-lm-health-extended pair is the deepest pairwise
duplication (same team lineage).
