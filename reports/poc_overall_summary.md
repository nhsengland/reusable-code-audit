# Cross-Repository Re-usability & Deduplication Audit — PoC Summary

**Date:** 2026-06-13
**Scope:** NHS England / NHSX data-science intern projects (Waves 1–8)
**Method:** Each repository was cloned and read against the **SUL (Structural,
Utility, Logic)** doctrine, with particular attention to *tangled code* —
reusable utilities with bespoke project logic hardcoded inside them. Findings
are recorded as per-repo reports (`reports/`) and as evidence folders
(`evidence/`) containing the exact raw source for every candidate.

---

## 1. Repositories audited

Seventeen repositories were successfully cloned and audited. Several catalogue
entries collapse onto a single repository (the same codebase appears in more
than one wave), and three entries had no auditable code.

| # | Repo | Wave(s) | Language | SUL adherence |
|---|------|---------|----------|---------------|
| 1 | evalsense | 8 | Python | **High** |
| 2 | NHSSynth | 4 | Python | **High** |
| 3 | hypergraph-mm | 3, 4 | Python (Numba) | **High** |
| 4 | mm-healthfair | 6, 8 | Python | Medium |
| 5 | nlp_renal_biopsy | 7 | Python | Medium |
| 6 | priv-lm-health-extended | 7 | Python | Medium |
| 7 | txt-ray-align | 2, 3 | Python | Medium |
| 8 | stm-survey-text | 2 | R | Medium |
| 9 | SynPath_Diabetes | 1 | Python | Medium |
| 10 | ESNEFT_diabetes_StephenRicher | 3 | Python | Medium |
| 11 | SynthVAE | 1, 2 | Python | Low |
| 12 | priv-lm-health | 5 | Python | Low |
| 13 | ELM4PSIR | 3 | Python | Low |
| 14 | P43_LTHMedCat | 4 | Python (notebooks) | Low |
| 15 | ProcessMining | 5 | Python (notebooks) | Low |
| 16 | LIME-XAI-Facial-Disease-Classification | 2 | Python (notebooks) | Low |
| 17 | commercial-data-healthcare-predictions | 1 | Python | Low |

**Not audited (no auditable code in this PoC):**
- `pvt_p62_corpus_extension` (P62) — repository is private; clone failed.
- P73 *VQA with GOSH* and P53 *SAIL graph embeddings* — code "Available on Request".
- P13 *NHS Text Data Exploration* — catalogue `codelink` is a placeholder (`holding.html`).

**Lineage note:** Several repositories are evolutions of earlier ones and share
DNA by design — `NHSSynth` ⟵ `SynthVAE`; `priv-lm-health-extended` ⟵
`priv-lm-health`; `hypergraph-mm` spans two waves. These pairs are the richest
seams of duplication and are called out individually below.

---

## 2. Headline findings

- **General engineering quality is bimodal.** Three repositories
  (`evalsense`, `NHSSynth`, `hypergraph-mm`) are properly packaged, with clean
  Structural/Utility/Logic separation, type hints and tests — they are the
  *reference standard* for the cohort and the source of the cleanest extraction
  candidates. The majority, however, are research scripts/notebooks where a
  genuinely reusable utility is tangled with one project's dataset, column names
  and file paths.
- **The same five or six utilities are re-implemented again and again** across
  unrelated teams and years: setting random seeds, loading an experiment config,
  ingesting MIMIC, cleaning clinical free-text, HuggingFace training/generation
  boilerplate, and linking NHS geographies (postcode → LSOA → IMD). These are
  the highest-leverage consolidation targets because the duplication spans the
  whole batch, not just sibling repos.
- **Hardcoding is the single biggest blocker to reuse.** Local absolute paths,
  dataset-specific column lists, trust/CCG/LSOA codes and magic date ranges are
  pervasive. In almost every extraction candidate the *utility is already
  reusable* — it is only the hardcoded value that needs to become a parameter.

---

## 3. Major themes of duplication

The 24 deduplication cases cluster into seven themes. Folder names below are
under `evidence/`.

### Theme A — Project boilerplate (spans the whole batch)
- `deduplication_random_seed_setting` — `set_seed` re-implemented in SynthVAE and
  NHSSynth (and inline in ELM4PSIR, mm-healthfair, txt-ray-align). One shared,
  complete version (seed numpy + torch + random + CUDA) would replace all of them.
- `deduplication_experiment_config_loading` — four divergent config loaders
  (NHSSynth, evalsense, nlp_renal_biopsy in YAML+Pydantic; mm-healthfair in TOML,
  copy-pasted across six scripts). Converge on YAML + Pydantic + CLI override.

### Theme B — MIMIC dataset handling (the flagship cross-batch overlap)
- `deduplication_mimic_ingestion_standardisation` — **five repos**
  (SynthVAE, mm-healthfair, priv-lm-health, priv-lm-health-extended, txt-ray-align)
  each independently load and standardise a MIMIC export. This is the single most
  duplicated capability in the PoC.
- `deduplication_mimic_notes_loading` (priv-lm-health ↔ priv-lm-health-extended)
  and `deduplication_mimic_free_text_cleaning` (mm-healthfair ↔ txt-ray-align) are
  finer-grained facets of the same theme.

### Theme C — Clinical / survey free-text NLP
- `deduplication_clinical_free_text_cleaning` — the lower-case → normalise →
  tokenise → stopword recipe re-implemented in **four** repos across two languages
  (stm-survey-text in R; nlp_renal_biopsy, P43_LTHMedCat, ELM4PSIR in Python).
- `deduplication_clinical_text_embedding` (mm-healthfair ↔ txt-ray-align) and
  `deduplication_clinical_note_cleaning` (ELM4PSIR-internal copy-paste).

