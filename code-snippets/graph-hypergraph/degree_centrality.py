"""Source: P34 Hypergraph-MM — https://github.com/nhsx/hypergraph-mm (hypmm/centrality_utils.py)"""

import numba
import numpy as np


@numba.njit(fastmath=True, nogil=True)
def degree_centrality(inc_mat_tail, inc_mat_head, edge_weights):
    n_diseases, n_edges = inc_mat_tail.shape
    node_degree_tail = np.zeros(n_diseases, dtype=np.float64)
    node_degree_head = np.zeros(n_diseases, dtype=np.float64)

    for i in range(n_diseases):
        for j in range(n_edges):
            node_degree_tail[i] += inc_mat_tail[i, j] * edge_weights[j]
            node_degree_head[i] += inc_mat_head[i, j] * edge_weights[j]

    edge_degree_tail = np.zeros(n_edges, dtype=np.float64)
    edge_degree_head = np.zeros(n_edges, dtype=np.float64)
    for j in range(n_edges):
        for i in range(n_diseases):
            edge_degree_tail[j] += inc_mat_tail[i, j]
            edge_degree_head[j] += inc_mat_head[i, j]

    return (node_degree_tail, node_degree_head), (edge_degree_tail, edge_degree_head)
