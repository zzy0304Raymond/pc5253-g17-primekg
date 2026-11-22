"""Chance paths and hubs on the full graph (fourth review, D, 22 Nov).

1. Quenched-ball null for decoy rates. Keep the drug's real targets and their
   PPI ball B_{L-2}(d); give the disease k_y random protein links drawn in
   proportion to the disease-layer degree. A typed path of length <= L exists
   with probability 1 - (1 - w)^{k_y}, w = sum_{x in B} k_Y(x) / K_Y. No parameters.
2. Attack decomposition for the two-hop indications under a degree attack:
   lost endpoints versus lost routes, and the mean field with the graph-wide
   hub share h (Eq. mf) versus the indications' own route hub share.
3. Protein-only control: remove the highest-degree proteins only, so that no
   drug or disease is removed, and track recall, decoy rate, ratio and information.
4. Do path counts at L >= 3 carry information that existence does not? AUROC of
   degree-normalised n3 and n4 among pairs with no shared protein.
5. The two-hop likelihood ratio runs from P(m>=1|ind)/P(m>=1|dec) at f = 0 to
   E[m|ind]/E[m|dec] as f -> 1, because 1 - (1-p^2)^m ~ m p^2 for small p.

Run from the repository root: python -m src.run_ws8_chance_hubs
"""
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import rankdata

from .common import ROOT, load_edges, load_nodes, n_removed
from .run_ws6_indications import Graph, information

FULL = "primekg_full_v1"
OUT = ROOT / "results" / "ws8"


