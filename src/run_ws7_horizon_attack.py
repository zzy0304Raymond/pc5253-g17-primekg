"""Two zero-parameter tests requested by the third independent review (D, 22 Nov).

1. Attack: size-biased mean field. A protein x carries k_D(x) k_Y(x) of the
   graph's drug--protein--disease routes, so a route lands on x with probability
   proportional to that product (a second-order friendship paradox). If the
   attack removes the set H, a route is cut with probability
       h = sum_{x in H} k_D k_Y / sum_x k_D k_Y,
   computed from the whole graph, not from the queries. A query whose endpoints
   survive keeps a route with probability 1 - sum_m P(m) h^m.

2. Horizon: limited-path percolation. For a pair at distance l0 = 2 and hop
   limit L = a l0, Lopez et al. (PRL 99, 188701) give the threshold
   p_c(a) = (kappa0 - 1)^((1 - a)/a), kappa0 = <k^2>/<k>. It is where the expected
   number of surviving paths of length L, (kappa0 - 1)^(L-2) p^L, falls to one.
   We compare it with the damage at which R_L / R_inf = 1/2, and we count the
   actual numbers of two- and three-hop paths per query (n2, n3) to explain where
   it fails. The independent-path estimate 1 - (1-p^2)^n2 (1-p^3)^n3 is also given.

Run from the repository root: python -m src.run_ws7_horizon_attack
"""
import json

import numpy as np
import pandas as pd
from scipy import sparse

from .common import ROOT, load_edges, load_nodes, load_order, n_removed
from .run_ws6_indications import Graph

OUT = ROOT / "results" / "ws7"
SAMPLE, FULL = "primekg_5000_bfs_v1", "primekg_full_v1"


def layer_degrees(g):
    drug, disease, ppi = g.layers(np.ones(len(g.uv), bool))
    return (np.asarray(drug.sum(0)).ravel(), np.asarray(disease.sum(0)).ravel(),
            np.asarray(ppi.sum(1)).ravel(), drug, disease, ppi)


def mean_field_attack(g, queries, rankings, fracs):
    """queries: array (drug, disease); m and the measured route survival come from the graph itself."""
    kD, kY, _, drug, disease, _ = layer_degrees(g)
    weight = kD * kY
    shared = drug[queries[:, 0]].multiply(disease[queries[:, 1]]).tocsr()
    m = np.diff(shared.indptr)
    keep = m > 0
    rows = []
    for name, ranking in rankings.items():
        for f in fracs:
            removed = np.zeros(g.n, bool)
            removed[ranking[:n_removed(f, g.n)]] = True
            h = weight[removed].sum() / weight.sum()
            ends = keep & ~removed[queries[:, 0]] & ~removed[queries[:, 1]]
            survived = np.array([np.any(~removed[shared.indices[shared.indptr[i]:shared.indptr[i + 1]]])
                                 for i in np.flatnonzero(ends)])
            route_share = removed[shared[ends].indices].mean()
            rows.append(dict(attack=name, frac_removed=f, queries=int(keep.sum()), endpoints_alive=int(ends.sum()),
                             h_predicted=h, h_measured=route_share,
                             route_survival_measured=survived.mean(),
                             route_survival_mean_field=1 - np.mean(h ** m[ends])))
    return pd.DataFrame(rows)


def path_counts(g, queries):
    _, _, _, drug, disease, ppi = layer_degrees(g)
    dq, yq = drug[queries[:, 0]], disease[queries[:, 1]]
    n2 = np.asarray(dq.multiply(yq).sum(1)).ravel()
    n3 = np.asarray((dq @ ppi).multiply(yq).sum(1)).ravel()
    return n2, n3


def kappa(g):
    return float((g.degree.astype(float) ** 2).sum() / g.degree.sum())


def crossing(f, ratio):
    """First damage fraction at which ratio falls below 1/2 (linear interpolation)."""
    i = np.flatnonzero(ratio < .5)
    if len(i) == 0 or i[0] == 0:
        return np.nan
    j = i[0]
    return f[j - 1] + (ratio[j - 1] - .5) * (f[j] - f[j - 1]) / (ratio[j - 1] - ratio[j])


def scan_full(g, queries, grid, seeds=range(5)):
    rows = []
    E = len(g.uv)
    for f in grid:
        for s in seeds:
            alive = np.ones(E, bool)
            alive[load_order(FULL, f"edge_random_s{s}")[:n_removed(f, E)]] = False
            r = g.retrieval(queries, alive)
            rows.append(dict(frac_removed=f, seed=s, **{k: float(r[k].mean()) for k in ("R2", "R3", "R4", "Rinf")}))
    return pd.DataFrame(rows).groupby("frac_removed").mean(numeric_only=True).drop(columns="seed").reset_index()


