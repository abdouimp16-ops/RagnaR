import numpy as np
import pandas as pd
from math import sqrt, log, exp, pi


def norm_ppf(p: float) -> float:
    a = [-3.969683028665376e+01, 2.209460984245205e+02,
         -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02,
         -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01,
         2.445134137142996e+00, 3.754408661907416e+00]

    plow, phigh = 0.02425, 1 - 0.02425

    if p < plow:
        q = sqrt(-2 * log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p > phigh:
        q = sqrt(-2 * log(1-p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    else:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def auc_score(y_true, y_prob) -> float:
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    n_pos = (y_true == 1).sum()
    n_neg = (y_true == 0).sum()
    if n_pos == 0 or n_neg == 0:
        return 0.5
    ranks = pd.Series(y_prob).rank(method="average")
    s_pos = ranks[y_true == 1].sum()
    return (s_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def deflated_sharpe(sharpe: float, n_trials: int, n_obs: int, skew: float = 0, kurt: float = 3) -> float:
    sr = sharpe
    euler = 0.5772156649
    z = norm_ppf(1 - 1 / max(n_trials, 1))
    sr_deflated = sr - z * sqrt((1 - skew * sr + (kurt - 1) * sr**2 / 4) / max(n_obs, 1))
    return sr_deflated


def pbo_cscv(returns: np.ndarray, n_splits: int = 16, n_combos: int = 100) -> float:
    returns = np.asarray(returns)
    if len(returns) < 40:
        return 1.0
    n = len(returns)
    split = n // 2
    below = 0
    for _ in range(n_combos):
        idx = np.arange(n)
        np.random.shuffle(idx)
        in_sample = returns[idx[:split]]
        out_sample = returns[idx[split:]]
        sr_is = in_sample.mean() / (in_sample.std() + 1e-12)
        sr_oos = out_sample.mean() / (out_sample.std() + 1e-12)
        if sr_oos < sr_is:
            below += 1
    return below / n_combos


def wilson_lower(successes: int, total: int, z: float = 1.96) -> float:
    if total == 0:
        return 0.0
    p = successes / total
    denom = 1 + z**2 / total
    center = p + z**2 / (2 * total)
    margin = z * sqrt((p * (1 - p) + z**2 / (4 * total)) / total)
    return max(0.0, (center - margin) / denom)


def sharpe_from_returns(returns: np.ndarray) -> float:
    if len(returns) < 2 or returns.std() == 0:
        return 0.0
    return returns.mean() / returns.std() * sqrt(len(returns))