def auroc(pos, neg):
    """Mann-Whitney AUROC with ties counted as one half."""
    r = rankdata(np.r_[pos, neg])
    return (r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def setup():
    g = Graph(load_nodes(FULL), load_edges(FULL))
    bench = pd.read_csv(ROOT / "results" / "ws6" / "indication_benchmark.csv")
    sets = {name: bench[bench.label == v][["drug", "disease"]].to_numpy() for name, v in (("indication", 1), ("decoy", 0))}
    return g, sets


def ball_null(g, sets):
    drug, disease, ppi = g.layers(np.ones(len(g.uv), bool))
    kY = np.asarray(disease.sum(0)).ravel()
    step = (sparse.identity(g.n, format="csr") + ppi).tocsr()
    rows = []
    for name, q in sets.items():
        ky = np.asarray(disease[q[:, 1]].sum(1)).ravel()
        ball = drug[q[:, 0]].copy()
        ball.data[:] = 1
        row = dict(set=name)
        for L in (2, 3, 4):
            if L > 2:
                ball = (ball @ step).tocsr()
                ball.data[:] = 1
            w = np.asarray(ball @ kY).ravel() / kY.sum()
            row[f"R{L}_ball"] = float(np.mean(1 - (1 - w) ** ky))
        rows.append(row)
    return pd.DataFrame(rows)


def counts(g, q):
    drug, disease, ppi = g.layers(np.ones(len(g.uv), bool))
    dq, yq = drug[q[:, 0]], disease[q[:, 1]]
    dp = (dq @ ppi).tocsr()
    n2 = np.asarray(dq.multiply(yq).sum(1)).ravel()
    n3 = np.asarray(dp.multiply(yq).sum(1)).ravel()
    n4 = np.asarray(dp.multiply((yq @ ppi).tocsr()).sum(1)).ravel()
    kprod = np.asarray(dq.sum(1)).ravel() * np.asarray(yq.sum(1)).ravel()
    return dict(n2=n2, n3=n3, n4=n4, kprod=kprod)


def count_information(g, sets):
    c = {k: counts(g, q) for k, q in sets.items()}
    p, n = c["indication"], c["decoy"]
    rows = [dict(score="n2 (all pairs)", auroc=auroc(p["n2"], n["n2"]))]
    zp, zn = p["n2"] == 0, n["n2"] == 0
    for key in ("n3", "n4"):
        rows.append(dict(score=f"{key}/(k_d k_y), pairs with n2 = 0",
                         auroc=auroc(p[key][zp] / p["kprod"][zp], n[key][zn] / n["kprod"][zn])))
    for L, key in (("R3", "n3"), ("R4", "n4")):
        rows.append(dict(score=f"{L} existence, pairs with n2 = 0",
                         auroc=auroc((p[key][zp] > 0).astype(float), (n[key][zn] > 0).astype(float))))
    ratio = dict(score="E[m|ind]/E[m|dec]", auroc=np.nan, value=p["n2"].mean() / n["n2"].mean(),
                 mean_m_given_ge1_ind=p["n2"][p["n2"] > 0].mean(), mean_m_given_ge1_dec=n["n2"][n["n2"] > 0].mean())
    rows.append(ratio)
    return pd.DataFrame(rows)


def attack_decomposition(g, sets, fracs=(.005, .01, .02, .05, .10)):
    drug, disease, _ = g.layers(np.ones(len(g.uv), bool))
    kD, kY = np.asarray(drug.sum(0)).ravel(), np.asarray(disease.sum(0)).ravel()
    weight = kD * kY
    ind = sets["indication"]
    shared = drug[ind[:, 0]].multiply(disease[ind[:, 1]]).tocsr()
    m = np.diff(shared.indptr)
    keep = m > 0
    q, sh, mm = ind[keep], shared[keep], m[keep]
    rank = np.lexsort((np.arange(g.n), -g.degree))
    rows = []
    for f in fracs:
        removed = np.zeros(g.n, bool)
        removed[rank[:n_removed(f, g.n)]] = True
        ends = ~removed[q[:, 0]] & ~removed[q[:, 1]]
        survived = np.array([np.any(~removed[sh.indices[sh.indptr[i]:sh.indptr[i + 1]]]) for i in range(len(q))])
        h_graph = weight[removed].sum() / weight.sum()
        h_query = removed[sh[ends].indices].mean()
        rows.append(dict(frac_removed=f, two_hop_indications=len(q), lost_drug=removed[q[:, 0]].mean(),
                         lost_disease=removed[q[:, 1]].mean(), lost_endpoint_points=100 * (1 - ends.mean()),
                         lost_route_points=100 * ends.mean() * (1 - survived[ends].mean()),
                         kept=float(ends.mean() * survived[ends].mean()),
                         h_graph=h_graph, h_query=h_query,
                         mf_graph=1 - np.mean(h_graph ** mm[ends]), mf_query=1 - np.mean(h_query ** mm[ends]),
                         route_survival_measured=survived[ends].mean()))
    deg = g.degree
    meta = dict(median_disease_degree_two_hop=float(np.median(deg[q[:, 1]])),
                median_disease_degree_all=float(np.median(deg[ind[:, 1]])),
                degree_cut_5pct=float(deg[rank[n_removed(.05, g.n) - 1]]))
    return pd.DataFrame(rows), meta


def protein_only_attack(g, sets, fracs=(0, .005, .01, .02, .05)):
    rank_all = np.lexsort((np.arange(g.n), -g.degree))
    proteins = rank_all[g.types[rank_all] == "gene/protein"]
    pos, neg = sets["indication"], sets["decoy"]
    rows = []
    for label, order in (("all nodes", rank_all), ("proteins only", proteins)):
        for f in fracs:
            k = n_removed(f, g.n)
            node_alive = np.ones(g.n, bool)
            node_alive[order[:k]] = False
            alive = node_alive[g.uv[:, 0]] & node_alive[g.uv[:, 1]]
            rp = g.retrieval(pos, alive, node_alive, max_hops=3)
            rn = g.retrieval(neg, alive, node_alive, max_hops=3)
            row = dict(attack=label, frac_nodes=f, removed=k)
            for L in ("R2", "R3"):
                tp, fp = rp[L].mean(), rn[L].mean()
                row.update({f"{L}_ind": tp, f"{L}_dec": fp, f"{L}_ratio": tp / fp, f"{L}_mbit": 1000 * information(tp, fp)})
            rows.append(row)
    return pd.DataFrame(rows)


def sample_two_factor(fracs=(.01, .02, .05, .10)):
    """Mean field with graph-wide h and with the queries' own route hub share, on the sample benchmark."""
    import json
    from .common import load_order
    gid = "primekg_5000_bfs_v1"
    g = Graph(load_nodes(gid), load_edges(gid))
    drug, disease, _ = g.layers(np.ones(len(g.uv), bool))
    weight = np.asarray(drug.sum(0)).ravel() * np.asarray(disease.sum(0)).ravel()
    queries = json.loads((ROOT / "data" / "processed" / gid / "queries.json").read_text())
    q = np.array([[x["drug_nid"], x["disease_nid"]] for x in queries])
    sh = drug[q[:, 0]].multiply(disease[q[:, 1]]).tocsr()
    m = np.diff(sh.indptr)
    rows = []
    for name in ("node_degree", "node_betweenness"):
        order = load_order(gid, name)
        for f in fracs:
            removed = np.zeros(g.n, bool)
            removed[order[:n_removed(f, g.n)]] = True
            ends = ~removed[q[:, 0]] & ~removed[q[:, 1]]
            survived = np.array([np.any(~removed[sh.indices[sh.indptr[i]:sh.indptr[i + 1]]]) for i in range(len(q))])
            h_graph = weight[removed].sum() / weight.sum()
            h_query = removed[sh[ends].indices].mean()
            rows.append(dict(graph="sample", attack=name.replace("node_", ""), frac_removed=f, h_graph=h_graph,
                             h_query=h_query, mf_graph=1 - np.mean(h_graph ** m[ends]),
                             mf_query=1 - np.mean(h_query ** m[ends]), route_survival_measured=survived[ends].mean(),
                             lost_endpoint_points=100 * (1 - ends.mean()),
                             lost_route_points=100 * ends.mean() * (1 - survived[ends].mean())))
    return pd.DataFrame(rows)


def controls(seeds=range(5), n_random=619):
    """Decoy route hub share under attack, random-protein removal, hub-discounted score, odds ratios."""
    g, sets = setup()
    drug, disease, _ = g.layers(np.ones(len(g.uv), bool))
    rank = np.lexsort((np.arange(g.n), -g.degree))
    rows = []
    for f in (.01, .05):
        removed = np.zeros(g.n, bool)
        removed[rank[:n_removed(f, g.n)]] = True
        for name, q in sets.items():
            sh = drug[q[:, 0]].multiply(disease[q[:, 1]]).tocsr()
            keep = np.diff(sh.indptr) > 0
            ends = ~removed[q[keep, 0]] & ~removed[q[keep, 1]]
            rows.append(dict(control="own route hub share under degree attack", set=name, frac_removed=f,
                             value=removed[sh[keep][ends].indices].mean()))
    proteins = np.flatnonzero(g.types == "gene/protein")
    ratios, infos = [], []
    for s in seeds:
        pick = np.random.default_rng(100 + s).choice(proteins, n_random, replace=False)
        node_alive = np.ones(g.n, bool)
        node_alive[pick] = False
        alive = node_alive[g.uv[:, 0]] & node_alive[g.uv[:, 1]]
        tp = g.retrieval(sets["indication"], alive, node_alive, max_hops=2)["R2"].mean()
        fp = g.retrieval(sets["decoy"], alive, node_alive, max_hops=2)["R2"].mean()
        ratios.append(tp / fp)
        infos.append(1000 * information(tp, fp))
    rows.append(dict(control=f"random removal of {n_random} proteins: ratio", set="both", value=np.mean(ratios)))
    rows.append(dict(control=f"random removal of {n_random} proteins: mbit", set="both", value=np.mean(infos)))
    weight = np.zeros(g.n)
    weight[g.degree > 0] = 1 / g.degree[g.degree > 0]
    score = {k: np.asarray(drug[q[:, 0]].multiply(disease[q[:, 1]]).tocsr() @ weight).ravel() for k, q in sets.items()}
    rows.append(dict(control="AUROC of sum of 1/k over shared proteins", set="both",
                     value=auroc(score["indication"], score["decoy"])))
    summary = pd.read_csv(ROOT / "results" / "ws6" / "indication_intact_summary.csv").set_index("set")
    for L in ("R2", "R3", "R4"):
        a, b = summary.loc["indication", L], summary.loc["decoy", L]
        rows.append(dict(control=f"odds ratio {L}", set="both", value=(a / (1 - a)) / (b / (1 - b))))
    return pd.DataFrame(rows)


def excess_by_horizon():
    """Poisson excess r_L of real over chance paths: 1 - TPR = (1 - FPR)^r, from the random-damage scan."""
    scan = pd.read_csv(ROOT / "results" / "ws6" / "indication_damage_scan.csv")
    rnd = scan[scan.kind == "edge_random"].groupby("frac_removed").mean(numeric_only=True)
    rows = []
    for f, row in rnd.iterrows():
        for L in ("R2", "R3", "R4"):
            tp, fp = row[f"{L}_pos"], row[f"{L}_neg"]
            rows.append(dict(frac_removed=f, horizon=L, decoy_rate=fp, ratio=tp / fp,
                             r_excess=np.log(1 - tp) / np.log(1 - fp)))
    return pd.DataFrame(rows)


def path_count_means():
    """Mean numbers of typed paths of length 2, 3, 4 for indications and decoys (intact graph)."""
    g, sets = setup()
    rows = []
    for name, q in sets.items():
        c = counts(g, q)
        rows.append(dict(set=name, **{f"mean_{k}": float(c[k].mean()) for k in ("n2", "n3", "n4")},
                         var_over_mean_n3=float(c["n3"].var() / c["n3"].mean())))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    g, sets = setup()
    b = ball_null(g, sets)
    b.to_csv(OUT / "ball_null.csv", index=False, lineterminator="\n")
    print(b.round(4).to_string())
    ci = count_information(g, sets)
    ci.to_csv(OUT / "count_information.csv", index=False, lineterminator="\n")
    print(ci.round(4).to_string())
    dec, meta = attack_decomposition(g, sets)
    dec.to_csv(OUT / "attack_decomposition.csv", index=False, lineterminator="\n")
    print(dec.round(3).to_string(), meta)
    pa = protein_only_attack(g, sets)
    pa.to_csv(OUT / "protein_only_attack.csv", index=False, lineterminator="\n")
    print(pa.round(3).to_string())
    full = dec.assign(graph="full, two-hop indications", attack="degree")
    cols = ["graph", "attack", "frac_removed", "h_graph", "h_query", "mf_graph", "mf_query",
            "route_survival_measured", "lost_endpoint_points", "lost_route_points"]
    pd.concat([full[cols], sample_two_factor()[cols]]).to_csv(OUT / "mean_field_two_factor.csv", index=False,
                                                              lineterminator="\n")
    controls().to_csv(OUT / "controls.csv", index=False, lineterminator="\n")
    excess_by_horizon().to_csv(OUT / "excess_by_horizon.csv", index=False, lineterminator="\n")
    path_count_means().to_csv(OUT / "path_count_means.csv", index=False, lineterminator="\n")
