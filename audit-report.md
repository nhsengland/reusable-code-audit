# Reusable Code Audit Report

## 1. Executive Summary

This audit reviewed public NHS internship project repositories to identify repeated technical patterns and candidate components for a shared reusable code library.

Key findings:

- **Python-first ecosystem**: most projects use Python with common scientific/ML stacks (pandas, numpy, scikit-learn, PyTorch).
- **Recurring workflow layers**: many projects independently implement data ingestion/cleaning, training/evaluation loops, and reporting utilities.
- **Strong reuse opportunity in utility code**: repeated patterns were found for file/path handling, text cleaning, split generation, fairness/evaluation wrappers, and experiment outputs.
- **Cross-cutting themes**: synthetic data generation, NLP preprocessing, multimodal pipelines, fairness/evaluation, and explainability all have reusable building blocks.

A practical next step is to stand up a small internal package with shared modules for `data_pipelines`, `evaluation`, `fairness`, and `text_preprocessing`, then migrate 2–3 pilot projects onto it.

## 2. Methodology

1. Reviewed each public repository listed in scope (excluding private “Available on Request” items).
2. Inspected repository structure and dependency declarations (for example `requirements.txt`, `pyproject.toml`, and README build notes).
3. Identified recurring functional areas and helper utilities.
4. Extracted/adapted representative source snippets into themed folders under `code-snippets/`.
5. Mapped projects to shared themes and produced recommendations for a reusable library roadmap.

## 3. Project Inventory

| ID | Repo | Primary language(s) | Key libraries (observed) | Main functional area |
|---|---|---|---|---|
| P82 | nhsengland/evalsense | Python | inspect-ai, evaluate, rouge/bleu tooling | LLM evaluation framework |
| P81 | nhsengland/mm-healthfair | Python | torch, fairlearn, shap, polars | Multimodal fairness modelling |
| P72 | nhsengland/nlp_renal_biopsy | Python | pandas, custom preprocessing modules | Clinical NLP preprocessing/evaluation |
| P71 | nhsengland/priv-lm-health-extended | Python | rouge-score, transformer-related tooling | Privacy risk and LM evaluation |
| P62 | nhsengland/pvt_p62_corpus_extension | N/A | N/A (repo unresolved) | NHS monitor corpus extension |
| P61 | nhsengland/mm-healthfair | Python | torch, fairlearn, shap, polars | Fairness/explainability in multimodal models |
| P52 | nhsengland/ProcessMining | Python (notebook-heavy) | process-mining notebook stack | Process mining and pathway analysis |
| P51 | nhsengland/priv-lm-health | Python | pandas, sklearn, transformers ecosystem | LM privacy and memorisation analysis |
| P43 | nhsengland/P43_LTHMedCat | Python | medcat/NLP stack (project-specific) | Neurology text enrichment |
| P41 | nhsengland/NHSSynth | Python | pyproject/poetry stack, synthetic data modules | Synthetic data framework |
| P34 | nhsx/hypergraph-mm | Python | numpy, scipy, numba | Hypergraph analytics |
| P33 | nhsx/ELM4PSIR | Python | pandas, sklearn, loguru | Clinical text modelling pipelines |
| P32 | nhsx/ESNEFT_diabetes_StephenRicher | Python | pandas, seaborn, networkx | Health inequalities analytics |
| P31 | nhsx/txt-ray-align | Python | torch, clip, sklearn, nltk | Text-image alignment and retrieval |
| P24 | nhsx/LIME-XAI-Facial-Disease-Classification | Python (notebook-heavy) | tensorflow, keras, scikit-image, sklearn | LIME explainability for imaging |
| P23 | nhsx/stm-survey-text | R | quanteda, stm, tidytext-style tooling | Survey NLP topic modelling |
| P22 | nhsx/txt-ray-align | Python | torch, clip, sklearn, nltk | Text-image alignment and retrieval |
| P21 | nhsx/SynthVAE | Python | torch, opacus, sdv/sdmetrics | Differentially private synthetic data |
| P14 | nhsx/commercial-data-healthcare-predictions | Python | sklearn, mcrforest | Model class reliance explainability |
| P12 | nhsx/SynthVAE | Python | torch, opacus, sdv/sdmetrics | Differentially private synthetic data |
| P11 | nhsx/SynPath_Diabetes | Python (notebook-heavy) | synthetic patient generation stack | Synthetic pathway generation |

## 4. Findings by Theme

### 4.1 Synthetic Data

**Projects:** P12, P21, P41, P11  
**Repeated patterns:** VAE training/reconstruction workflows, tabular metric scoring, helper utilities for output handling and experiment directories.  
**Reusable abstractions:**
- Standard synthetic data evaluation API (`distributional_metrics`, `privacy_metrics`)
- Shared experiment I/O/path utilities
- Optional differential privacy training hooks (Opacus wrappers)