def horizon(g_sample, g_full, sample_q, full_q):
    rows = []
    hop = pd.read_csv(ROOT / "results" / "ws4" / f"{SAMPLE}__hop_fresh_orders.csv")
    hop = pd.concat([pd.DataFrame([dict(frac_removed=0.0, R_L3_mean=1.0, R_L4_mean=1.0, R_Linf_mean=1.0)]), hop])
    grid = np.round(np.arange(0, .951, .05), 2)
    full = scan_full(g_full, full_q, grid)
    full.to_csv(OUT / "full_indications_m1_hop_scan.csv", index=False, lineterminator="\n")
    for name, g, q, f, rl in (("BFS sample, benchmark", g_sample, sample_q, hop.frac_removed.to_numpy(),
                               {L: (hop[f"R_L{L}_mean"] / hop.R_Linf_mean).to_numpy() for L in (3, 4)}),
                              ("Full graph, indications with m >= 1", g_full, full_q, full.frac_removed.to_numpy(),
                               {L: (full[f"R{L}"] / full.Rinf).to_numpy() for L in (3, 4)})):
        k0 = kappa(g)
        n2, n3 = path_counts(g, q)
        for L in (3, 4):
            a = L / 2
            rows.append(dict(graph=name, L=L, kappa0=k0, f_predicted=1 - (k0 - 1) ** ((1 - a) / a),
                             f_measured=crossing(f, rl[L]), median_n2=float(np.median(n2)),
                             median_n3=float(np.median(n3)), median_n3_over_n2=float(np.median(n3 / n2))))
    return pd.DataFrame(rows), full


def independent_paths(g, q, full_scan=None, sample=False, fracs=(.3, .5, .7, .85)):
    n2, n3 = path_counts(g, q)
    rows = []
    if sample:
        hop = pd.read_csv(ROOT / "results" / "ws4" / f"{SAMPLE}__hop_fresh_orders.csv").set_index("frac_removed")
    for f in fracs:
        p = 1 - f
        est = float(np.mean(1 - (1 - p * p) ** n2 * (1 - p ** 3) ** n3))
        meas = float(hop.loc[f, "R_L3_mean"]) if sample else float(full_scan.set_index("frac_removed").loc[f, "R3"])
        rows.append(dict(graph="sample" if sample else "full", frac_removed=f, R3_independent_paths=est, R3_measured=meas))
    return pd.DataFrame(rows)


def equal_node_damage(frac=.05, seeds=range(10)):
    """Full graph, 5% of nodes removed at random or by degree: S and two-hop retrieval of indications."""
    g = Graph(load_nodes(FULL), load_edges(FULL))
    bench = pd.read_csv(ROOT / "results" / "ws6" / "indication_benchmark.csv")
    pos = bench[bench.label == 1][["drug", "disease"]].to_numpy()
    neg = bench[bench.label == 0][["drug", "disease"]].to_numpy()
    rows = []
    states = [("node_random", s, load_order(FULL, f"node_random_s{s}")) for s in seeds]
    states.append(("node_degree", None, np.lexsort((np.arange(g.n), -g.degree))))
    for name, seed, order in states:
        node_alive = np.ones(g.n, bool)
        node_alive[order[:n_removed(frac, g.n)]] = False
        alive = node_alive[g.uv[:, 0]] & node_alive[g.uv[:, 1]]
        rp = g.retrieval(pos, alive, node_alive, max_hops=2)
        rn = g.retrieval(neg, alive, node_alive, max_hops=2)
        rows.append(dict(strategy=name, seed=seed, frac_removed=frac, S=g.giant(alive),
                         R2_pos=float(rp["R2"].mean()), R2_neg=float(rn["R2"].mean())))
    return pd.DataFrame(rows)


def two_hop_many_orders(n_orders=500, seed=20261123):
    """Two-hop retrieval of indications with m >= 1 over many fresh random edge orders (full graph).

    Each route d-x-y is a pair of edge ids; a query survives if both edges of some route survive.
    """
    nodes, edges = load_nodes(FULL), load_edges(FULL)
    g = Graph(nodes, edges)
    bench = pd.read_csv(ROOT / "results" / "ws6" / "indication_benchmark.csv")
    pos = bench[bench.label == 1][["drug", "disease"]].to_numpy()
    n2, _ = path_counts(g, pos)
    q = pos[n2 > 0]
    eid = {}
    for i, (u, v) in enumerate(g.uv):
        eid[(u, v)] = i
        eid[(v, u)] = i
    nbr = {}
    for (u, v), i in eid.items():
        nbr.setdefault(u, {})[v] = i
    first, second, owner = [], [], []
    for k, (d, y) in enumerate(q):
        for x, e1 in nbr[d].items():
            e2 = nbr.get(x, {}).get(y)
            if e2 is not None and g.types[x] == "gene/protein":
                first.append(e1); second.append(e2); owner.append(k)
    first, second, owner = map(np.array, (first, second, owner))
    rng = np.random.default_rng(seed)
    grid = np.round(np.arange(0, 1.0001, .05), 2)
    E = len(g.uv)
    out = np.zeros((n_orders, len(grid)))
    for o in range(n_orders):
        rank = np.empty(E, np.int64)
        rank[rng.permutation(E)] = np.arange(E)
        for j, f in enumerate(grid):
            cut = n_removed(f, E)
            ok = (rank[first] >= cut) & (rank[second] >= cut)
            out[o, j] = np.bincount(owner[ok], minlength=len(q)).astype(bool).mean()
    return pd.DataFrame(dict(frac_removed=grid, R2_mean=out.mean(0), R2_se=out.std(0, ddof=1) / np.sqrt(n_orders),
                             R2_sd=out.std(0, ddof=1), n_orders=n_orders))


