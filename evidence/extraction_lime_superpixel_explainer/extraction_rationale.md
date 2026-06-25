# Extraction Rationale: lime_superpixel_explainer

## What
`LIME-XAI-Facial-Disease-Classification/Investigations/Explain_working_con.ipynb`
(code cells 5-19): a complete from-scratch implementation of LIME for image classifiers —
quickshift superpixel segmentation, random binary perturbation matrix, `perturb_image()`
masking function, model inference over perturbations, cosine-distance exponential kernel
weighting, weighted linear surrogate model (sklearn `LinearRegression`), and top-k superpixel
mask visualisation.

## Why it is reusable
This is the only substantive algorithmic code in the repository and it is model-agnostic: the
classifier only enters through `model.predict`. A function/class taking
(`predict_fn`, `image`, `segmentation_params`, `num_perturbations`, `kernel_width`,
`num_top_features`) would serve any Keras/PyTorch image classifier needing local explanations,
and is a useful teaching/audit alternative to the `lime` PyPI package because every step is
inspectable. Currently it is scattered across notebook cells with global state, so it cannot be
imported anywhere.

## Tangled bespoke logic to parameterise
1. **Inception-specific preprocessing tangled in** (code cell 5): `resize(Xi, (299, 299))` and
   `(Xi - 0.5) * 2`, with the matching un-preprocess `Xi / 2 + 0.5` repeated in the display
   cells (cells 10, 13, 19). Accept a preprocessed image plus an optional
   `inverse_preprocess_fn` for display.
2. **Hardcoded model and image paths** (cells 4-5): `"../models/incepv3con.h5"`,
   `"../data/test.jpeg"` — must become arguments.
3. **Magic numbers**: `num_perturb = 150` (cell 11), `kernel_width = 0.25` (cell 16),
   quickshift `kernel_size=4, max_dist=200, ratio=0.2` (cell 9), `num_top_features = 25`
   (cell 18), `np.random.seed(222)` (cells 2, 6) — all should be keyword parameters with these
   as defaults, and the RNG should be a passed-in `numpy.random.Generator`.
4. **Class selection** (cells 8, 17): `top_pred_classes[0]` is implicit; expose
   `class_to_explain` as a parameter.
5. Surrogate model fixed to `LinearRegression`; allow ridge/lasso injection as in canonical
   LIME.