### 4.2 NLP / Text Processing

**Projects:** P72, P71, P51, P33, P23, P43  
**Repeated patterns:** text cleaning, token/stopword pipelines, train/holdout text split creation, note normalization and admin-language stripping.  
**Reusable abstractions:**
- configurable text cleaning/preprocessing pipeline
- dataset split helpers for LM and downstream tasks
- common lexical metrics wrappers (ROUGE/BLEU)

### 4.3 Multimodal

**Projects:** P22, P31, P61, P81, P82 (evaluation layer linkage)  
**Repeated patterns:** multimodal dataset wrappers, embedding generation, retrieval-style evaluation, modality-specific feature mapping.  
**Reusable abstractions:**
- base multimodal dataset classes (text/image/timeseries)
- embedding generation and persistence utility
- shared retrieval metrics module

### 4.4 Graphs / Hypergraphs

**Projects:** P34 (+ graph analytics elements in P32)  
**Repeated patterns:** centrality and overlap coefficient computation over structured disease networks; heavy numerical kernels.  
**Reusable abstractions:**
- numba-accelerated graph/hypergraph metric kernels
- standard wrappers for node/edge centrality outputs

### 4.5 Evaluation

**Projects:** P82, P31/P22, P12/P21, P61/P81  
**Repeated patterns:** metric computation wrappers, standardized score objects/dataframes, evaluation report generation.  
**Reusable abstractions:**
- evaluator protocol/factory pattern
- unified metric interface for text, tabular synthetic data, and retrieval tasks

### 4.6 Explainability

**Projects:** P24, P14, P61/P81  
**Repeated patterns:** fairness CI estimation, SHAP/LIME-driven feature attribution, grouped feature importance reporting.  
**Reusable abstractions:**
- confidence-interval utilities for fairness metrics
- generic explainability report builders (SHAP/LIME/MCR outputs)

### 4.7 Data Pipelines

**Projects:** P33, P72, P52, P32, P51/P71  
**Repeated patterns:** train/holdout split generation, ingestion + schema normalization, path and file management helpers.  
**Reusable abstractions:**
- robust split + persistence helper module
- standardized input JSON/build manifests for downstream pipelines

## 5. Reuse Opportunity Matrix

| Project ID | Synthetic data | NLP/Text | Multimodal | Graph/Hypergraph | Evaluation | Explainability | Data pipelines |
|---|---|---|---|---|---|---|---|
| P82 |  | ✓ |  |  | ✓ |  | ✓ |
| P81 |  |  | ✓ |  | ✓ | ✓ | ✓ |
| P72 |  | ✓ |  |  | ✓ |  | ✓ |
| P71 |  | ✓ |  |  | ✓ |  | ✓ |
| P62 |  |  |  |  |  |  |  |
| P61 |  |  | ✓ |  | ✓ | ✓ | ✓ |
| P52 |  |  |  |  | ✓ |  | ✓ |
| P51 |  | ✓ |  |  | ✓ |  | ✓ |
| P43 |  | ✓ |  |  | ✓ |  | ✓ |
| P41 | ✓ |  |  |  | ✓ |  | ✓ |
| P34 |  |  |  | ✓ | ✓ |  | ✓ |
| P33 |  | ✓ |  |  | ✓ |  | ✓ |
| P32 |  |  |  | ✓ | ✓ | ✓ | ✓ |
| P31 |  | ✓ | ✓ |  | ✓ |  | ✓ |
| P24 |  |  |  |  | ✓ | ✓ | ✓ |
| P23 |  | ✓ |  |  | ✓ |  | ✓ |
| P22 |  | ✓ | ✓ |  | ✓ |  | ✓ |
| P21 | ✓ |  |  |  | ✓ |  | ✓ |
| P14 |  |  |  |  | ✓ | ✓ | ✓ |
| P12 | ✓ |  |  |  | ✓ |  | ✓ |
| P11 | ✓ |  |  |  | ✓ |  | ✓ |

## 6. Recommendations

1. **Start with a small shared core package** covering:
   - `pipelines/splits.py`
   - `text/cleaning.py`
   - `evaluation/interfaces.py`
   - `fairness/confidence_intervals.py`

2. **Pilot adoption in 2–3 active projects** (suggested: EvalSense, MM-HealthFair, and one NLP project) to validate API design.

3. **Create template conventions** for new internship repos:
   - standard folder layout
   - shared CLI entrypoints
   - mandatory metric/evaluation adapters

4. **Add lightweight governance**:
   - semantic versioning for shared package
   - contribution guide with clinical-safe defaults
   - minimal integration test suite against representative datasets

5. **Resolve/confirm unavailable scope repo (P62)** before final library planning so corpus-oriented reuse opportunities are not missed.
