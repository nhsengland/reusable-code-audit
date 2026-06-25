# Deduplication Overlap: Clinical / survey free-text cleaning pipelines

## Repos involved
- stm-survey-text (R) — `R/main/functions.R` `clean_text`
- nlp_renal_biopsy (Python) — `src/preprocessing/eda.py` tokenisation
- P43_LTHMedCat (Python) — `notebooks/common.py` MedCAT/negspacy pipeline setup
- ELM4PSIR (Python) — `classification_tasks/.../datasets/preprocess/utils.py` `get_clean_text` (lower-casing + markup/newline normalisation of NHS patient-safety incident free-text)

## What overlaps (Partial / cross-language)
All four implement the same conceptual NLP-preprocessing recipe for clinical or
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
- ELM4PSIR: `get_clean_text` lower-cases and normalises markup/newline artefacts
  (`<br />`, `&#xd;`, `\\n`) specific to the incident-report export format — the
  upstream "normalise before tokenise" half of the same recipe.

## Shared vs bespoke
Shared: the lowercase → normalise → tokenise → remove stopwords → frequency-matrix
recipe. Bespoke: the libraries differ (quanteda vs spaCy vs MedCAT vs plain
`str.replace`), and each hardcodes its own input column / document source
(`data$Response`, `report[section_key]`, a neurology-letters CSV) and its own
markup-replacement map (ELM4PSIR's `&#xd;`/`<br />` set is specific to the
LFPSE/incident export). This is a semantic overlap, not a copy-paste clone:
consolidation would mean a documented, language-agnostic "clinical free-text
normalisation" reference spec — `clean_text(text, replacement_map=None,
stopwords=None)` plus a downstream tokeniser — rather than a single shared
function. Worth flagging because the same preprocessing decisions are being
re-litigated in four NHS repos.
