"""Source: P12/P21 SynthVAE — https://github.com/nhsx/SynthVAE (metrics.py)"""

import numpy as np
import pandas as pd
import gower
from sdv.evaluation import evaluate
from sdv.metrics.tabular import NumericalMLP, CategoricalSVM


def distribution_metrics(distributional_metrics, data_supp, synthetic_supp, categorical_columns, include_gower=False):
    synthetic_supp = synthetic_supp[data_supp.columns]
    synthetic_supp[categorical_columns] = synthetic_supp[categorical_columns].astype(object)
    data_supp[categorical_columns] = data_supp[categorical_columns].astype(object)

    evals = evaluate(synthetic_supp, data_supp, metrics=distributional_metrics, aggregate=False)
    metrics = np.array(evals["raw_score"])

    if include_gower:
        metrics = np.append(metrics, np.mean(gower.gower_matrix(data_supp, synthetic_supp)))
        return pd.DataFrame(data=[metrics], columns=(distributional_metrics + ["Gower"]))

    return pd.DataFrame(data=[metrics], columns=distributional_metrics)


def privacy_metric(private_variable, data_supp, synthetic_supp, categorical_columns, continuous_columns):
    if private_variable in continuous_columns:
        key_fields = [c for c in continuous_columns if c != private_variable]
        return NumericalMLP.compute(
            data_supp.fillna(0),
            synthetic_supp.fillna(0),
            key_fields=key_fields,
            sensitive_fields=[private_variable],
        )

    key_fields = [c for c in categorical_columns if c != private_variable]
    return CategoricalSVM.compute(
        data_supp.fillna(0),
        synthetic_supp.fillna(0),
        key_fields=key_fields,
        sensitive_fields=[private_variable],
    )
