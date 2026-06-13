# Extraction Candidate: Survey free-text cleaning pipeline (R, tangled)

## What it is
`clean_text` (plus `convert_to_stm`, `lemmatiser`, `text_length`) from
`stm-survey-text/R/main/functions.R`. A quanteda-based text-cleaning pipeline:
builds a corpus from a dataframe column, lowercases, expands contractions,
strips punctuation/digits/single-character tokens, lemmatises or stems,
optionally builds n-grams, removes stopwords, and returns tokens plus a trimmed
document-feature matrix.

## Why it is reusable (Utility, tangled)
Free-text cleaning for topic modelling / NLP is a generic step. This is the R
counterpart of the spaCy/regex cleaning done in nlp_renal_biopsy and the MedCAT
notebooks — a cross-language semantic overlap. The pipeline (lowercase → expand
contractions → strip non-alnum/digits/short tokens → lemmatise → tokenise →
remove stopwords → trim by frequency) is a reusable recipe.

## What must be parameterised to untangle it
The function is welded to this survey dataset:
- The text column is hardcoded as `data$Response` (line 46) and doc id as
  `data$row_index` (line 47) — should be column-name arguments.
- `min_termfreq` default `2` is a magic threshold (already an argument).
- Stopwords are passed in (good) but the calling `preprocess.R` builds
  `mystopwords` from a dataset-specific `highFreq` list.
To untangle: pass the text column and id column names as parameters and remove
the `data$Response`/`data$row_index` literals so the pipeline works on any
dataframe column.
