# Deduplication Rationale: clinical_note_cleaning (ELM4PSIR internal)

**Repos:** ELM4PSIR (internal duplication — two modules within the same repository)
**Type:** Near-identical copy/paste

## What overlaps
This is an **internal** duplication inside a single repository: the same `clean_data`
free-text cleaning routine has been copied into two sibling utility modules.

- **`utils/prepare_classification_datasets.py:72-134`** (`LMTextData.clean_data`)
- **`utils/prepare_notes_for_lm.py:70-138`** (sibling class `.clean_data`)

The two bodies are line-for-line the same recipe operating on a notes DataFrame:

1. Optional bracketed-content strip `r"\[.*?\]"` (de-identification placeholders) when
   `remove_punctuation` is set.
2. Iterate a `self.replacement_map` of `(original, replacement)` pairs applying
   `str.replace`, dropping NA rows each pass and bailing out early on an empty frame.
3. Optionally strip an `admin_language` token list (replacing each with a space).
4. `str.strip()`, `str.lower()`, then a second whitespace collapse
   `re.sub(r"\\s+", " ", x)` per row, and finally `dropna()`.

The only differences are cosmetic: the `prepare_notes_for_lm` copy adds an unused
`min_tokens=5` parameter and defaults `remove_punctuation=False` (vs `True`), and the
docstrings differ ("classification datasets" vs "CRIS produced clinical notes"). The
algorithm is otherwise identical.

## What is shared vs bespoke
**Shared (the whole function):** the entire cleaning pipeline is common. There is no
divergent logic between the two copies — this is straightforward copy/paste drift waiting
to happen (the two will inevitably fall out of sync as one is edited and the other is not).

**Bespoke (stays per call-site):** only the configuration injected via the surrounding
class — the `text_col` name, the `replacement_map` contents, and the `admin_language` token
list. None of this is bespoke *logic*; it is bespoke *data*.

## Deduplication proposal
Collapse the two into one shared `clean_notes_df(df, text_col, replacement_map,
admin_language=None, remove_punctuation=False, strip_bracketed=True)` helper in a single
`utils` module, and have both `LMTextData` and the LM-prep class call it. Parameterise:
the text column name, the replacement map, the admin-token list, and the
`remove_punctuation` / bracket-strip flags (currently the only behavioural difference
between the two copies). Note the `r"\\s+"` regex is double-escaped and matches a literal
`\s+` rather than whitespace — fix this once, in the shared version, rather than twice.
