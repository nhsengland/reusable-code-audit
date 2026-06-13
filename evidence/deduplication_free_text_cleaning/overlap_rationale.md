# Deduplication Case: Clinical/Survey Free-Text Cleaning

**What it does:** Normalises raw NHS free-text (patient-safety incident reports, survey responses, histopathology reports) before NLP modelling: lower-casing, stripping markup/punctuation/digits, normalising whitespace and newlines, and tokenising.

**Why it is an overlap:** This is a **cross-language semantic overlap**. Three repositories implement the same intent — "turn messy NHS free-text into clean model-ready text" — in two different languages:

| Repo | File | Language | Implementation |
|---|---|---|---|
| ELM4PSIR | `classification_tasks/.../word_vector_nn/datasets/preprocess/utils.py` (lines 1–26) | Python | `get_clean_text`: lower-case, replace `<br />`/`\n`/`&#xd;` markup artefacts |
| stm-survey-text | `R/main/functions.R` (lines 38–76) | R | `clean_text`: lower-case, expand contractions, strip punctuation/digits/single characters, tokenise, remove stopwords, build document-frequency matrix |
| nlp_renal_biopsy | `src/renal_biopsy/preprocessor.py` (lines 77–143) | Python | `segment_report` + helpers: lower-case matching, whitespace/colon normalisation — **tangled** with renal-biopsy section segmentation |

Per the audit doctrine, the R-vs-Python difference does not matter: the intent and outcome (cleaned, tokenisable text from NHS free-text sources) are the same, so this is a deduplication candidate.

**Shared utility vs bespoke differences (Partial Overlap):**
- *Shared core:* lower-casing, markup/punctuation/digit stripping, whitespace normalisation, tokenisation with a configurable stop-word list.
- *Bespoke (must stay out of the shared utility or be parameterised):* ELM4PSIR's markup replacements are specific to the LFPSE/incident-data export format (`&#xd;` carriage returns) — these should be a configurable replacement map. stm-survey-text's lemmatisation/n-gram/document-frequency-matrix steps are STM-specific post-processing and belong downstream. nlp_renal_biopsy's section-header dictionary (`microscopy`, `conclusion`, specimen relevance words) is renal-pathology business logic and must be passed in as a parameter, not hardcoded.

**Consolidation plan:** A shared text-preprocessing module (Python, with thin R bindings or a documented R equivalent) exposing `clean_text(text, replacement_map=None, strip_digits=True, stopwords=None)` plus a separate, parameterised `segment_by_headers(text, header_map)` for report sectioning. Each project then supplies only its replacement map / header dictionary.
