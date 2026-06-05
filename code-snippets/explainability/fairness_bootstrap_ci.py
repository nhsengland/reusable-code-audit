"""Source: P61/P81 MM-HealthFair — https://github.com/nhsengland/mm-healthfair (src/utils/fairness_utils.py)"""

import numpy as np
from scipy.stats import norm


def bias_corrected_ci(bootstrap_samples, observed_value):
    sorted_samples = np.sort(bootstrap_samples)
    z0 = norm.ppf((np.sum(sorted_samples < observed_value) + 0.5) / len(sorted_samples))

    jackknife_estimates = [np.mean(np.delete(sorted_samples, i)) for i in range(len(sorted_samples))]
    mean_jackknife = np.mean(jackknife_estimates)
    a = np.sum((mean_jackknife - jackknife_estimates) ** 3) / (
        6 * (np.sum((mean_jackknife - jackknife_estimates) ** 2) ** 1.5)
    )

    alpha = [0.025, 0.975]
    adjusted_percentiles = norm.cdf(z0 + (z0 + norm.ppf(alpha)) / (1 - a * (z0 + norm.ppf(alpha))))

    if np.isnan(adjusted_percentiles[0]):
        adjusted_percentiles = alpha

    lower = np.percentile(sorted_samples, adjusted_percentiles[0] * 100)
    upper = np.percentile(sorted_samples, adjusted_percentiles[1] * 100)
    return lower, upper
