"""Source: P34 Hypergraph-MM — https://github.com/nhsx/hypergraph-mm (hypmm/weight_functions.py)"""

import numba
import numpy as np


@numba.njit(fastmath=True, nogil=True)
def comp_overlap_coeff(prev_arr, inds, denom_arr):
    n_diseases = inds.shape[0]
    inds = inds.astype(np.int64)

    bin_int = 0
    for i in range(n_diseases):
        bin_int += 2 ** inds[i]

    numerator = prev_arr[bin_int]

    denominator = denom_arr[inds[0]]
    for i in range(1, n_diseases):
        new_denom = denom_arr[inds[i]]
        if new_denom < denominator:
            denominator = new_denom

    return numerator / denominator, denominator
