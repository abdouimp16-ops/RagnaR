import numpy as np
import pandas as pd


def kmeans(X: np.ndarray, k: int, max_iter: int = 100, seed: int = 42):
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(X), k, replace=False)
    centers = X[idx].copy()

    for _ in range(max_iter):
        dists = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = dists.argmin(axis=1)
        new_centers = np.array([X[labels == i].mean(axis=0) if (labels == i).any() else centers[i]
                                for i in range(k)])
        if np.allclose(centers, new_centers):
            break
        centers = new_centers
    return labels, centers


def regime_features(df: pd.DataFrame) -> np.ndarray:
    f = []
    f.append(df["close"].pct_change(20).fillna(0))
    f.append(df["atr"] / df["close"])
    f.append((df["close"] - df["ema200"]) / df["close"])
    f.append(df["adx"] / 100)
    f.append(df["rsi"] / 100)
    f.append(df["vol_ratio"].fillna(1))
    return np.column_stack(f)


def forward_return_sharpe(df: pd.DataFrame, horizon: int = 30) -> pd.Series:
    ret = df["close"].pct_change(horizon).shift(-horizon)
    ret = ret.rolling(horizon).mean() / ret.rolling(horizon).std()
    return ret.fillna(0)


class RegimeClassifier:
    def __init__(self, k: int = 4):
        self.k = k
        self.centers = None
        self.labels = None
        self.regime_sharpes = {}

    def fit(self, df: pd.DataFrame):
        X = regime_features(df)
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-12)
        self.labels, self.centers = kmeans(X, self.k)
        fwd = forward_return_sharpe(df)

        for i in range(self.k):
            mask = self.labels == i
            if mask.any():
                self.regime_sharpes[i] = fwd[mask].mean()
            else:
                self.regime_sharpes[i] = 0.0

        min_s, max_s = min(self.regime_sharpes.values()), max(self.regime_sharpes.values())
        self.regime_mult = {}
        for i, s in self.regime_sharpes.items():
            if max_s - min_s < 1e-9:
                self.regime_mult[i] = 1.0
            else:
                normalized = (s - min_s) / (max_s - min_s)
                self.regime_mult[i] = 0.35 + normalized * 1.15

    def predict(self, df: pd.DataFrame) -> int:
        X = regime_features(df)
        X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-12)
        row = X[-1]
        dists = ((row[None, :] - self.centers) ** 2).sum(axis=1)
        return int(dists.argmin())

    def get_multiplier(self, label: int) -> float:
        return self.regime_mult.get(label, 1.0)

    def allowed_directions(self, label: int) -> dict:
        s = self.regime_sharpes.get(label, 0)
        return {"LONG": s > -0.05, "SHORT": s > -0.05}
