# Extraction Candidate: Multi-provider LLM generation wrapper

## What it is
The `LLMGenerator` class from priv-lm-health-extended
(`privacy_in_context/generations.py:1-100`). A single interface that dispatches to one of
three back-ends chosen at construction by a `provider` string:
- **anthropic** — `anthropic.Anthropic` client, `messages.create`, returning
  `(message.content[0].text, message.stop_reason)`;
- **openai** — `OpenAI` client, `chat.completions.create`, returning
  `(content, finish_reason)`;
- **huggingface** — local `AutoModelForCausalLM` + `AutoTokenizer`, device/dtype auto-selected,
  `model.generate` under `torch.no_grad()`, returning the prompt-stripped continuation.

A uniform `generate(prompt, max_tokens, temperature)` method hides the per-provider call
shape and error handling (each branch logs and returns `("", "error")` on exception).

## Why it is reusable (Utility)
A provider-agnostic `generate(prompt) -> (text, stop_reason)` facade over Anthropic, OpenAI,
and local HuggingFace models is broadly useful: any project that wants to swap between a
hosted API and a local model — for cost, privacy, or benchmarking reasons — needs exactly
this abstraction. It is independent of the privacy-in-context experiment it currently lives
in, and is a cleaner version of the bespoke per-provider call sites scattered across other
repos.

## What must be parameterised to untangle it
- **API keys** — already read from `kwargs.get("api_key")` falling back to
  `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` env vars; keep, and document.
- **Generation defaults** — `max_tokens=5000`, `temperature=0.0` are reasonable defaults but
  should remain arguments (they are).
- **Provider registry** — the `if/elif` provider dispatch is closed; to extend it cleanly,
  refactor to a small provider-handler registry so new back-ends can be registered without
  editing the constructor.
- **Anthropic model id** — passed in as `model_name`, so no hardcoded model; this is correct
  and should be preserved. (See the `claude-api` reference for current Claude model ids when
  documenting defaults — none are hardcoded here, which is the desired state.)
- No project-specific imports; the class is already standalone bar the optional API-key env
  vars.
