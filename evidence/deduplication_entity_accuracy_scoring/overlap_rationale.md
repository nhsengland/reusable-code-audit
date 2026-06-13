# Deduplication Overlap: Per-entity accuracy scoring (within nlp_renal_biopsy)

## Repos involved
- nlp_renal_biopsy — `src/modelling/qa_base.py` `QABase.calculate_entity_accuracy`
- nlp_renal_biopsy — `src/evaluate/entity.py` `calculate_entity_accuracy`

## What overlaps (Duplicate within one repo)
Two functions compute the same thing: for each entity in an
`entity_to_info_map`, accumulate correct/total over a list of per-report score
dicts, compute an accuracy percentage, and print a fixed-width table with
`Entity / Score / Type` columns. The `qa_base` version reads the map from
`self.entity_guidelines`; the `entity.py` version takes it as an argument and
additionally collects up to three incorrect-prediction examples per entity.

## Shared vs bespoke
Shared: the accumulate-correct-over-total → percentage → tabular print logic,
including the `"=" * N` / `"-" * N` header formatting and column widths.
Bespoke / incidental: where the entity map comes from, and the error-example
collection. These should be one parameterised metric helper:
`per_label_accuracy(scores, labels, collect_errors=False)` returning a dict and
optionally printing. The hardcoded console-table formatting (widths 30/15/15,
80-char rules) is itself a small reusable reporting utility duplicated here.
