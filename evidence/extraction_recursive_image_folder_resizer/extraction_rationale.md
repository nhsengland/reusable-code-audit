# Extraction Rationale: recursive_image_folder_resizer

## What
`txt-ray-align/data/resize.py` lines 28-98: a `Dataset`/`DataLoader`-parallelised bulk image
resizer. It globs all images under a root folder, resizes them with torchvision transforms in
worker processes, and writes them to a mirrored directory tree (`<folder>_res`) preserving the
nested sub-structure (MIMIC-CXR's `p1x/p1xxxxxxx/sxxxxxxx/*.jpg` layout survives intact).

## Why it is reusable
Downsampling a large research imaging corpus once, up front, while preserving folder structure
is a routine chore for any imaging project (X-ray, retinal, dermatology, histopathology tiles).
Using a torch `DataLoader` for free multiprocess parallelism is a neat, generic trick; nothing
here depends on MIMIC-CXR semantics.

## Tangled bespoke logic to parameterise
1. **Extension hardcoded**: glob is fixed to `**/*.jpg` (line 33) and output `format="JPEG"`
   (line 86). Parameterise input glob/extensions and output format/quality (PNG/DICOM-derived
   JPEG workflows differ).
2. **Output naming convention hardcoded**: destination is always sibling folder
   `<name>_res` (lines 58-60) and the path-rewrite logic locates the source folder name inside
   each file path (lines 77-79) — fragile if the name repeats in the tree. Accept an explicit
   `output_folder` and compute relative paths with `Path.relative_to`.
3. **Aspect handling**: `T.Resize(size=resize_to)` resizes the short side only; expose the full
   torchvision transform (or target size tuple) as a parameter.
4. No overwrite/skip-existing flag — add idempotency for resumable runs.
