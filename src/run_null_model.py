"""Degree-attack null models: why the real graph is more fragile than GF theory.

The Callaway et al. (2000) curve assumes an uncorrelated configuration model with
the empirical degree sequence. Three rewirings keep that sequence and remove
different parts of the remaining structure:

* ``rewire_full``  - Maslov-Sneppen double-edge swaps that ignore relation type
                     (1K null model: degrees only).
* ``rewire_typed`` - swaps only between edges of the same relation, keeping every
                     node's degree in every relation (typed 1K null model).
* ``rewire_2k``    - swaps only between edge ends whose endpoints have equal
                     degree, which keeps the joint degree distribution and hence
                     the degree assortativity (2K null model).

All graphs share the degree sequence, so B's fixed degree ranking applies to each.
Run from the repository root: python -m src.run_null_model primekg_5000_bfs_v1
"""
import argparse
import platform

import numpy as np
import pandas as pd

from .common import RESULT_COLUMNS, ROOT, load_edges, load_nodes, load_order, n_removed, sha256, graph_dir, write_json
from .percolation import nz_nodes
from . import theory

SWAPS_PER_EDGE = 10
REALISATIONS = 5
GRID = np.round(np.arange(0, 1.0001, .05), 2)
MODELS = ("real", "rewire_2k", "rewire_typed", "rewire_full")


def _key(a, b):
    return (a, b) if a < b else (b, a)


def _swap_loop(uv, pick, rng, n_attempts):
    """Generic double-edge swap. pick() returns (e1, s1, e2, s2) or None.

    Ends uv[e1, s1] and uv[e2, s2] are exchanged when the result keeps the graph
    simple. Returns the number of accepted swaps.
    """
    present = set(map(tuple, np.sort(uv, axis=1).tolist()))
    accepted = 0
    for _ in range(n_attempts):
        chosen = pick(rng)
        if chosen is None:
            continue
        e1, s1, e2, s2 = chosen
        if e1 == e2:
            continue
        a, b = uv[e1, 1 - s1], uv[e1, s1]
        c, d = uv[e2, 1 - s2], uv[e2, s2]
        if a == d or c == b or b == d:
            continue
        new1, new2 = _key(a, d), _key(c, b)
        if new1 in present or new2 in present or new1 == new2:
            continue
        present.discard(_key(a, b))
        present.discard(_key(c, d))
        present.add(new1)
        present.add(new2)
        uv[e1, s1], uv[e2, s2] = d, b
        accepted += 1
    return accepted


def rewire_full(uv, relation, degree, rng):
    m = len(uv)

    def pick(r):
        e1, e2 = r.integers(m, size=2)
        return int(e1), int(r.integers(2)), int(e2), int(r.integers(2))
    return _swap_loop(uv, pick, rng, SWAPS_PER_EDGE * m)


def rewire_typed(uv, relation, degree, types):
    """Exchange the protein ends of two edges of the same relation.

    For protein_protein either end may be exchanged; for drug_protein and
    disease_protein the protein end is always exchanged, so drugs keep only
    drug_protein edges and diseases only disease_protein edges.
    """
    def run(rng):
        total = 0
        for rel in np.unique(relation):
            ids = np.flatnonzero(relation == rel)
            if rel == "protein_protein":
                def pick(r, ids=ids):
                    e1, e2 = ids[r.integers(len(ids), size=2)]
                    return int(e1), int(r.integers(2)), int(e2), int(r.integers(2))
            else:
                protein_side = (types[uv[ids, 1]] == "gene/protein").astype(int)

                def pick(r, ids=ids, side=protein_side):
                    i, j = r.integers(len(ids), size=2)
                    return int(ids[i]), int(side[i]), int(ids[j]), int(side[j])
            total += _swap_loop(uv, pick, rng, SWAPS_PER_EDGE * len(ids))
        return total
    return run


def rewire_2k(uv, relation, degree, rng):
    """Exchange two edge ends whose endpoints have the same degree."""
    m = len(uv)
    stub_degree = degree[uv.ravel()]
    order = np.argsort(stub_degree, kind="stable")
    sorted_degree = stub_degree[order]
    starts = np.searchsorted(sorted_degree, sorted_degree, side="left")
    ends = np.searchsorted(sorted_degree, sorted_degree, side="right")
    position = np.empty(2 * m, dtype=np.int64)
    position[order] = np.arange(2 * m)

    def pick(r):
        stub = int(r.integers(2 * m))
        p = position[stub]
        lo, hi = starts[p], ends[p]
        if hi - lo < 2:
            return None
        other = int(order[r.integers(lo, hi)])
        return stub // 2, stub % 2, other // 2, other % 2
    return _swap_loop(uv, pick, rng, SWAPS_PER_EDGE * m)


def assortativity(uv, degree):
    """Pearson correlation of endpoint degrees over both edge orientations."""
    x = np.concatenate([degree[uv[:, 0]], degree[uv[:, 1]]]).astype(float)
    y = np.concatenate([degree[uv[:, 1]], degree[uv[:, 0]]]).astype(float)
    return float(np.corrcoef(x, y)[0, 1])


def low_degree_neighbour_mean(uv, degree, k_max=3):
    """Mean degree of the neighbours of nodes with degree <= k_max."""
    a = np.concatenate([uv[:, 0], uv[:, 1]])
    b = np.concatenate([uv[:, 1], uv[:, 0]])
    mask = degree[a] <= k_max
    return float(degree[b[mask]].mean())


