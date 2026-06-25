# Extraction Rationale: lsoa_census_indicator_loaders

## What
`ESNEFT_diabetes_StephenRicher/scripts/utils.py` lines 299–331
(`load_english_language`, `load_adult_skills`):

- Two loaders that read raw 2011-Census CSV extracts (English-language
  proficiency and adult-skills/qualifications), strip the leading metadata rows,
  parse the `LSOA11CD:name` cell into a clean LSOA11CD code, index by LSOA, and
  compute a single derived proportion per LSOA — the share of population who
  cannot speak English well, and the share of adults with low/no qualifications.

## Why it is reusable
Loading ONS/Census LSOA-level indicator CSVs and reducing them to a per-LSOA
proportion is a recurring task when supplementing deprivation/demographic
analyses (these specific loaders feed the `postcode_lsoa_imd_linkage` deprivation
work). The pattern — skip metadata header, parse `LSOA11CD:` prefix, aggregate
selected category columns into a numerator/denominator ratio — generalises across
many census tables.

## Tangled bespoke logic to parameterise
1. **Magic CSV-shape constants**: `skiprows=11`, `nrows=34753` (the count of 2011
   English LSOAs) are hardcoded in both loaders (lines 8–9, 27–28). Parameterise
   skiprows/nrows or detect them.
2. **Hardcoded column index sets**: `load_english_language` sums columns `[3,4]`
   over the row total; `load_adult_skills` sums `[0,1]` (lines 13–14, 32–33).
   These category-index choices are table-specific — pass the numerator-column
   indices in.
3. **Hardcoded `dtype` column maps** keyed `{ 'LSOA11CD': str, 0:int, 1:int, … }`
   differ between the two functions (5 vs 7 value columns) — derive from the
   target table rather than hardcode.
4. **`LSOA11CD:` split rule** `x.split(':')[1].strip()` (lines 10, 29) assumes the
   exact ONS cell format; make the code-extraction rule configurable/robust.
5. The two functions are near-identical aside from column indices and width — they
   collapse into one parameterised `load_lsoa_indicator(path, skiprows, nrows,
   numerator_cols)` helper.
