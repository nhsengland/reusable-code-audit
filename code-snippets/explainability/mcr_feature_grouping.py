"""Source: P14 Model Class Reliance project — https://github.com/nhsx/commercial-data-healthcare-predictions (MCR_for_op_rf.py)"""

import numpy as np


def build_group_index_map(feature_names, grouping_names, grouped_features):
    grouping_names2indexes = {}
    for i, group_name in enumerate(grouping_names):
        grouping_names2indexes[group_name] = np.asarray(
            [feature_names.index(v) for v in grouped_features[i]]
        )
    return grouping_names2indexes
