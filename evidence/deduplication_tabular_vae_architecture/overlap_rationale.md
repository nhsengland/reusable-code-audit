# Deduplication: Tabular VAE Architecture (Encoder/Decoder/Noiser/ELBO)

## Shared functionality
Both repos implement the *same* VAE for mixed-type tabular data; NHSSynth's is a direct descendant of SynthVAE's (NHSSynth historically grew out of SynthVAE).

Line-by-line correspondences:
- **Encoder**: SynthVAE `VAE.py` 14-44 vs NHSSynth `vae.py` 25-54 — identical 2-hidden-layer MLP emitting `2 * latent_dim` outputs, identical `mu_z = outs[:, :latent_dim]` / `logsigma_z = outs[:, latent_dim:]` split, even identical docstring ("diagonal Gaussian variational posterior assumed").
- **Decoder**: SynthVAE 47-81 vs NHSSynth 57-84 — identical MLP shape.
- **Noiser**: SynthVAE 84-93 vs NHSSynth 87-96 — same zero-initialised per-feature log-sigma linear layer (NHSSynth unfreezes the weights and changes bias init to -0.5).
- **Loss/ELBO**: SynthVAE `loss()` 139-179 vs NHSSynth `loss()` 325-401 — same structure: KL(q‖N(0,1)) + reparameterised sample + per-categorical-group cross-entropy + Gaussian log-likelihood through the Noiser. NHSSynth adds free bits, logsigma clamping, beta annealing and a binary (missingness) head.
- **Generation**: SynthVAE `generate()` 116-137 vs NHSSynth `generate()` 203-323 — same one-hot-categorical sampling per categorical block plus Gaussian noise on continuous columns; NHSSynth adds temperature scaling and metadata-driven column grouping.

## State: Tangled/Partial Overlap
**Shared (semantic core):** encoder/decoder topology, reparameterisation, KL + mixed-likelihood ELBO decomposition, one-hot categorical sampling at generation time, early-stopped epoch loop.

**Bespoke per repo:**
- SynthVAE: contiguous-block column convention (`num_categories` list with categoricals first, continuous last — `x_gen_[:, -num_continuous:]`), per-class GPU print statements, training loop embedded in the model class (`train`/`diff_priv_train`, lines 181-397).
- NHSSynth: `Model` base-class integration (`self.metatransformer`, `multi_column_indices`), column-suffix string conventions (`_normalised`, `_value`, `_c\d+` regex at vae.py 280-292), adaptive temperature constants (3.0/1.5/5.0/2.0), KL annealing/free-bits, learned latent statistics, posterior-collapse diagnostics.

## Recommendation
One canonical tabular-VAE module (NHSSynth's is strictly more capable) parameterised by a column-grouping descriptor (list of index groups + continuous indices) rather than either repo's bespoke convention (positional blocks vs name suffixes). SynthVAE should then be archived as a consumer or marked superseded.
