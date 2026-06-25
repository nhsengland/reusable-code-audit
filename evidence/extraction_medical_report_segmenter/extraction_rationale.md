# Extraction Candidate: Header-based clinical report segmenter (tangled)

## What it is
`segment_report` and helpers from
`nlp_renal_biopsy/src/renal_biopsy/preprocessor.py`. It splits a free-text
pathology report into sections by detecting upper-case headers via regex, then
fuzzy-matches each detected header to a canonical header list using Levenshtein
distance (tolerating OCR/typo variation up to distance 2), and re-associates
content under the nearest valid header.

## Why it is reusable (Structural/Utility, tangled)
Header-driven, fuzzy-matched segmentation of semi-structured clinical documents
(discharge summaries, histopathology, radiology reports) is a generic need in
NHS text projects. The fuzzy-match-to-canonical-header mechanism is the reusable
core and is genuinely useful — it tolerates inconsistent real-world headers.

## What must be parameterised to untangle it (this is classic tangled code)
The reusable segmenter is welded to renal-biopsy specifics:
- The canonical header list `["TYPED","CLINICAL","SPECIMEN","MACROSCOPY",
  "MICROSCOPY","CONCLUSION"]` is hardcoded in `RenalBiopsyProcessor.__init__`.
- `text.replace("ELECTRON MICROSCOPY", "[electron microscopy]")` is a
  domain-specific pre-edit hardcoded in `segment_report`.
- `_is_relevant_renal_specimen` hardcodes `['kidney','renal','nephrectomy']`.
- `_process_conclusion_section` hardcodes the regexes `reported by`,
  `report authorised by`, `supplementary report` and the extra header keys.
- The Levenshtein threshold `<= 2` is a magic number.
To untangle: inject the canonical header list, the fuzzy-distance threshold, the
pre-substitution map, the specimen-filter keyword list, and the
conclusion-splitting regex set as constructor parameters; keep only the
generic detect-headers / fuzzy-assign loop in the base class.
