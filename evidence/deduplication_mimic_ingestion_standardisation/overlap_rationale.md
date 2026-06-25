# Deduplication Case: MIMIC Dataset Ingestion & Standardisation

**What it does:** Loads raw MIMIC exports (MIMIC-III, MIMIC-IV hospital module, or MIMIC-CXR reports), selects the relevant columns/records, harmonises column names and dtypes, and produces an analysis-ready dataset. This is the single most widely duplicated capability in the audited batch: **five repositories** independently implement MIMIC ingestion from scratch.

**Why it is an overlap:** All five implementations share the same intent — "turn a PhysioNet MIMIC download into a clean, filtered DataFrame/Dataset" — but each was written independently, in a different style, and each is a **partial (tangled) overlap** with bespoke project logic baked in:

| Repo | File | Shared utility | Tangled bespoke logic |
|---|---|---|---|
| mm-healthfair | `src/utils/mimiciv.py` (lines 14–110) | Read MIMIC-IV `admissions.csv.gz` with explicit column/dtype lists; standardise fields | Emergency-department cohort selection and a hardcoded "extended stay > 7 days" outcome label (`ext_stay_threshold=7`) |
| priv-lm-health-extended | `data_processing/base_datasets/mimic.py` (lines 1–71) | Read MIMIC-III/IV note CSVs; rename columns; harmonise dtypes across versions (`ROW_ID`→`note_id` etc.) | Merging III+IV into a single HuggingFace `Dataset` and a lower-case/punctuation-stripped `NOTE_MATCH_COL` used only by the memorisation experiments |
| priv-lm-health | `membership_inference/prepare_data_MIA.py` (lines 17–117) | Walk a directory of MIMIC note CSVs, deduplicate patients, sample sentences | Member/non-member/external split sizes (90 patients, 1000 sentences) specific to the membership-inference attack |
| SynthVAE | `utils.py` (lines 151–333) | Generic tabular pre-processing: per-column transformer fitting (datetime→seconds, GMM/standard scaling, one-hot) | Hardcoded MIMIC-III column lists (`ETHNICITY`, `DISCHARGE_LOCATION`, `FIRST_CAREUNIT`, …) burned into the function body |
| txt-ray-align | `data/create_section_files.py` (lines 38–184) | Walk the MIMIC-CXR patient folder hierarchy (`p00`…`p19`) and extract report text | Radiology-specific section extraction (impression/findings/last paragraph fallback) for image–text alignment |

The deepest pairwise duplication is **priv-lm-health vs priv-lm-health-extended** (same team lineage, both prepare MIMIC clinical notes for privacy experiments) and **SynthVAE vs mm-healthfair** (both implement column-type-driven tabular standardisation of MIMIC hospital data).

**Consolidation plan:** Create a shared `mimic-tools` package with three layers:
1. **Loaders** — `read_table(path, table, columns=None, dtypes=None)` for the hospital module, a notes loader that harmonises III/IV schemas (lift directly from priv-lm-health-extended's rename map), and a CXR report walker (lift from txt-ray-align).
2. **Standardisers** — column-type-driven transformation (datetime→numeric, scaling, encoding) lifted from SynthVAE's `mimic_pre_proc`, with the column lists passed as parameters instead of hardcoded.
3. **Cohort builders** — parameterised filters (e.g. `ed_cohort(stay_threshold_days=7)`) so that each project's bespoke cohort/outcome definitions become arguments, not forks.

Every bespoke element noted in the table above must move from a hardcoded value to a function parameter or config entry before the shared package is viable.
