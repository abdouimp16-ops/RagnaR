import numpy as np
import pandas as pd
from cv import auc_score


class MetaLayer:
    def __init__(self, auc_threshold: float = 0.53):
        self.auc_threshold = auc_threshold
        self.weights = None
        self.bias = 0.0
        self.active = False

    def fit(self, X_meta: np.ndarray, y_true: np.ndarray, sample_weight: np.ndarray | None = None):
        n, d = X_meta.shape
        if sample_weight is None:
            sample_weight = np.ones(n)
        y_bin = np.where(y_true > 0.5, 1.0, -1.0)

        # Simple single-layer perceptron
        self.weights = np.zeros(d)
        lr = 0.05
        for _ in range(200):
            z = X_meta @ self.weights + self.bias
            z = np.clip(z, -50, 50)
            p = 1 / (1 + np.exp(-z))
            err = p - y_true
            self.weights -= lr * (X_meta.T @ (err * sample_weight)) / n
            self.bias -= lr * (err * sample_weight).sum() / n

        p = self.predict_proba(X_meta)
        auc = auc_score(y_true, p)
        self.active = auc > self.auc_threshold
        return auc

    def predict_proba(self, X_meta: np.ndarray) -> np.ndarray:
        if self.weights is None:
            return np.full(X_meta.shape[0], 0.5)
        z = X_meta @ self.weights + self.bias
        z = np.clip(z, -50, 50)
        return 1 / (1 + np.exp(-z))

    def should_activate(self):
        return self.active


def build_meta_features(prob_ens: np.ndarray, prob_log: np.ndarray, prob_gbm: np.ndarray,
                        score_rules: np.ndarray, regime_mult: np.ndarray,
                        vol_z: np.ndarray, trend_strength: np.ndarray) -> np.ndarray:
    return np.column_stack([
        prob_ens,
        prob_log,
        prob_gbm,
        np.abs(prob_log - prob_gbm),
        score_rules,
        regime_mult,
        vol_z,
        trend_strength,
    ])
