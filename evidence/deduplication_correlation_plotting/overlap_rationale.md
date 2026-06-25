# Deduplication: Real-vs-Synthetic Correlation-Matrix Plotting

## Shared functionality
Both repos provide diagnostic plotting that compares real against synthetic
tabular data. The specific overlap is the **correlation-matrix triptych**: plot
the real correlation matrix, plot the synthetic correlation matrix, then plot
their element-wise difference annotated with a Gower distance and a correlation
RMSE.

- SynthVAE `plot.py` (1-153): a live, argparse-driven script. After loading the
  SUPPORT data, restoring a trained VAE and generating a synthetic sample, lines
  110-154 build the three `matshow` figures using the
  `make_axes_locatable`/`append_axes("right", size="5%", pad=0.05)` colorbar
  recipe (credited to a StackOverflow answer), with the diff plot titled by
  `gower.gower_matrix` mean and `sqrt(mean((real.corr - synth.corr)**2))`.
- NHSSynth `modules/plotting/plots.py` (68-217): the **identical** SynthVAE
  correlation-plotting block is preserved **verbatim but commented out** —
  literal evidence of the copy lineage (NHSSynth grew out of SynthVAE). The only
  live plotting in this module is `tsne()` (27-65), a Plotly t-SNE scatter of
  real vs synthetic points, plus the `factorize_all_categoricals` helper
  (11-24) that numerically encodes and min-max scales every column.

## State: Partial Overlap (one side vestigial)
**Shared:** the conceptual pairing of a real and a synthetic dataframe for visual
fidelity comparison; the correlation-matrix-difference plot with Gower + RMSE
summary statistics; the StackOverflow colorbar-sizing idiom (byte-for-byte
identical in both files).

**Bespoke per repo:**
- SynthVAE: matplotlib backend; the whole block is welded into an end-to-end
  script that hardcodes the SUPPORT dataset (`pycox.datasets.support`), the
  `original_continuous_columns = ["duration"] + x7..x14` / `["event"] + x1..x6`
  schema, GMM pre-processing, VAE reconstruction and the
  `actual_corr_{}.png` / `sample_corr_{}.png` / `diff_corr_{}.png` filename
  pattern keyed on `pre_proc_method`. There is no reusable function boundary —
  it is top-level script body.
- NHSSynth: the correlation code is dead (commented out); the live contribution
  is a separate **t-SNE** projection plot built on Plotly, plus
  `factorize_all_categoricals` (object→`pd.factorize`, datetime→numeric,
  then min-max scaling). `fig.show()` with no save path; no Gower/RMSE.

## What must be parameterised
A single `plot_correlation_comparison(real_df, synth_df, *, distance_fn=None,
save_path_template=None, show=False)` utility should:
- take two already-prepared dataframes (no dataset loading, no VAE, no
  pre-processing) — removing SynthVAE's SUPPORT/GMM/VAE coupling entirely;
- compute `real.corr()`, `synth.corr()` and their difference, rendering all
  three with a shared, injected colorbar helper;
- accept an optional distance callable (default Gower) and always report the
  correlation RMSE in the diff-plot title;
- parameterise the output filenames (drop the hardcoded `*_corr_{}.png`
  pattern) and make saving vs `show()` a caller choice (reconciling SynthVAE's
  `savefig` with NHSSynth's `fig.show()`).

The companion `factorize_all_categoricals` + `tsne()` pair is independently
reusable as a `plot_tsne_comparison(real_df, synth_df)` utility and should be
extracted alongside, since the categorical-factorise/min-max recipe is generic.

## Recommendation
Adopt one plotting module exposing both `plot_correlation_comparison` and
`plot_tsne_comparison`, parameterised on two dataframes only. Delete the dead
commented correlation block in NHSSynth `plots.py` and retire SynthVAE's inline
script body in favour of calling the shared utility.
