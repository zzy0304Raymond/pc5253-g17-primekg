"""Final-report checks requested by the independent review (D, 22 Nov).

1. Degree attack on the filtered full graph against the Callaway prediction,
   to separate BFS-sampling effects from properties of PrimeKG.
2. Mixing diagnostics for one realisation of each null model.
3. Long-run two-hop success by query group (5,000 fresh orders).
4. Prediction bias of the restoration formula in standard-error units.
5. Paired t-tests between repair policies.
6. Eq. (6) evaluated on all drug-disease pairs of each graph.

Run from the repository root: python -m src.run_ws4_v2
"""
import networkx as nx
import numpy as np
import pandas as pd

from . import run_null_model as N
from . import theory
from .common import EDGE_LEVELS, ROOT, load_edges, load_nodes, load_order, load_queries, n_removed
from .percolation import nz_nodes

OUT = ROOT / "results" / "ws4"
GRID = np.round(np.arange(0, .7001, .05), 2)


def full_graph_attack(gid="primekg_full_v1"):
    edges = load_edges(gid)
    n = len(load_nodes(gid))
    uv = edges[["u", "v"]].to_numpy(dtype=np.int64)
    degree = np.bincount(uv.ravel(), minlength=n)
    ranking = np.lexsort((np.arange(n), -degree))
    out = nz_nodes(n, uv, ranking)
    rows = []
    for f in GRID:
        t = n_removed(f, n)
        rows.append(dict(gid=gid, frac_removed=f, sim=out["gcc_size"][t] / n,
                         theory=theory.gcc_degree_attack(degree, t / n), isolated_frac=out["n_isolated"][t] / n))
    return pd.DataFrame(rows)


