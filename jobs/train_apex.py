import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import config
import numpy as np
import pandas as pd
from cv import auc_score, pbo_cscv, deflated_sharpe
from ensemble import CalibratedEnsemble
from drift import save_model_registry


def load_training_data():
    conn = sqlite3.connect(config.DB_PATH)
    labels = pd.read_sql("SELECT * FROM labels", conn)
    conn.close()

    if len(labels) < 200:
        return None, None, None, None

    # Simplified: would join with features in production
    X = np.random.randn(len(labels), 17)
    y = labels["label"].values
    w = np.ones(len(labels))
    return X, y, w, labels


def purged_kfold(n: int, k: int = 5, embargo: int = 5):
    idx = np.arange(n)
    splits = []
    fold_size = n // k
    for i in range(k):
        test_start = i * fold_size
        test_end = (i + 1) * fold_size if i < k - 1 else n
        test_idx = idx[test_start:test_end]
        embargo_end = min(test_end + embargo, n)
        train_idx = np.concatenate([idx[:test_start], idx[embargo_end:]])
        splits.append((train_idx, test_idx))
    return splits


def run():
    X, y, w, labels = load_training_data()

    if X is None:
        print("NOT_ENOUGH_DATA")
        sys.exit(2)

    # K-Fold مع Purge
    splits = purged_kfold(len(y))
    aucs = []
    returns = []

    for train_idx, test_idx in splits:
        X_tr, X_te = X[train_idx], X[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]
        w_tr = w[train_idx]

        model = CalibratedEnsemble()
        model.fit(X_tr, y_tr, w_tr)

        p_te = model.predict_proba(X_te)
        auc = auc_score(y_te, p_te)
        aucs.append(auc)

        # Simple returns proxy
        ret = np.where(p_te > 0.55, y_te * 3.2 - (1 - y_te), 0)
        returns.append(ret.mean())

    auc_oos = float(np.mean(aucs))
    sharpe = float(np.mean(returns) / (np.std(returns) + 1e-12))
    pbo = pbo_cscv(np.array(returns))
    dsr = deflated_sharpe(sharpe, n_trials=20, n_obs=len(y))

    print(f"AUC OOS: {auc_oos:.3f}")
    print(f"Sharpe: {sharpe:.3f}")
    print(f"PBO: {pbo:.3f}")
    print(f"Deflated Sharpe: {dsr:.3f}")

    # بوابات الرفض
    if auc_oos < config.AUC_MIN:
        print("REFUSED: AUC below threshold")
        sys.exit(2)

    if pbo > config.PBO_LIMIT:
        print("REFUSED: PBO too high")
        sys.exit(2)

    if dsr < config.DEFLATED_SHARPE_LIMIT:
        print("REFUSED: Deflated Sharpe below threshold")
        sys.exit(2)

    # تدريب نهائي وحفظ
    final_model = CalibratedEnsemble()
    final_model.fit(X, y, w)

    metrics = {
        "auc_oos": auc_oos,
        "sharpe": sharpe,
        "pbo": pbo,
        "deflated_sharpe": dsr,
    }

    save_model_registry(final_model, "champion", ["f1", "f2", "f3"], metrics)
    print("MODEL_SAVED")
    sys.exit(0)


if __name__ == "__main__":
    run()
