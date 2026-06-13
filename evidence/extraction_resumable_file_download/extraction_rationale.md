# Extraction Candidate: Resumable, hash-verified file downloader

## What it is
A self-contained HTTP file-download utility (`download_file`, `verify_file`,
`get_remote_file_headers`, `to_safe_filename`) from `evalsense/utils/files.py`.
It performs streaming download with a tqdm progress bar, exponential-backoff
retries (tenacity), HTTP range-based resume of partial downloads, detection of
compression encodings that preclude resume, and integrity verification by
expected size and configurable hash algorithm.

## Why it is reusable (Utility)
This is generic infrastructure entirely independent of any dataset, model, or
clinical domain. Any healthcare-analytics project that pulls large model
weights, public datasets, lexicons, or reference files from a URL needs exactly
this. It is markedly more robust than the ad-hoc `hf_hub_download` /
`requests.get` patterns found in the other repos (e.g. nlp_renal_biopsy
`download_llm_model_from_hf`), offering resume, retry, and integrity checks that
those lack.

## What must be parameterised to untangle it
Very little — the function is already well-parameterised. To extract cleanly:
- Replace the two `evalsense.constants` imports (`USER_AGENT`,
  `DEFAULT_HASH_TYPE`) with constructor/argument defaults so there is no
  dependency on the evalsense package namespace.
- `USER_AGENT = "EvalSense/0"` is hardcoded in constants; expose it as a
  parameter with a neutral default.
That is the only coupling; the download/verify logic itself is domain-neutral.
