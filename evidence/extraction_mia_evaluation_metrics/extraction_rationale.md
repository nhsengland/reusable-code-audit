# Extraction Candidate: Membership-inference evaluation metrics

## What it is
The threshold-based membership-inference scoring functions from priv-lm-health
(`privlm/mi_attack.py:333-463`): `return_predictions_labels`, `return_auc_roc_over_alphas`,
and `calculate_results`. Given per-example test statistics for three populations — members,
non-members, and an external set — these:
- threshold the member statistic at a quantile `alpha` to produce member/non-member/external
  predictions and labels (`return_predictions_labels`);
- sweep a list of `alpha` quantiles, convert per-alpha predictions into class-probability
  features, fit a `LogisticRegression` meta-classifier and report the ROC-AUC for both the
  member-vs-non-member and member-vs-external comparisons (`return_auc_roc_over_alphas`);
- compute rounded precision/recall/F1 for both a loss-based and a likelihood-ratio-based
  attack (`calculate_results`).

## Why it is reusable (Utility / Logic)
Evaluating a membership-inference attack — turning raw per-example statistics into
threshold-swept predictions and standard classification metrics (precision/recall/F1,
ROC-AUC) — is a generic privacy-evaluation capability reusable by any project that runs MIA
against a model, independent of how the underlying statistic was produced. It pairs
naturally with the scoring primitive in
`evidence/deduplication_reference_model_mia_scoring/`: that produces the statistics, this
evaluates them.

## What must be parameterised to untangle it
- **The three-population shape is hardwired** (member / non-member / external). Generalise
  to accept named statistic arrays so a two-population (member vs non-member) attack does
  not have to fake an external set.
- **Label-length bug** — `mem_labels`, `ext_labels`, and several others are sized from
  `len(nonmem_test_statistic)` rather than their own population length
  (e.g. `mem_labels = [1] * len(nonmem_test_statistic)`). Fix to use each population's own
  length on extraction; the current code only works when the populations are equal-sized.
- **`alpha` / `alphas`** — already arguments; keep.
- Decouple from the surrounding attack script (no other `mi_attack` state is used by these
  three functions — they operate purely on the statistic arrays), and expose the rounding
  precision (currently fixed at 3 dp) as an option.
