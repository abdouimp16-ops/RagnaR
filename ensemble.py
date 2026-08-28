import numpy as np
import pandas as pd


class LogisticRegression:
    def __init__(self, l2: float = 1.0, lr: float = 0.05, epochs: int = 300):
        self.l2 = l2
        self.lr = lr
        self.epochs = epochs
        self.weights = None
        self.bias = 0.0

    def sigmoid(self, z):
        z = np.clip(z, -50, 50)
        return 1 / (1 + np.exp(-z))

    def fit(self, X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray | None = None):
        n, d = X.shape
        self.weights = np.zeros(d)
        if sample_weight is None:
            sample_weight = np.ones(n)
        for _ in range(self.epochs):
            z = X @ self.weights + self.bias
            p = self.sigmoid(z)
            err = p - y
            grad_w = (X.T @ (err * sample_weight)) / n + self.l2 * self.weights
            grad_b = (err * sample_weight).sum() / n
            self.weights -= self.lr * grad_w
            self.bias -= self.lr * grad_b

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.sigmoid(X @ self.weights + self.bias)


class DecisionStump:
    def fit(self, X, y, w):
        best = None
        best_loss = float("inf")
        for j in range(X.shape[1]):
            vals = np.unique(X[:, j])
            if len(vals) > 20:
                quantiles = np.quantile(X[:, j], np.linspace(0.05, 0.95, 20))
                vals = np.unique(quantiles)
            for thr in vals:
                pred = np.where(X[:, j] <= thr, 1.0, -1.0)
                loss = (w * (pred != y)).sum()
                if loss < best_loss:
                    best_loss = loss
                    best = (j, thr, pred.copy())
        return best

    def predict(self, X, model):
        j, thr, _ = model
        return np.where(X[:, j] <= thr, 1.0, -1.0)


class GradientBoosting:
    def __init__(self, n_estimators: int = 160, lr: float = 0.1):
        self.n_estimators = n_estimators
        self.lr = lr
        self.models = []
        self.gamma = []

    def fit(self, X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray | None = None):
        n = len(y)
        if sample_weight is None:
            sample_weight = np.ones(n)
        y_bin = np.where(y > 0.5, 1.0, -1.0)
        F = np.zeros(n)
        stump = DecisionStump()
        for _ in range(self.n_estimators):
            p = 1 / (1 + np.exp(-2 * F))
            w = sample_weight * np.abs(y_bin - p)
            model = stump.fit(X, y_bin, w)
            pred = stump.predict(X, model)
            gamma = (w * y_bin * pred).sum() / (w * pred * pred).sum()
            F += self.lr * gamma * pred
            self.models.append(model)
            self.gamma.append(gamma)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        F = np.zeros(X.shape[0])
        stump = DecisionStump()
        for model, gamma in zip(self.models, self.gamma):
            F += self.lr * gamma * stump.predict(X, model)
        return 1 / (1 + np.exp(-2 * F))


def isotonic_regression(x: np.ndarray, y: np.ndarray):
    order = np.argsort(x)
    x_s, y_s = x[order], y[order]
    y_iso = y_s.copy()
    n = len(y_iso)
    i = 0
    while i < n - 1:
        j = i
        while j < n - 1 and y_iso[j] > y_iso[j + 1]:
            j += 1
        if j > i:
            y_iso[i:j + 1] = y_iso[i:j + 1].mean()
            i = max(0, i - 1)
        else:
            i += 1
    out = np.interp(x, x_s, y_iso)
    return np.clip(out, 0.001, 0.999)


class CalibratedEnsemble:
    def __init__(self, w_logistic: float = 0.4, w_gbm: float = 0.6):
        self.w_logistic = w_logistic
        self.w_gbm = w_gbm
        self.logistic = LogisticRegression()
        self.gbm = GradientBoosting()
        self.calibrator = None

    def fit(self, X, y, sample_weight=None):
        self.logistic.fit(X, y, sample_weight)
        self.gbm.fit(X, y, sample_weight)
        p_log = self.logistic.predict_proba(X)
        p_gbm = self.gbm.predict_proba(X)
        p_ens = self.w_logistic * p_log + self.w_gbm * p_gbm
        self.calibrator = lambda p: isotonic_regression(p, y)
        self._cal_pred = self.calibrator(p_ens)

    def predict_proba(self, X):
        p_log = self.logistic.predict_proba(X)
        p_gbm = self.gbm.predict_proba(X)
        p_ens = self.w_logistic * p_log + self.w_gbm * p_gbm
        return isotonic_regression(p_ens, self._cal_pred)

    def predict_logistic(self, X):
        return self.logistic.predict_proba(X)

    def predict_gbm(self, X):
        return self.gbm.predict_proba(X)
