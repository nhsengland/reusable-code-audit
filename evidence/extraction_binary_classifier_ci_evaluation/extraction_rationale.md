# Extraction Rationale: binary_classifier_ci_evaluation

## What
A cohesive cluster in `mm-healthfair/src/utils/eval_utils.py` (lines 190-341):

- `expect_f1()` / `optimal_threshold()` — threshold selection by maximising the *expected* F1
  computed directly from predicted probabilities (no labels needed for the sweep).
- `get_roc_performance()` — Youden's J optimal operating point, then ROC-AUC, PPV, NPV,
  sensitivity and specificity each with 95% CIs via the `confidenceinterval` package.
- `get_pr_performance()` — PR-AUC with an analytic 95% CI derived from a covariance matrix of
  precision/recall standard errors, plus optimal-F1 thresholded classification report.

## Why it is reusable
This is exactly the evaluation battery required of any binary clinical risk model
(NHS guidance expects CIs on discrimination metrics, an operating-point justification, and
sensitivity/specificity reporting). The functions take only `y_test` and `prob` arrays — they
are completely independent of MIMIC-IV, the multimodal model and the fairness pipeline, yet
they currently live inside a project-specific `utils` package and will inevitably be re-written
by the next risk-prediction project.

## Tangled bespoke logic to parameterise
1. **Confidence level hardcoded**: `confidence_level=0.95` repeated in every `cfi.*_score` call
   (lines 251-255, 305-308) and `z = stats.norm.ppf(1 - 0.05 / 2)` (line 323) and `1.96`
   (lines 330-331). Expose a single `confidence_level` parameter and derive z from it.
2. **Mixed printing and computing**: `verbose` blocks print classification reports inline;
   extract to a returned dict / structured result so library callers are not forced through
   stdout.
3. **Result-dict key contract**: keys such as `"roc_upper"`, `"pr_lower"`, `"yd_idx"`,
   `"f1_thres"` are an implicit interface consumed by the plotting helpers earlier in the same
   file (`plot_roc` line 87, `plot_pr` line 140). Formalise as a small dataclass.
4. **`pos_label=1` assumption** (lines 239, 289): expose as a parameter for cohorts where the
   positive class is encoded differently.