def attack_rows(gid, model, realisation, n, uv, ranking, drugs):
    out = nz_nodes(n, uv, ranking)
    rows = []
    adjacency_drug = {}
    for frac in GRID:
        t = n_removed(frac, n)
        rows.append([gid, model, realisation, float(frac), t, "gcc_frac", out["gcc_size"][t] / n])
        rows.append([gid, model, realisation, float(frac), t, "isolated_frac", out["n_isolated"][t] / n])
    # Fraction of drugs left without any surviving neighbour after a 5% attack.
    t = n_removed(.05, n)
    removed = np.zeros(n, dtype=bool)
    removed[ranking[:t]] = True
    keep = ~removed[uv[:, 0]] & ~removed[uv[:, 1]]
    has_edge = np.zeros(n, dtype=bool)
    has_edge[uv[keep].ravel()] = True
    alive_drugs = drugs[~removed[drugs]]
    rows.append([gid, model, realisation, .05, t, "drug_isolated_frac", float(np.mean(~has_edge[alive_drugs]))])
    return rows


def run(gid):
    nodes, edges = load_nodes(gid), load_edges(gid)
    n = len(nodes)
    types = nodes.node_type.to_numpy()
    relation = edges.relation.to_numpy()
    base = edges[["u", "v"]].to_numpy(dtype=np.int64)
    degree = np.bincount(base.ravel(), minlength=n)
    ranking = load_order(gid, "node_degree")
    drugs = np.flatnonzero(types == "drug")
    rows, stats = [], []
    rows += attack_rows(gid, "real", -1, n, base, ranking, drugs)
    stats.append(dict(model="real", realisation=-1, accepted_swaps=0, assortativity=assortativity(base, degree),
                      knn_low_degree=low_degree_neighbour_mean(base, degree)))
    for model in MODELS[1:]:
        for r in range(REALISATIONS):
            rng = np.random.default_rng(20261122 + 1000 * MODELS.index(model) + r)
            uv = base.copy()
            if model == "rewire_full":
                accepted = rewire_full(uv, relation, degree, rng)
            elif model == "rewire_2k":
                accepted = rewire_2k(uv, relation, degree, rng)
            else:
                accepted = rewire_typed(uv, relation, degree, types)(rng)
            assert np.array_equal(np.bincount(uv.ravel(), minlength=n), degree)
            assert len(set(map(tuple, np.sort(uv, axis=1).tolist()))) == len(uv)
            rows += attack_rows(gid, model, r, n, uv, ranking, drugs)
            stats.append(dict(model=model, realisation=r, accepted_swaps=accepted,
                              assortativity=assortativity(uv, degree),
                              knn_low_degree=low_degree_neighbour_mean(uv, degree)))
            print(f"{model} r={r}: accepted {accepted}, assortativity {stats[-1]['assortativity']:.3f}", flush=True)
    for frac in GRID:
        rows.append([gid, "theory_attack", -1, float(frac), n_removed(frac, n), "gcc_frac",
                     theory.gcc_degree_attack(degree, n_removed(frac, n) / n)])
    data = pd.DataFrame(rows, columns=RESULT_COLUMNS)
    out = ROOT / "results" / "ws4"
    data.to_csv(out / f"{gid}__null_model_attack.csv", index=False, lineterminator="\n")
    stats = pd.DataFrame(stats)
    stats.to_csv(out / f"{gid}__null_model_stats.csv", index=False, lineterminator="\n")
    gcc = data[data.metric == "gcc_frac"].groupby(["strategy", "frac_removed"]).value.mean().unstack("strategy")
    gap = gcc.sub(gcc["theory_attack"], axis=0)
    summary = pd.DataFrame({
        "model": [m for m in MODELS],
        "assortativity_mean": [stats[stats.model == m].assortativity.mean() for m in MODELS],
        "knn_low_degree_mean": [stats[stats.model == m].knn_low_degree.mean() for m in MODELS],
        "S_at_f05": [gcc.loc[.05, m] for m in MODELS],
        "S_at_f30": [gcc.loc[.30, m] for m in MODELS],
        "S_at_f45": [gcc.loc[.45, m] for m in MODELS],
        "max_abs_gap_to_theory_f_le_0p5": [gap.loc[gap.index <= .5, m].abs().max() for m in MODELS],
        "max_abs_gap_to_real_f_le_0p5": [(gcc.loc[gcc.index <= .5, m] - gcc.loc[gcc.index <= .5, "real"]).abs().max()
                                         for m in MODELS],
        "drug_isolated_frac_at_f05": [data[(data.strategy == m) & (data.metric == "drug_isolated_frac")].value.mean()
                                      for m in MODELS],
    })
    summary.to_csv(out / f"{gid}__null_model_summary.csv", index=False, lineterminator="\n")
    write_json(out / f"{gid}__null_model_provenance.json", {
        "gid": gid, "python": platform.python_version(), "swaps_per_edge": SWAPS_PER_EDGE,
        "realisations": REALISATIONS, "manifest_sha256": sha256(graph_dir(gid) / "manifest.json"),
        "source_sha256": sha256(ROOT / "src" / "run_null_model.py"),
        "note": "Same degree sequence and the same fixed degree ranking (B's node_degree order) in every model."})
    print(summary.round(4).to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gids", nargs="*", default=["primekg_5000_bfs_v1"])
    for gid in parser.parse_args().gids:
        run(gid)
