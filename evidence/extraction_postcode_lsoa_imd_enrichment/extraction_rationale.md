# Extraction Rationale: postcode_lsoa_imd_enrichment

## What
`ProcessMining/Notebooks/2_CADData_to_EVlog.ipynb` (Cells 20–36) and
`ProcessMining/Notebooks/Add_postcodes_to_LSOAs_and_IMD.ipynb` (Cells 4–7) —
near-identical implementations of:

- `fetch(url, relative_path)` — a download-and-cache helper that retrieves a file
  only if not already in a local `cache/` directory.
- Loading the ONS postcode→OA→LSOA→MSOA→LAD lookup (selected columns/dtypes,
  `latin-1`, skipping the header) and normalising the `PCDS` postcode column.
- `produce_LSOA_IMD(df)` — upper-cases the incident postcode, fetches the IMD 2019
  scores CSV, merges the input on postcode→`PCDS`→`LSOA11CD`, then joins IMD
  deciles by `LSOA code (2011)`, returning the deprivation-enriched frame.

## Why it is reusable
This is the canonical UK postcode→LSOA→IMD enrichment pipeline plus a generic
cached-download utility — both broadly useful across NHS/local-authority analytics
(see the `deduplication_postcode_lsoa_imd_linkage` case, where ESNEFT and
commercial-data hit the same need). The `fetch` helper is a clean standalone
Utility; the enrichment is a reusable join once column names are externalised.

## Tangled bespoke logic to parameterise
1. **The two notebooks duplicate each other** — differ only in postcode column
   (`Incident_Postcode` vs `Incident Postcode`), source paths (`source/` prefix),
   join-key casing (`PCDS`/`pcds`, `LSOA11CD`/`lsoa11cd`) and the
   `drop_duplicates` step. These divergences must collapse into one parameterised
   function (postcode column, key names passed in).
2. **Hardcoded URLs**: the ArcGIS postcode-lookup URL and the
   `assets.publishing.service.gov.uk` IMD File 7 URL are embedded (Cells 20/26 and
   5/7). Externalise as config/defaults.
3. **Hardcoded filenames / paths**: `PCD_OA_LSOA_MSOA_LAD_FEB20_UK_LU.csv`, the
   long `Postcode_to_Output_Area...November_2018...csv` name, `cache_path` from
   `os.getcwd()`, `'imd.csv'`. Inject these.
4. **Hardcoded read spec**: `usecols=[2,6,7,8,11]`, `skiprows=1`,
   `encoding='latin-1'` are tied to the specific ONS file vintage — parameterise.
5. **Hardcoded IMD column allow-list** (cell 36 of notebook 2) and the
   `drop_duplicates(subset=['patientID'], keep='first')` step are dataset
   business logic — make the column selection configurable and the dedupe optional.
6. **`global` postcode_LSOA_df** captured by `produce_LSOA_IMD` is an implicit
   dependency — pass the lookup frame in.
