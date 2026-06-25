# Deduplication Overlap: JSON load/save helpers (within nlp_renal_biopsy)

## Repos involved
- nlp_renal_biopsy — `src/utils/json.py` (`load_json`, `save_json`)
- nlp_renal_biopsy — `src/ner/src/utils.py` (`load_json`, `save_json`)

## What overlaps (Duplicate within one repo)
The repo contains two independent, near-identical `load_json` / `save_json`
implementations in two different utility modules. Both wrap `json.load` /
`json.dump` over a path. The `src/ner` variant additionally creates parent
directories and validates the path is non-None; the `src/utils` variant adds
`encoding="utf-8"` and an `indent` argument. They are functionally redundant and
are imported by different parts of the same codebase.

## Shared vs bespoke
Entirely shared concern (read/write a JSON file). The only differences are
incidental: directory creation, None-checking, encoding, and indent default.
These should collapse to a single helper with `indent`, `encoding`, and
`make_parents` parameters. This duplication is a clear consolidation target and
also signals that the wider NHS estate re-implements trivial JSON IO repeatedly
(evalsense has its own file helpers; the MedCAT notebooks pickle/json by hand).
