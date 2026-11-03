"""E's edge restoration: static rankings, fixed damage masks, explicit budgets."""
import numpy as np

from .common import check_order, n_removed


def _ids(values, total=None):
    a = np.asarray(values)
    if a.ndim != 1 or not np.issubdtype(a.dtype, np.integer):
        raise ValueError("Edge IDs must be a one-dimensional integer array")
    if len(np.unique(a)) != len(a) or (a < 0).any():
        raise ValueError("Edge IDs must be unique and nonnegative")
    if total is not None and (a >= total).any():
        raise ValueError("Edge ID out of range")
    return a.astype(np.int64, copy=False)


def _mask(edge_alive):
    a = np.asarray(edge_alive)
    if a.ndim != 1 or a.dtype != np.bool_:
        raise ValueError("edge_alive must be a one-dimensional boolean mask")
    return a


def restore(edge_alive, ranked_removed_eids, budget_frac):
    """Return a copy, restoring a ranking prefix up to the requested budget.

    Budget = round(budget_frac * originally removed edges), capped at the
    candidate count. Candidate shortages leave budget unspent; callers record
    the actual restored count. No new edges or mutations of inputs are allowed.
    """
    mask = _mask(edge_alive)
    order = _ids(ranked_removed_eids, len(mask))
    if mask[order].any():
        raise ValueError("Ranking contains an edge that is already alive")
    count = n_removed(budget_frac, int((~mask).sum()))
    out = mask.copy()
    out[order[:count]] = True
    return out


def rank_random(removed_eids, seed):
    return np.random.default_rng(seed).permutation(_ids(removed_eids))


def rank_edge_betweenness(removed_eids, edge_order):
    """Filter B's original high-to-low full-edge ranking to removed edges."""
    order = check_order(edge_order, len(edge_order))
    removed = _ids(removed_eids, len(order))
    return order[np.isin(order, removed)].copy()


def rank_relation_type(removed_eids, edges, seed):
    removed = _ids(removed_eids, len(edges))
    eligible = edges.relation.to_numpy()[removed]
    return np.random.default_rng(seed).permutation(
        removed[np.isin(eligible, ["drug_protein", "disease_protein"])])


def training_path_eids(edges, train_queries):
    """Compile original two-hop paths, rejecting any non-training query."""
    if any(q.get("split") != "train" for q in train_queries):
        raise ValueError("Task-aware ranking accepts training queries only")
    index = {(int(u), int(v), r): int(eid) for eid, u, v, r in
             edges[["eid", "u", "v", "relation"]].itertuples(index=False, name=None)}
    paths = []
    for q in train_queries:
        pairs = []
        for protein in q["intermediates"]:
            drug = sorted((q["drug_nid"], protein))
            disease = sorted((q["disease_nid"], protein))
            pairs.append((index[(*drug, "drug_protein")], index[(*disease, "disease_protein")]))
        paths.append(np.asarray(pairs, dtype=np.int64).reshape(-1, 2))
    return paths


def task_aware_scores(edge_alive, paths):
    """Count completable paths in currently unsuccessful training queries.

    Successful queries and paths missing both edges contribute no score.
    Scores are computed once before any restoration; no use of test queries.
    """
    mask = _mask(edge_alive)
    scores = np.zeros(len(mask), dtype=np.int64)
    for pairs in paths:
        states = mask[pairs]
        if np.all(states, axis=1).any():
            continue
        completable = pairs[states.sum(axis=1) == 1]
        if len(completable):
            missing = completable[~mask[completable]]
            np.add.at(scores, missing, 1)
    return scores


def rank_task_aware(removed_eids, edge_alive, paths, seed):
    mask = _mask(edge_alive)
    removed = _ids(removed_eids, len(mask))
    if mask[removed].any():
        raise ValueError("Task-aware candidates must be removed edges")
    scores = task_aware_scores(mask, paths)
    shuffled = np.random.default_rng(seed).permutation(removed)
    return shuffled[np.argsort(-scores[shuffled], kind="stable")]
