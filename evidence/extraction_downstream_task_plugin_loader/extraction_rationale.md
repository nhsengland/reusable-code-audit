# Extraction: Downstream-Task Plugin Loader (`Task` + `get_tasks`)

## What it is
`NHSSynth/src/nhssynth/modules/evaluation/tasks.py` (lines 1-101): a minimal plugin system for "train-on-synthetic, test-on-real"-style utility evaluation. A `Task` wraps a user callable plus declarative flags (`supports_fairness`, `target` column, description); `get_tasks(fn_dataset, tasks_root)` discovers every `.py` file under `tasks/<dataset_name>/`, imports it dynamically with `importlib`, and collects the module-level `task` object. Example plugins live in `tasks/support/logreg.py`, `tasks/support/randomforest.py` and `tasks/hypertension_synthetic/logreg.py`.

## Why it is reusable
Letting analysts drop a single Python file into a conventions-based directory to register an arbitrary downstream evaluation — without touching framework code — is a Structural pattern useful to any evaluation harness (synthetic-data utility, model benchmarking, RAP pipelines). It cleanly separates Logic (the per-dataset task files) from Structure (discovery/execution), which is exactly the SUL separation this audit promotes. The fairness integration point (a task declares its `target` and whether it yields binary predictions) is a tidy contract reused by `EvalFrame._task_step`.

## Bespoke logic that must be parameterised/abstracted
1. **CWD-relative import** (line 96): `spec_from_file_location("nhssynth_task_" + ..., os.getcwd() + "/" + str(task_path))` breaks when the CLI is run from another directory; resolve `task_path` absolutely instead.
2. **Directory convention is hard-asserted** (lines 86-89): the `tasks_dir/<dataset>` layout and the "module must expose a variable named `task`" convention (line 100) should be documented parameters (attribute name configurable, graceful skip with warning rather than `AttributeError`).
3. **No sandboxing/validation**: arbitrary code execution from the tasks directory is inherent to the design, but the extracted utility should validate that the loaded object is a `Task` and surface import errors per-file rather than aborting discovery.
4. The deprecated `supports_aequitas` alias (lines 27-33, 53-55) is NHSSynth-history baggage; drop on extraction.
