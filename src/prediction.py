"""Per-query prediction of retrieval failure (WS4, task card D5).

The theory baseline has no fitted parameter. Logistic regression uses the five
features named in the work plan. Random removal follows the agreed split, train
seeds 0-6 and test seeds 7-9. A targeted attack has one deterministic outcome
per query, so it uses repeated cross-validation over queries instead.
"""
import warnings

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .common import ROOT, graph_dir, load_edges, load_nodes, load_queries, n_removed

PREDICTION_LEVELS = (.3, .5)
TRAIN_SEEDS = range(7)
TEST_SEEDS = range(7, 10)
ATTACK_LEVELS = (.05, .10)


def query_features(gid, queries):
    """Log m, intermediate degree mean and minimum, drug and disease degree."""
    degree = pd.read_csv(graph_dir(gid) / "node_features.csv").degree.to_numpy(float)
    rows = []
    for q in queries:
        inter = degree[q["intermediates"]]
        rows.append((q["redundancy_m"], inter.mean(), inter.min(),
                     degree[q["drug_nid"]], degree[q["disease_nid"]]))
    return np.log(np.array(rows))


def _model():
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))


def _outcome(gid, strategy, seed, frac):
    path = ROOT / "results" / "ws3" / f"{gid}__perquery__{strategy}__s{seed}.csv"
    frame = pd.read_csv(path)
    frame = frame[frame.frac_removed == frac].sort_values("query_id")
    return (frame.s_alive.to_numpy() > 0).astype(int)


def _ceiling(probability, n_draws=2000, seed=0):
    """Expected AUC if outcomes really are independent draws from probability."""
    rng = np.random.default_rng(seed)
    scores = []
    for _ in range(n_draws):
        outcome = (rng.random(len(probability)) < probability).astype(int)
        if 0 < outcome.sum() < len(outcome):
            scores.append(roc_auc_score(outcome, probability))
    return float(np.mean(scores))


def random_failure(gid):
    """Return the template table and a detail table for random edge removal."""
    queries = load_queries(gid)
    features = query_features(gid, queries)
    m = np.array([q["redundancy_m"] for q in queries])
    total = len(load_edges(gid))
    table, detail = [], []
    for frac in PREDICTION_LEVELS:
        keep = 1 - n_removed(frac, total) / total
        theory = 1 - (1 - keep * keep) ** m
        train_y = np.concatenate([_outcome(gid, "edge_random", s, frac) for s in TRAIN_SEEDS])
        test_y = np.concatenate([_outcome(gid, "edge_random", s, frac) for s in TEST_SEEDS])
        train_x = np.tile(features, (len(TRAIN_SEEDS), 1))
        test_x = np.tile(features, (len(TEST_SEEDS), 1))
        fitted = _model().fit(train_x, train_y)
        logistic = fitted.predict_proba(test_x)[:, 1]
        theory_test = np.tile(theory, len(TEST_SEEDS))
        for name, score in (("theory", theory_test), ("logistic", logistic)):
            table.append((name, frac, "AUC", roc_auc_score(test_y, score)))
            table.append((name, frac, "Brier", brier_score_loss(test_y, score)))
        detail.append(dict(strategy="edge_random", damage_frac=frac, evaluation="test seeds 7-9",
                           n_rows=len(test_y), base_rate=float(test_y.mean()),
                           brier_base_rate=float(test_y.mean() * (1 - test_y.mean())),
                           auc_ceiling_if_formula_true=_ceiling(theory),
                           theory_auc=table[-4][3], theory_brier=table[-3][3],
                           logistic_auc=table[-2][3], logistic_brier=table[-1][3]))
    return pd.DataFrame(table, columns=["model", "damage_frac", "metric", "value"]), detail


def targeted_attack(gid):
    """Query-level cross-validation on the deterministic attack outcomes."""
    queries = load_queries(gid)
    features = query_features(gid, queries)
    m = np.array([q["redundancy_m"] for q in queries])
    total = len(load_nodes(gid))
    detail = []
    splitter = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=42)
    for strategy in ("node_degree", "node_betweenness"):
        for frac in ATTACK_LEVELS:
            outcome = _outcome(gid, strategy, -1, frac)
            phi = 1 - n_removed(frac, total) / total
            theory = phi * phi * (1 - (1 - phi) ** m)
            scores = []
            for train, test in splitter.split(features, outcome):
                predicted = _model().fit(features[train], outcome[train]).predict_proba(features[test])[:, 1]
                scores.append((roc_auc_score(outcome[test], theory[test]),
                               brier_score_loss(outcome[test], theory[test]),
                               roc_auc_score(outcome[test], predicted),
                               brier_score_loss(outcome[test], predicted)))
            mean = np.mean(scores, axis=0)
            detail.append(dict(strategy=strategy, damage_frac=frac, evaluation="5-fold CV x 20 over queries",
                               n_rows=len(outcome), base_rate=float(outcome.mean()),
                               brier_base_rate=float(outcome.mean() * (1 - outcome.mean())),
                               auc_ceiling_if_formula_true=np.nan,
                               theory_auc=mean[0], theory_brier=mean[1],
                               logistic_auc=mean[2], logistic_brier=mean[3]))
    return detail


def run(gid):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        table, detail = random_failure(gid)
        detail += targeted_attack(gid)
    return table, pd.DataFrame(detail)