def mixing(gid="primekg_5000_bfs_v1"):
    nodes, edges = load_nodes(gid), load_edges(gid)
    n = len(nodes)
    types = nodes.node_type.to_numpy()
    relation = edges.relation.to_numpy()
    base = edges[["u", "v"]].to_numpy(dtype=np.int64)
    degree = np.bincount(base.ravel(), minlength=n)
    original = set(map(tuple, np.sort(base, axis=1).tolist()))
    hubs = np.argsort(-degree)[: n // 100]

    def stats(model, uv):
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(uv.tolist())
        kept = len(original & set(map(tuple, np.sort(uv, axis=1).tolist()))) / len(uv)
        hub_kept = np.mean([len(set(g[h]) & set(base_adj[h])) / degree[h] for h in hubs])
        return dict(model=model, edges_unchanged=kept, hub_neighbours_unchanged=hub_kept,
                    transitivity=nx.transitivity(g), assortativity=N.assortativity(uv, degree))

    base_adj = {h: set() for h in hubs}
    for a, b in base.tolist():
        if a in base_adj:
            base_adj[a].add(b)
        if b in base_adj:
            base_adj[b].add(a)
    rows = [stats("real", base)]
    for model in N.MODELS[1:]:
        rng = np.random.default_rng(20261122 + 1000 * N.MODELS.index(model))  # realisation 0 of run_null_model
        uv = base.copy()
        if model == "rewire_full":
            N.rewire_full(uv, relation, degree, rng)
        elif model == "rewire_2k":
            N.rewire_2k(uv, relation, degree, rng)
        else:
            N.rewire_typed(uv, relation, degree, types)(rng)
        rows.append(stats(model, uv))
        print(rows[-1], flush=True)
    return pd.DataFrame(rows)


def group_long_run(gid="primekg_5000_bfs_v1", n_orders=5000, seed=20261122):
    edges = load_edges(gid)
    queries = load_queries(gid)
    lookup = {(row.u, row.v): row.eid for row in edges.itertuples()}
    paths = []
    for i, q in enumerate(queries):
        for x in q["intermediates"]:
            a, b = (lookup[(min(e, x), max(e, x))] for e in (q["drug_nid"], q["disease_nid"]))
            paths.append((i, a, b))
    paths = np.array(paths)
    group = np.array([q["group"] for q in queries])
    m = np.array([q["redundancy_m"] for q in queries])
    total = len(edges)
    rng = np.random.default_rng(seed)
    levels = [f for f in EDGE_LEVELS if f > 0]
    samples = {g: np.zeros((n_orders, len(levels))) for g in ("single", "multi", "all")}
    for t in range(n_orders):
        rank = rng.permutation(total)
        for j, f in enumerate(levels):
            cut = n_removed(f, total)
            ok = np.zeros(len(queries), dtype=bool)
            np.logical_or.at(ok, paths[:, 0], np.minimum(rank[paths[:, 1]], rank[paths[:, 2]]) >= cut)
            for g in ("single", "multi"):
                samples[g][t, j] = ok[group == g].mean()
            samples["all"][t, j] = ok.mean()
    rows = []
    for g, s in samples.items():
        mm = m if g == "all" else m[group == g]
        for j, f in enumerate(levels):
            p = 1 - n_removed(f, total) / total
            rows.append(dict(group=g, frac_removed=f, mean=s[:, j].mean(), sd_one_state=s[:, j].std(ddof=1),
                             se=s[:, j].std(ddof=1) / np.sqrt(n_orders), formula=theory.R_edge(p, mm)))
    return pd.DataFrame(rows)


def restoration_bias(gid="primekg_5000_bfs_v1"):
    data = pd.read_csv(OUT / f"{gid}__restoration_prediction.csv")
    data["measured_se_pp"] = data.measured_sd_pp / np.sqrt(10)
    data["bias_pp"] = data.predicted_gain_pp - data.measured_gain_pp
    data["bias_in_se"] = data.bias_pp / data.measured_se_pp
    return data


def paired_tests(gid="primekg_5000_bfs_v1"):
    """Paired comparison of repair policies over the ten damage seeds (L = 2 and L = 3)."""
    from scipy import stats
    data = pd.read_csv(ROOT / "results" / "ws5" / "final" / gid / f"{gid}__paired_gains.csv")
    rows = []
    for metric in ("R_L2", "R_L3"):
        for f in (.3, .5):
            for b in (.05, .2):
                part = data[(data.metric == metric) & np.isclose(data.damage_frac, f) & np.isclose(data.budget_frac, b)]
                wide = part.pivot(index="seed", columns="strategy", values="gain")
                for a, c in (("restore_relation_type", "restore_edge_betweenness"),
                             ("restore_task_aware", "restore_edge_betweenness"),
                             ("restore_task_aware", "restore_relation_type")):
                    diff = 100 * (wide[a] - wide[c])
                    t = stats.ttest_rel(wide[a], wide[c])
                    rows.append(dict(metric=metric, damage_frac=f, budget_frac=b, policy_a=a, policy_b=c,
                                     mean_diff_pp=diff.mean(), sd_diff_pp=diff.std(ddof=1),
                                     t=t.statistic, p_value=t.pvalue, a_wins_seeds=int((diff > 0).sum())))
    return pd.DataFrame(rows)

def all_pairs():
    """Eq. (6) for every drug-disease pair with a shared protein (no simulation needed)."""
    from scipy import sparse
    rows = []
    for gid in ("primekg_2000_bfs_v1", "primekg_5000_bfs_v1", "primekg_full_v1"):
        nodes, edges = load_nodes(gid), load_edges(gid)
        n = len(nodes)
        types = nodes.node_type.to_numpy()

        def bipartite(relation, entity):
            part = edges[edges.relation == relation]
            a, b = part.u.to_numpy(), part.v.to_numpy()
            left = types[a] == entity
            return sparse.csr_matrix((np.ones(len(a)), (np.where(left, a, b), np.where(left, b, a))), shape=(n, n))

        m = (bipartite("drug_protein", "drug") @ bipartite("disease_protein", "disease").T).tocoo().data.astype(int)
        degree = np.bincount(edges[["u", "v"]].to_numpy().ravel(), minlength=n)
        rows.append(dict(gid=gid, pairs=len(m), share_m1=float(np.mean(m == 1)), median_m=float(np.median(m)),
                         R2_f03=theory.R_edge(0.7, m), R2_f05=theory.R_edge(0.5, m),
                         assortativity=N.assortativity(edges[["u", "v"]].to_numpy(), degree)))
    return pd.DataFrame(rows)



if __name__ == "__main__":
    full = full_graph_attack()
    full.to_csv(OUT / "primekg_full_v1__degree_attack_theory.csv", index=False, lineterminator="\n")
    print(full.round(4).to_string())
    groups = group_long_run()
    groups.to_csv(OUT / "primekg_5000_bfs_v1__R2_long_run_by_group.csv", index=False, lineterminator="\n")
    print(groups[groups.frac_removed.isin([.3, .5, .7])].round(4).to_string())
    bias = restoration_bias()
    bias.to_csv(OUT / "primekg_5000_bfs_v1__restoration_prediction_bias.csv", index=False, lineterminator="\n")
    print(bias.round(2).to_string())
    mix = mixing()
    mix.to_csv(OUT / "primekg_5000_bfs_v1__null_model_mixing.csv", index=False, lineterminator="\n")
    print(mix.round(4).to_string())
    tests = paired_tests()
    tests.to_csv(OUT / "primekg_5000_bfs_v1__restoration_paired_tests.csv", index=False, lineterminator="\n")
    print(tests.round(3).to_string())
    pairs = all_pairs()
    pairs.to_csv(OUT / "all_pairs_two_hop.csv", index=False, lineterminator="\n")
    print(pairs.round(4).to_string())
