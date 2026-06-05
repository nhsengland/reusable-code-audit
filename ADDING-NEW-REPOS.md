# ADDING NEW REPOSITORIES TO THE CATALOG

## Purpose

This catalog is a living artifact. When a new repository is audited, compare it against existing catalog entries first, then update overlaps and add any genuinely new reusable patterns.

## Step-by-Step Process

### Step 1 — Profile the new repo

- Record language(s), key libraries, and main functional areas.
- Map the repository to one or more existing themes in `catalog.yml`.
- If no existing theme fits, propose a new theme ID/label.

### Step 2 — Compare against existing catalog entries

- For each relevant theme, review matching `snippets` entries in `catalog.yml`.
- Ask whether the new repository implements the same pattern:
  - **If YES**: update the existing snippet entry:
    - add the project ID to `source_projects`
    - add source attribution under `source_repos`
    - increment `overlap_count`
  - **If NO (new pattern)**: create a new snippet entry in the same theme.

### Step 3 — Add new snippets

- Save the snippet file under `code-snippets/<theme>/` with a descriptive filename.
- Add a source attribution header comment in the snippet file (project, repo URL, original file path).
- Add/update the corresponding snippet entry in `catalog.yml`.

### Step 4 — Update `catalog.md`

- Refresh summary stats (projects/themes/snippets/reuse candidates).
- Update the overlap summary table and per-theme sections.
- Update the cross-project overlap map counts.
- Ensure the new snippet code is embedded in the relevant theme “Raw snippets” section.

### Step 5 — Update `audit-report.md`

- Add the new project to the Project Inventory table.
- Update Findings by Theme and the Reuse Opportunity Matrix.
- Update recommendations if the new repo changes prioritization.

## Template: New Catalog Entry

```yaml
- id: THEME-NNN
  title: ""
  theme: ""
  file: "code-snippets/<theme>/<filename>.py"
  source_projects: []
  source_repos:
    - url: ""
      file: ""
  overlap_count: 1
  reuse_candidate: true
  reuse_notes: ""
  suggested_library_module: ""
```

## Checklist

- [ ] New project ID and repo URL added to repository documentation.
- [ ] New project mapped to existing theme(s) (or new theme added).
- [ ] Existing snippet overlaps updated in `catalog.yml` where applicable.
- [ ] New snippet files added to `code-snippets/<theme>/` with source headers.
- [ ] New snippet entries added to `catalog.yml` with overlap and reuse metadata.
- [ ] `catalog.md` regenerated/updated (summary tables, per-theme sections, raw snippet blocks, overlap matrix).
- [ ] `audit-report.md` inventory/findings/matrix sections updated.
- [ ] Final consistency check completed (`catalog.yml` and `catalog.md` counts align).
