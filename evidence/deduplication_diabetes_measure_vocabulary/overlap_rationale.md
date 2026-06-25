# Deduplication Case: Diabetes Measure / Observation Vocabulary

**What it does:** Defines a controlled vocabulary of diabetes-relevant clinical
measures and condition labels — HbA1c, BMI, GFR, diastolic BP, urine
microalbumin, haemoglobin, smoking status, and Type 1 / Type 2 diabetes
sub-categories — together with rename maps that fold many verbose source codes
(CTV3 descriptions, named observation variables) into a small canonical set used
downstream for summarisation and synthetic-record generation.

**Why it is an overlap:** Two repositories independently hardcode essentially the
same diabetes measurement panel, expressed against different coding conventions:

| Repo | File | Vocabulary |
|---|---|---|
| ESNEFT_diabetes_StephenRicher | `scripts/utils.py` (lines 95–107, 167–196, 240–249) | `CTV3Desc_rename` map (CTV3 long descriptions → `HbA1c`, `BMI`, `GFR`, `Diastolic BP`, `Urine Microalbumin`, …); `type1_default` / `type2_default` label lists; `measures` list driving longitudinal summaries |
| SynPath_Diabetes | `t2dm/create_patients.ipynb` (Cell 1) | `observationsVars` (`egfr`, `haemoglobin`, `hba1c`, `hdlCholesterol`, `systolicBloodPressure`, `weight`, …) and `conditionsVars` (`af`, `albuminuria`, `currentSmoker`, `history_MI`, `history_Stroke`, `pvd`, …) used to melt a wide patient CSV |

Both are encoding the same domain concept — "the set of measures and conditions
that characterise a diabetes patient" — but one keys it on ESNEFT CTV3 read-code
descriptions and the other on bespoke camelCase column names. This is a
**semantic / vocabulary overlap**: the same clinical panel, duplicated as two
incompatible string vocabularies.

**Shared vs bespoke (Partial Overlap):**
- *Shared core:* the canonical measure panel (HbA1c, BMI, eGFR/GFR, blood
  pressure, urine microalbumin, lipids, haemoglobin) and the Type 1 / Type 2
  diabetes condition distinction.
- *Bespoke (must be parameterised, not shared verbatim):* ESNEFT's keys are CTV3
  long-description strings specific to the ESNEFT extract (e.g. `'Haemoglobin A1c
  level - IFCC standardised'`, `'GFR calculated Cockcroft-Gault formula'`);
  SynPath's keys are simulation variable names. The Type 1/2 label *lists* in
  ESNEFT are read-code phrasings, whereas SynPath has no diabetes-type strings at
  all (it is implicitly T2DM). These mappings are coding-system-specific and
  belong in injected lookup tables.

**Consolidation plan:** Externalise a single canonical diabetes measure/condition
vocabulary (e.g. a small reference module or YAML) naming the panel and the
T1D/T2D label sets, plus per-source rename maps (`ctv3_to_canonical`,
`synpath_to_canonical`) that each project supplies. Code then references the
canonical names rather than re-declaring CTV3 strings or column lists inline.
