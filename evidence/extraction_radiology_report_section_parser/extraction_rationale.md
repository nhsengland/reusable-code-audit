# Extraction Rationale: radiology_report_section_parser

## What
`txt-ray-align/data/section_parser.py` (whole file, lines 1-260) and its driver
`data/create_section_files.py` (lines 33-135). Adapted from MIT-LCP mimic-code:

- `section_text()` — regex-based splitting of free-text radiology reports into sections keyed
  by their ALL-CAPS headers, with preamble/last-paragraph handling.
- `normalize_section_names()` — a large curated dictionary mapping ~60 header variants and
  misspellings ("impresson", "findins", "comparsion"...) onto canonical section names, plus
  pattern rules for view descriptions ("pa and lateral", "frontal view"...).
- The driver walks a report folder tree, applies per-study override rules, and extracts the
  conclusion section with priority impression > findings > last_paragraph > comparison.

## Why it is reusable
Sectioning free-text radiology (and, with a different header dictionary, discharge/clinic
letter) reports is a prerequisite for almost every NHS NLP project. The core algorithm —
header-regex splitting, fuzzy header normalisation, prioritised conclusion selection — is
generic; the curated misspelling dictionary alone represents significant embedded labour worth
keeping in one shared, versioned place rather than re-copied per project (it is already a
second-generation copy from mimic-code).

## Tangled bespoke logic to parameterise
1. **MIMIC-CXR per-study overrides hardcoded**: `custom_mimic_cxr_rules()` (lines 198-260)
   embeds ~50 literal MIMIC-CXR study IDs (`"s50913680"` etc.) with manual section names and
   character indices. Move to an optional, externally-supplied overrides file (CSV/JSON);
   the parser must accept `custom_section_names: dict` and `custom_indices: dict` as inputs.
2. **Header dictionary and priority order hardcoded**: `frequent_sections` (lines 89-148),
   `p_findings` patterns (lines 150-169) and the conclusion priority tuple
   `("impression", "findings", "last_paragraph", "comparison")`
   (create_section_files.py lines 115, 129) should be loadable/overridable per document type.
3. **MIMIC-CXR folder convention hardcoded** in the driver: group folders matching
   `p` + 2 chars (line 53), patient folders starting `p`, study files `s*.txt` (lines 66, 76),
   output names `mimic_cxr_*.csv` and the 10,000-report batch size `jmp = 10000`
   (lines 150, 165-169). Parameterise the glob patterns, output stem and batch size.
4. The section regex `r"\n ([A-Z ()/,-]+):\s"` (line 17) assumes MIMIC-CXR's
   leading-space layout; expose as an argument with this as default.
