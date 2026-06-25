# Extraction Candidate: Prompt-template load/validate/save helper

## What it is
`prompt_template_handler.py` from `nlp_renal_biopsy/src/ner/`. A small generic
module that loads a prompt template from JSON, validates that all
`{placeholder}` tokens required by the caller are present (raising a typed
`PromptTemplateError` otherwise), and saves templates back to JSON creating
parent directories as needed.

## Why it is reusable (Utility)
Externalising prompts to files and validating that required interpolation slots
exist before runtime is good practice for any LLM pipeline. evalsense uses
`format_template` (raising on missing keys) for the same concern at format time;
this module does it at load time. A combined "prompt template with declared
required placeholders, validated on load and on format" utility would serve both
repos and any LLM healthcare project.

## What must be parameterised to untangle it
The core `load_and_validate_prompt_template` / `save_template_to_json` are
already fully generic (placeholders passed as an argument). The only coupling is
the convenience wrappers that hardcode domain placeholder sets:
- `load_and_validate_extraction_prompt_template` hardcodes
  `["input_text","entity_name"]`.
- `load_and_validate_generate_prompt_template` hardcodes `["data"]`.
- The JSON key `"prompt_template"` is hardcoded as the template field name.
To untangle: drop the domain wrappers (or move them to the renal/NER package)
and expose the JSON field name as a parameter; ship only the generic core.
