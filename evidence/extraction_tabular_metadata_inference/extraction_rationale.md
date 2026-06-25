# Extraction: Tabular Metadata Inference and YAML Round-Trip (`MetaData`)

## What it is
`NHSSynth/src/nhssynth/modules/dataloader/metadata.py` (lines 1-355) defines a `MetaData` class (with nested `ColumnMetaData`) that, for an arbitrary pandas DataFrame:
- infers or validates per-column dtype, categorical/boolean status (nunique-based heuristics, lines 86-100), datetime format (via pandas' `_guess_datetime_format_for_array`, lines 58-72) and a decimal rounding scheme recovered from the data itself (lines 74-84);
- resolves a per-column missingness strategy and transformer from declarative config;
- round-trips all of this to/from YAML, including a `_collapse` step (lines 208-247) that de-duplicates identical column specs into YAML anchors;
- emits SDV/SDMetrics-compatible metadata (`get_sdv_metadata`, lines 323-345).

## Why it is reusable
This is a Utility-grade, dataset-agnostic "schema sidecar" for any tabular pipeline: NHS analytics teams constantly need to declare/infer column types, datetime formats and missingness handling, and to keep that as reviewable YAML rather than code. The rounding-scheme inference and the SDV metadata bridge are particularly valuable, repeatedly reinvented pieces. It has no NHSSynth-specific column names or datasets in it — it is already 90% untangled.

## Bespoke logic that must be parameterised/abstracted
1. **Transformer registry is hardwired and resolved via `eval()`** (line 142: `eval(self.transformer_name)(**self.transformer_config)`). This both couples the class to the three NHSSynth transformers imported at lines 16-20 and is a code-injection risk from user-supplied YAML. Replace with an injectable `registry: dict[str, type[ColumnTransformer]]` lookup.
2. **Inference heuristics are magic numbers** — categorical if `nunique() <= 10`, boolean if `<= 2` (lines 95-100); expose thresholds as constructor parameters.
3. **Default transformer policy** (`_infer_transformer`, lines 149-162) embeds modelling decisions (BGM clustering for continuous, `n_components=1` for datetimes); make the policy a pluggable strategy so the metadata layer can be used by non-VAE pipelines.
4. **Constraint coupling**: `ConstraintGraph` (line 174) is imported from a sibling module; extraction should make constraints an optional plug-in rather than a hard dependency.
5. `MISSINGNESS_STRATEGIES` mapping should likewise be injected rather than imported, so downstream users can register custom strategies.
