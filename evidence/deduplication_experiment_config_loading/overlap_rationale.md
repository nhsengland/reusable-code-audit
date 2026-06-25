# Deduplication Case: Experiment Configuration Loading

**What it does:** Loads a declarative configuration file (YAML or TOML) describing an experiment or pipeline run — paths, model hyperparameters, dataset definitions — optionally validates it against a schema, and merges it with command-line arguments.

**Why it is an overlap:** This is a **semantic overlap** across at least four repositories. Each project solved "configure my pipeline without hardcoding values" independently, with a different file format and a different validation strategy, so none of the implementations can be shared even though their intent is identical:

| Repo | File | Approach |
|---|---|---|
| NHSSynth | `src/nhssynth/cli/config.py` (lines 42–135) | YAML loaded with `yaml.safe_load`, manually merged over argparse defaults, with custom module-hierarchy validation and a `write_config` round-trip for experiment reproducibility |
| nlp_renal_biopsy | `src/ner/src/config/global_config.py` (lines 1–37) | YAML loaded with `yaml.safe_load`, validated through Pydantic `BaseModel` schemas |
| evalsense | `evalsense/datasets/dataset_config.py` (lines 250–301) | YAML loaded with `yaml.safe_load`, validated through Pydantic models with deep-merge of multiple config files |
| mm-healthfair | `src/train.py` (lines 20–99) and five sibling scripts | TOML loaded with `toml.load`, merged with argparse by hand; the same load-and-merge block is copy-pasted into `train.py`, `evaluate.py`, `explain.py`, `fairness.py`, `explore_data.py` and `prepare_data.py` |

mm-healthfair additionally duplicates the pattern *within* itself: six scripts each repeat the argparse + `toml.load` boilerplate.

**Shared utility vs bespoke differences:** The shared utility is "load config file → validate → merge with CLI args → hand back a typed object". The bespoke parts are only the schema contents (which keys each project expects) and the file format choice. Neither justifies four divergent implementations.

**Consolidation plan:** Adopt a single pattern — YAML + Pydantic schema + CLI override (the nlp_renal_biopsy/evalsense approach is the cleanest) — in a shared package, e.g. `nhs_analytics_common.config.load_config(path, schema: type[BaseModel], cli_overrides=None)`. Each project then contributes only its Pydantic schema. NHSSynth's `write_config` (dumping the resolved config next to experiment outputs for reproducibility) is the one genuinely valuable extra and should be folded into the shared utility rather than lost.
