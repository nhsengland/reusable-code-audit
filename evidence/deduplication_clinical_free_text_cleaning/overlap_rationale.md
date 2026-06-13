# Deduplication Overlap: Clinical / survey free-text cleaning pipelines

## Repos involved
- stm-survey-text (R) — `R/main/functions.R` `clean_text`
- nlp_renal_biopsy (Python) — `src/preprocessing/eda.py` tokenisation
- P43_LTHMedCat (Python) — `notebooks/common.py` MedCAT/negspacy pipeline setup

## What overlaps (Partial / cross-language)
All three implement the same conceptual NLP-preprocessing recipe for clinical or
survey free text: lowercase the text, tokenise, drop stopwords and
non-alphabetic / short tokens, and build a frequency/document representation.
- stm-survey-text: `tolower` → expand contractions → strip non-alnum, digits,
  single-char tokens → lemmatise → `tokens_remove(pattern = StopWords)` →
  document-feature matrix (quanteda).
- nlp_renal_biopsy: `[token.text for token in self.nlp(text.lower()) if
  token.is_alpha and token.text not in self.stop_words]` → gensim
  dictionary/bag-of-words (spaCy + gensim).
- P43_LTHMedCat: spaCy-backed MedCAT pipeline with stopword/component disabling
  and negspacy clinical termsets — the same lowercase/tokenise/stopword concern,
  embedded in clinical-NER setup.

## Shared vs bespoke
Shared: the lowercase → tokenise → remove stopwords → frequency-matrix recipe.
Bespoke: the libraries differ (quanteda vs spaCy vs MedCAT), and each hardcodes
its own input column / document source (`data$Response`, `report[section_key]`,
a neurology-letters CSV). This is a semantic overlap, not a copy-paste clone:
consolidation would mean a documented, language-agnostic "clinical free-text
normalisation" reference spec rather than a single shared function. Worth
flagging because the same preprocessing decisions are being re-litigated in
three NHS repos.