def information_theory(fracs=np.round(np.arange(0, .9001, .05), 2)):
    """Predicted recall, decoy rate and information under random edge removal.

    L = 2 uses Eq. (6), exact in expectation for each set. L = 3 uses the
    independent-path estimate 1 - (1-p^2)^n2 (1-p^3)^n3 with each pair's actual path counts.
    """
    from .run_ws6_indications import information
    g = Graph(load_nodes(FULL), load_edges(FULL))
    bench = pd.read_csv(ROOT / "results" / "ws6" / "indication_benchmark.csv")
    sets = {k: bench[bench.label == v][["drug", "disease"]].to_numpy() for k, v in (("pos", 1), ("neg", 0))}
    counts = {k: path_counts(g, q) for k, q in sets.items()}
    rows = []
    for f in fracs:
        p = 1 - f
        row = dict(frac_removed=f)
        for k, (n2, n3) in counts.items():
            row[f"R2_{k}"] = float(np.mean(1 - (1 - p * p) ** n2))
            row[f"R3_{k}"] = float(np.mean(1 - (1 - p * p) ** n2 * (1 - p ** 3) ** n3))
        for L in ("R2", "R3"):
            row[f"{L}_info_bits"] = float(information(row[f"{L}_pos"], row[f"{L}_neg"]))
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    gs = Graph(load_nodes(SAMPLE), load_edges(SAMPLE))
    gf = Graph(load_nodes(FULL), load_edges(FULL))
    q = json.loads((ROOT / "data" / "processed" / SAMPLE / "queries.json").read_text())
    sample_q = np.array([[x["drug_nid"], x["disease_nid"]] for x in q])
    bench = pd.read_csv(ROOT / "results" / "ws6" / "indication_benchmark.csv")
    ind = bench[bench.label == 1][["drug", "disease"]].to_numpy()
    n2, _ = path_counts(gf, ind)
    full_q = ind[n2 > 0]

    rankings = {"degree": load_order(SAMPLE, "node_degree"), "betweenness": load_order(SAMPLE, "node_betweenness")}
    mf = mean_field_attack(gs, sample_q, rankings, (.01, .02, .05, .10))
    mf.insert(0, "graph", "sample")
    full_rank = {"degree": np.lexsort((np.arange(gf.n), -gf.degree))}
    mf_full = mean_field_attack(gf, full_q, full_rank, (.005, .01, .02, .05, .10))
    mf_full.insert(0, "graph", "full_indications")
    mf = pd.concat([mf, mf_full])
    mf.to_csv(OUT / "attack_mean_field.csv", index=False, lineterminator="\n")
    print(mf.round(3).to_string())

    hz, full_scan = horizon(gs, gf, sample_q, full_q)
    hz.to_csv(OUT / "limited_path_percolation.csv", index=False, lineterminator="\n")
    print(hz.round(3).to_string())
    ip = pd.concat([independent_paths(gs, sample_q, sample=True), independent_paths(gf, full_q, full_scan)])
    ip.to_csv(OUT / "independent_path_estimate.csv", index=False, lineterminator="\n")
    print(ip.round(3).to_string())
    n2_all, _ = path_counts(gf, ind)
    pd.DataFrame(dict(m=np.rint(n2_all[n2_all > 0]).astype(int))).to_csv(
        OUT / "full_indications_m.csv", index=False, lineterminator="\n")
    neg = bench[bench.label == 0][["drug", "disease"]].to_numpy()
    n2_neg, _ = path_counts(gf, neg)
    decoys = scan_full(gf, neg[n2_neg > 0], np.round(np.arange(0, .951, .05), 2))
    decoys.to_csv(OUT / "full_decoys_m1_hop_scan.csv", index=False, lineterminator="\n")
    f = decoys.frac_removed.to_numpy()
    print("decoy crossings", [round(crossing(f, (decoys[f"R{L}"] / decoys.Rinf).to_numpy()), 3) for L in (3, 4)])
    equal_node_damage().to_csv(OUT / "full_equal_node_damage.csv", index=False, lineterminator="\n")
    two_hop_many_orders().to_csv(OUT / "full_indications_m1_two_hop_500_orders.csv", index=False, lineterminator="\n")
    information_theory().to_csv(OUT / "information_theory.csv", index=False, lineterminator="\n")
