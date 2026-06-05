# NHS Reusable Code Audit (Proof of Concept)

This repository contains a proof-of-concept audit of completed NHS internship projects to identify repeated engineering patterns and reusable code candidates for a future NHS reusable code library.

## Catalog

- [`catalog.md`](./catalog.md) — central human-readable overlap catalog with inline raw snippets
- [`catalog.yml`](./catalog.yml) — machine-readable source of truth for themes, snippets, overlap counts, and reuse metadata

**Headline stats:** 14 snippets extracted across 7 themes from 21 audited projects.

## Repository structure

- [`audit-report.md`](./audit-report.md) — full cross-project audit findings and recommendations
- [`code-snippets/`](./code-snippets/) — theme-based reusable snippet candidates extracted/adapted from audited repositories
  - [`synthetic-data`](./code-snippets/synthetic-data/)
  - [`nlp-text-processing`](./code-snippets/nlp-text-processing/)
  - [`multimodal`](./code-snippets/multimodal/)
  - [`graph-hypergraph`](./code-snippets/graph-hypergraph/)
  - [`evaluation`](./code-snippets/evaluation/)
  - [`explainability`](./code-snippets/explainability/)
  - [`data-pipelines`](./code-snippets/data-pipelines/)

## Audited projects

| ID | Title | Repository |
|---|---|---|
| P82 | EvalSense | https://github.com/nhsengland/evalsense |
| P81 | MM-HealthFair (Wave 8) | https://github.com/nhsengland/mm-healthfair |
| P72 | NER Evaluation with GOSH | https://github.com/nhsengland/nlp_renal_biopsy |
| P71 | Privacy Leakage Extended | https://github.com/nhsengland/priv-lm-health-extended |
| P62 | NHS Monitor Corpus | https://github.com/nhsengland/pvt_p62_corpus_extension |
| P61 | Understanding Fairness and Explainability in Multimodal Approaches | https://github.com/nhsengland/mm-healthfair |
| P52 | Exploring Process Mining | https://github.com/nhsengland/ProcessMining |
| P51 | Investigating Privacy Concerns for LMs | https://github.com/nhsengland/priv-lm-health |
| P43 | Enriching Neurology Patient Information using MedCAT | https://github.com/nhsengland/P43_LTHMedCat |
| P41 | NHS Synth | https://github.com/nhsengland/NHSSynth |
| P34 | Using Hypergraphs to Investigate Comorbidities | https://github.com/nhsx/hypergraph-mm |
| P33 | Exploring Large-scale Language Models with NHS Incident Data | https://github.com/nhsx/ELM4PSIR |
| P32 | Predicting the Impact of Health Inequalities - Diabetes | https://github.com/nhsx/ESNEFT_diabetes_StephenRicher |
| P31 | Txt-Ray Align Continued | https://github.com/nhsx/txt-ray-align |
| P24 | Using LIME to explain facial disease classification | https://github.com/nhsx/LIME-XAI-Facial-Disease-Classification |
| P23 | STM for survey data | https://github.com/nhsx/stm-survey-text |
| P22 | Txt-Ray Align | https://github.com/nhsx/txt-ray-align |
| P21 | SynthVAE Continued | https://github.com/nhsx/SynthVAE |
| P14 | Model Class Reliance | https://github.com/nhsx/commercial-data-healthcare-predictions |
| P12 | SynthVAE | https://github.com/nhsx/SynthVAE |
| P11 | SynPathDiabetes | https://github.com/nhsx/SynPath_Diabetes |

## Notes

- This repository is an investigation artifact, not a production library.
- P61/P81, P21/P12, and P31/P22 are treated as distinct project entries within shared codebases.
- P62 repository link was included in scope but was not resolvable at audit time.
