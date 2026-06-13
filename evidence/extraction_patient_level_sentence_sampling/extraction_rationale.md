# Extraction Candidate: Patient-level sentence sampling for privacy evaluation

## What it is
The patient-stratified sentence-sampling helpers from priv-lm-health
(`privlm/mi_attack.py:26-146`): `get_subject_ids`, `create_member_df`,
`create_non_member_df`, `prep_mimic_for_MI`, and `prep_i2b2_for_MI`. The two `prep_*`
functions implement the same recipe over different sources — randomly select N patients by
subject id, gather their notes, sentence-tokenise (`nltk.sent_tokenize`), deduplicate, keep
only sentences of at least `min_len_sentences` characters, shuffle, and take the first
`number_of_sentences` — producing a fixed-size pool of patient-derived sentences for a
membership-inference experiment. `prep_mimic_for_MI` consumes a DataFrame; `prep_i2b2_for_MI`
walks a directory of i2b2 XML files (subject id from the filename prefix, text from
`<TEXT>` via BeautifulSoup).

## Why it is reusable (Utility)
"Sample a balanced, fixed-size set of sentences grouped by patient, with a minimum-length
filter and reproducible shuffling" is a generic preparation step for any privacy/membership
experiment over clinical notes — the same pattern would serve any corpus with a
patient/subject identifier. The patient-level grouping (selecting whole subjects before
sampling their sentences, rather than sampling sentences globally) is the methodologically
important, reusable part.

## What must be parameterised to untangle it
- **Column names** — `SUBJECT_ID` / `TEXT` are hardcoded; expose as arguments (these are the
  MIMIC names and will differ on other corpora).
- **Source abstraction** — the MIMIC (DataFrame) and i2b2 (XML directory) variants share the
  select-patients → tokenise → filter → sample core. Extract that core to operate on a
  `{subject_id: [text]}` mapping, with thin source-specific loaders (DataFrame reader; XML
  walker) feeding it. The i2b2 subject-id-from-`[0:3]`-of-filename rule is dataset-specific
  and stays in its loader.
- **Sampling sizes** — `number_of_patients=90`, `number_of_sentences=4072`,
  `min_len_sentences=20` are already arguments; the hard `assert len(...) == N` checks should
  become a clear error (or a warning) so the helper degrades gracefully when a corpus is
  smaller than requested.
- **Seeding** — the functions call the global `random.shuffle`; thread an explicit seed/RNG
  through for reproducibility.
