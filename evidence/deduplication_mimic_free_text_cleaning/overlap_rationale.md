# Deduplication Case: MIMIC Free-Text (Clinical Note / Report) Cleaning

**What it does:** Normalises raw MIMIC free text — discharge-note text in
mm-healthfair, CheXpert/MIMIC-CXR radiology reports in txt-ray-align — by
stripping artefacts and collapsing whitespace so the text is fit for embedding or
downstream modelling.

| Repo | File | Shared intent | Bespoke / tangled logic |
|---|---|---|---|
| mm-healthfair | `src/utils/preprocessing.py` (`clean_notes`, lines 746-763) and `src/utils/mimiciv.py` (lines 440-448) | Remove MIMIC de-identification artefacts and squash repeated whitespace | Operates on a Polars `target` column; removes the `___` de-id placeholder; strips runs of `==` separators; then filters notes to an eligible `hadm_id` lookup |
| txt-ray-align | `chexpert/loader/load.py` (`clean`, lines 73-91) | Lower-case, normalise punctuation spacing, collapse multi-whitespace, drop empty sentences | `and/or`→`or` rewrite; `XXX/YYY`→`XXX or YYY` slash expansion; `..`→`.` double-period repair; `punctuation_spacer` translation table; empty-sentence regex — all tuned for CheXpert report grammar |

**Why it is an overlap:** Both share the core intent of *clean noisy clinical
free text → normalised string*, and both converge on the same canonical
sub-step: **collapse all internal whitespace to single spaces** (`str.replace_all(r"\s+", " ")`
vs `" ".join(report.split())`). This is a **partial (tangled) overlap** — the
generic skeleton is shared but each repo layers domain-specific cleaning on top.

**Shared vs bespoke:**
- *Shared (extractable):* a small ordered pipeline of text-normalisation steps —
  whitespace collapse, artefact removal, optional lower-casing — applied to a
  string column. The whitespace-collapse step is genuinely identical in intent.
- *Bespoke (must be parameterised):* the **artefact set** (mm-healthfair's `___`
  de-id placeholder and `==+` separators vs txt-ray-align's `and/or`, slash
  expansion, double-period and empty-sentence rules); whether to **lower-case**
  (txt-ray-align yes, mm-healthfair no); the **execution backend** (Polars
  column expression vs per-string Python `re`); and the surrounding
  **filtering** (mm-healthfair's `hadm_id` eligibility filter is a separate
  cohort concern, not cleaning, and must not migrate into a shared cleaner).

**Consolidation note:** The reusable artefact is an ordered, configurable list of
`(pattern, replacement)` substitutions plus a final whitespace-collapse, exposed
so each repo supplies its own rule set and lower-casing flag. This case is the
free-text counterpart to the structural duplication captured centrally in
`evidence/deduplication_mimic_ingestion_standardisation/`; the two should be
consolidated together so MIMIC ingestion and MIMIC text-cleaning live in one
`mimic-tools` package. Keep cohort filtering out of the shared cleaner.