### Theme D — Transformer / LLM scaffolding
- `deduplication_hf_trainer_boilerplate` (ELM4PSIR ↔ priv-lm-health),
  `deduplication_hf_generation_pipeline` (priv-lm-health-extended internal), and
  `deduplication_llm_judge_comparison` (evalsense ↔ nlp_renal_biopsy LLM-as-judge).

### Theme E — Synthetic / tabular data (SynthVAE ↔ NHSSynth lineage)
- `deduplication_tabular_vae_architecture`, `deduplication_gmm_onehot_preprocessing`,
  `deduplication_sdv_quality_metrics`, `deduplication_opacus_dp_training`,
  `deduplication_correlation_plotting` — NHSSynth is essentially the matured,
  packaged successor to SynthVAE, so most of SynthVAE is superseded rather than
  merely duplicated.

### Theme F — Privacy attacks
- `deduplication_reference_model_mia_scoring` (priv-lm-health ↔
  priv-lm-health-extended) — membership-inference / reference-model scoring.

### Theme G — Population health, pathways & NHS geography
- `deduplication_postcode_lsoa_imd_linkage` — postcode→LSOA→IMD deprivation
  linkage in ESNEFT, ProcessMining and commercial-data-healthcare-predictions.
- `deduplication_diabetes_measure_vocabulary` (ESNEFT ↔ SynPath_Diabetes) and
  `deduplication_synthetic_patient_event_timelines` (ProcessMining ↔ SynPath_Diabetes).

---

## 4. Highest-value extraction candidates

Ranked by reuse leverage × cleanliness of the underlying utility. Full rationale
and raw source are in the named `evidence/` folders.

| Rank | Candidate (`evidence/…`) | Source repo | Why it's high value | Key thing to parameterise |
|------|--------------------------|-------------|---------------------|---------------------------|
| 1 | `extraction_resumable_file_download` | evalsense | Robust, hash-verified, resumable downloader — every repo needs dataset/model fetching | Output dir & auth via args (already mostly clean) |
| 2 | `extraction_postcode_lsoa_imd_enrichment` + `extraction_lsoa_census_indicator_loaders` | ProcessMining, ESNEFT | NHS-geography linkage is reusable by *any* population-health team | Reference lookup paths & target IMD year |
| 3 | `extraction_tabular_metadata_inference` | NHSSynth | Generic dtype/metadata inference for arbitrary tabular data | Already generic; lift out of NHSSynth package boundary |
| 4 | `extraction_robust_json_parsing` | nlp_renal_biopsy | Recovers valid JSON from messy LLM output — universal LLM-app need | Nothing bespoke; pure utility |
| 5 | `extraction_dp_model_training_scaffold` | NHSSynth | Differential-privacy training scaffold (Opacus) reusable beyond synthesis | Model/optimiser & ε budget as args |
| 6 | `extraction_bootstrapped_fairness_metrics` / `extraction_fairness_metrics_binary_classification` | mm-healthfair | Bootstrapped subgroup fairness metrics — reusable across any classifier | Sensitive-attribute column & group definitions |
| 7 | `extraction_multi_provider_llm_generator` | priv-lm-health-extended | One interface over Anthropic / OpenAI / HuggingFace backends | Provider choice, model name & API keys via config (sibling `attacker_LM/run.py` also hardcodes `HF_HOME = /import/hf-cache/`) |
| 8 | `extraction_hypergraph_centrality_solvers` + `extraction_numba_binary_powerset_encoding` | hypergraph-mm | Numba-accelerated set/centrality maths, domain-agnostic | Disease/code vocabulary passed in, not assumed |
| 9 | `extraction_prompt_template_validator` + `extraction_llm_answer_extraction` | evalsense, nlp_renal_biopsy | Prompt-template-with-required-placeholder validation and answer/score parsing | Placeholder set & score regex as args |
| 10 | `extraction_icd9_to_icd10_ltc_mapping` | mm-healthfair | Reusable ICD-9→ICD-10 long-term-condition crosswalk | Mapping table path & target LTC list |

A further 30 extraction candidates (radiology report section parsing, LIME
superpixel explainer, Keras transfer-learning fine-tune, FHIR patient
serialisation, event-log construction, grouped MCR/Rashomon, constrained
rejection sampling, etc.) are documented in `evidence/extraction_*`.

---

## 5. Recommended consolidation roadmap

1. **Stand up a shared `nhs-analytics-common` package first.** Move the Theme-A
   boilerplate (seed setting, config loading) and the Theme-G geography linkage
   into it. These are low-risk, no bespoke logic, and benefit every team
   immediately.
2. **Build a `mimic-tools` package** (Theme B): loaders, schema-harmonisers and
   parameterised cohort builders. Lift the cleanest pieces from each of the five
   implementations; replace every hardcoded column list / cohort filter with a
   parameter. This retires the largest single block of duplicated effort.
3. **Publish a `clinical-text` module** (Theme C): a documented, language-agnostic
   normalise→tokenise→stopword spec with a Python reference implementation, plus a
   parameterised report-section segmenter.
4. **Retire SynthVAE in favour of NHSSynth** (Theme E): treat NHSSynth as the
   canonical synthetic-tabular library and archive SynthVAE, porting any unique
   SynthVAE investigations onto the NHSSynth API.
5. **Extract the standalone utilities** in §4 as small, independently-versioned
   helpers as capacity allows.

**The recurring action in every case is the same:** turn a hardcoded value
(a path, a column list, a trust/CCG/LSOA code, a date range) into a parameter.
The utilities are already there — they are simply trapped inside one project's
bespoke logic.

---

*Generated by an automated cross-repository audit. Each claim above is backed by
raw source in the corresponding `evidence/` folder; see the per-repo files in
`reports/` for repository-level detail.*
