"""External validation on the full filtered graph with PrimeKG's own drug indications (D, 22 Nov).

The benchmark of the main study is self-referential: a query succeeds if a typed
path exists. Here the queries are the 6,233 approved drug--disease indications of
PrimeKG whose drug and disease are both in the filtered graph. These edges were
removed when the graph was built, so they are ground truth that the graph never
saw. Each indication is paired with a degree-preserving decoy: the diseases of
the indication list are permuted among its drugs, and pairs with any known
drug--disease relation (indication, contraindication, off-label use) are
rejected. Positives and decoys therefore have identical drug-degree and
disease-degree distributions.

For each damage state we record, at hop limits L = 2, 3, 4 and unlimited,
  recall      TPR = fraction of indications that still have a typed path,
  false rate  FPR = the same fraction for decoys,
  information I(label; path exists) in bits for a balanced mixture.

Inputs: data/processed/primekg_full_v1, and data/raw/kg.csv (only rows whose
relation is indication, contraindication or off-label use are read).
Run from the repository root: python -m src.run_ws6_indications
"""
import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.csgraph import connected_components

from . import theory
from .common import ROOT, load_edges, load_nodes, load_order, n_removed

GID = "primekg_full_v1"
OUT = ROOT / "results" / "ws6"
RAW = ROOT / "data" / "raw" / "kg.csv"
DRUG_DISEASE = ("indication", "contraindication", "off-label use")
RANDOM_GRID = np.round(np.arange(0, .9001, .1), 2)
ATTACK_GRID = (0, .005, .01, .02, .03, .05, .075, .1, .15, .2)
SEEDS = range(5)
HOPS = ("R2", "R3", "R4", "Rinf")


def drug_disease_relations(path=RAW):
    """Rows of kg.csv with a drug--disease relation, oriented drug -> disease."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            if r[0] in DRUG_DISEASE and r[4] == "drug" and r[9] == "disease":
                rows.append((r[0], int(r[2]), int(r[7])))
    return pd.DataFrame(rows, columns=["relation", "x_index", "y_index"])


def benchmark(nodes, relations, seed=42):
    x2n = dict(zip(nodes.x_index, nodes.nid))
    rel = relations.assign(d=relations.x_index.map(x2n), y=relations.y_index.map(x2n)).dropna()
    rel[["d", "y"]] = rel[["d", "y"]].astype(int)
    known = set(zip(rel.d, rel.y))
    pos = rel[rel.relation == "indication"][["d", "y"]].drop_duplicates().to_numpy()
    contra = rel[rel.relation == "contraindication"][["d", "y"]].drop_duplicates().to_numpy()
    rng = np.random.default_rng(seed)
    neg = {}
    while len(neg) < len(pos):
        perm = rng.permutation(len(pos))
        for d, y in zip(pos[:, 0], pos[perm, 1]):
            if (d, y) not in known:
                neg.setdefault((int(d), int(y)), None)
    neg = np.array(list(neg)[:len(pos)])
    return pos, neg, contra, rel


class Graph:
    def __init__(self, nodes, edges):
        self.n = len(nodes)
        self.types = nodes.node_type.to_numpy()
        self.uv = edges[["u", "v"]].to_numpy(dtype=np.int64)
        self.rel = edges.relation.to_numpy()
        self.degree = np.bincount(self.uv.ravel(), minlength=self.n)

    def layers(self, alive):
        n, uv, rel, types = self.n, self.uv, self.rel, self.types

        def bipartite(name, entity):
            sel = (rel == name) & alive
            a, b = uv[sel, 0], uv[sel, 1]
            left = types[a] == entity
            return sparse.csr_matrix((np.ones(sel.sum()), (np.where(left, a, b), np.where(left, b, a))), shape=(n, n))

        sel = (rel == "protein_protein") & alive
        ppi = sparse.csr_matrix((np.ones(sel.sum()), (uv[sel, 0], uv[sel, 1])), shape=(n, n))
        return bipartite("drug_protein", "drug"), bipartite("disease_protein", "disease"), ppi + ppi.T

    def giant(self, alive):
        a = sparse.csr_matrix((np.ones(alive.sum()), (self.uv[alive, 0], self.uv[alive, 1])), shape=(self.n, self.n))
        return np.bincount(connected_components(a, directed=False)[1]).max() / self.n

    def retrieval(self, q, alive, node_alive=None, max_hops=4):
        """Success of typed retrieval d -> protein (-PPI-)* -> y at L = 2..max_hops and unlimited."""
        drug, disease, ppi = self.layers(alive)
        dq, yq = drug[q[:, 0]], disease[q[:, 1]]
        out = {"m": np.rint(np.asarray(dq.multiply(yq).sum(1)).ravel()).astype(int)}
        out["R2"] = out["m"] > 0
        step = sparse.identity(self.n, format="csr") + ppi
        reach = dq
        for hops in range(3, max_hops + 1):
            reach = reach @ step
            reach.data[:] = 1
            out[f"R{hops}"] = np.asarray(reach.multiply(yq).sum(1)).ravel() > 0
        label = connected_components(ppi, directed=False)[1]
        k = label.max() + 1

        def by_component(mat):
            rows = np.repeat(np.arange(len(q)), np.diff(mat.indptr))
            return sparse.csr_matrix((np.ones(mat.nnz), (rows, label[mat.indices])), shape=(len(q), k))

        out["Rinf"] = np.asarray(by_component(dq).multiply(by_component(yq)).sum(1)).ravel() > 0
        if node_alive is not None:
            ok = node_alive[q[:, 0]] & node_alive[q[:, 1]]
            out = {key: v * ok if key == "m" else v & ok for key, v in out.items()}
        return out


def information(tpr, fpr):
    """I(label; success) in bits for a balanced mixture of positives and decoys."""
    def h(x):
        x = np.clip(x, 1e-12, 1 - 1e-12)
        return -(x * np.log2(x) + (1 - x) * np.log2(1 - x))
    return h((tpr + fpr) / 2) - (h(tpr) + h(fpr)) / 2


def configuration_model(g, pos, neg):
    """Expected typed-path counts in a configuration model with the same layer degrees.

    A drug with k_d targets and a disease with k_y proteins share, on average,
    Lambda_2 = k_d k_y sum_x a_x b_x / (A B) proteins, where a_x and b_x are the drug and
    disease degrees of protein x and A, B the layer totals. Each PPI step multiplies the
    count of longer paths by about kappa - 1, with kappa = <k^2>/<k> of the PPI layer.
    The probability that at least one path exists is 1 - exp(-Lambda_L).
    """
    drug, disease, ppi = g.layers(np.ones(len(g.uv), bool))
    a, b = np.asarray(drug.sum(0)).ravel(), np.asarray(disease.sum(0)).ravel()
    k = np.asarray(ppi.sum(1)).ravel()
    kd, ky = np.asarray(drug.sum(1)).ravel(), np.asarray(disease.sum(1)).ravel()
    A, B, K = a.sum(), b.sum(), k.sum()
    kappa = (k ** 2).sum() / K
    c2 = (a * b).sum() / (A * B)
    c3 = (a * k).sum() * (b * k).sum() / (A * B * K)
    c4 = c3 * (kappa - 1)
    rows = []
    for name, q in (("indication", pos), ("decoy", neg)):
        x = kd[q[:, 0]] * ky[q[:, 1]]
        lam = {"R2": c2 * x, "R3": (c2 + c3) * x, "R4": (c2 + c3 + c4) * x}
        rows.append(dict(set=name, kappa=kappa, c2=c2, c3=c3, c4=c4,
                         **{key: float(np.mean(1 - np.exp(-v))) for key, v in lam.items()}))
    return pd.DataFrame(rows)


def intact_uncertainty(g, pos, relations, nodes, seeds=range(1, 6), n_boot=1000):
    """Spread of the intact decoy rate over decoy seeds, and drug-cluster bootstrap of the ratios."""
    alive = np.ones(len(g.uv), bool)
    rp = g.retrieval(pos, alive)
    rows = []
    for seed in seeds:
        neg = benchmark(nodes, relations, seed=seed)[1]
        rn = g.retrieval(neg, alive)
        rows.append(dict(kind="decoy_seed", seed=seed, **{f"{k}_neg": float(rn[k].mean()) for k in HOPS},
                         **{f"{k}_ratio": float(rp[k].mean() / rn[k].mean()) for k in HOPS}))
    neg = benchmark(nodes, relations, seed=42)[1]
    rn = g.retrieval(neg, alive)
    rng = np.random.default_rng(7)
    drugs = np.unique(pos[:, 0])
    pos_by = {d: np.flatnonzero(pos[:, 0] == d) for d in drugs}
    neg_by = {d: np.flatnonzero(neg[:, 0] == d) for d in drugs}
    boot = {k: [] for k in HOPS}
    for _ in range(n_boot):
        pick = rng.choice(drugs, len(drugs))
        ip = np.concatenate([pos_by[d] for d in pick])
        iq = np.concatenate([neg_by[d] for d in pick])
        for k in HOPS:
            boot[k].append(rp[k][ip].mean() / max(rn[k][iq].mean(), 1e-12))
    for k in HOPS:
        lo, hi = np.percentile(boot[k], [2.5, 97.5])
        rows.append(dict(kind="drug_bootstrap", seed=42, hop=k, ratio=float(rp[k].mean() / rn[k].mean()),
                         ci_low=float(lo), ci_high=float(hi), n_drugs=len(drugs)))
    return pd.DataFrame(rows)


def damage_scan(g, pos, neg):
    both = np.vstack([pos, neg])
    is_pos = np.r_[np.ones(len(pos), bool), np.zeros(len(neg), bool)]
    E = len(g.uv)
    rank = np.lexsort((np.arange(g.n), -g.degree))
    states = [("edge_random", f, s) for f in RANDOM_GRID for s in SEEDS] + [("degree", f, None) for f in ATTACK_GRID]
    rows = []
    for kind, f, seed in states:
        if kind == "edge_random":
            alive = np.ones(E, bool)
            alive[load_order(GID, f"edge_random_s{seed}")[:n_removed(f, E)]] = False
            node_alive = None
        else:
            node_alive = np.ones(g.n, bool)
            node_alive[rank[:n_removed(f, g.n)]] = False
            alive = node_alive[g.uv[:, 0]] & node_alive[g.uv[:, 1]]
        r = g.retrieval(both, alive, node_alive)
        row = dict(kind=kind, frac_removed=f, seed=seed, S=g.giant(alive))
        for key in HOPS:
            tpr, fpr = r[key][is_pos].mean(), r[key][~is_pos].mean()
            row.update({f"{key}_pos": tpr, f"{key}_neg": fpr, f"{key}_info_bits": information(tpr, fpr)})
        rows.append(row)
        print(kind, f, seed, round(row["R2_pos"], 4), round(row["R2_neg"], 4), flush=True)
    return pd.DataFrame(rows)


def intact_summary(g, pos, neg, contra):
    alive = np.ones(len(g.uv), bool)
    hub_cut = np.quantile(g.degree[g.types == "gene/protein"], .99)
    drug, disease, _ = g.layers(alive)
    rows = []
    for name, q in (("indication", pos), ("decoy", neg), ("contraindication", contra)):
        r = g.retrieval(q, alive, max_hops=3 if name == "contraindication" else 4)
        m = r["m"]
        shared = drug[q[:, 0]].multiply(disease[q[:, 1]]).tocoo()
        hub_share = float(np.mean(g.degree[shared.col] >= hub_cut)) if shared.nnz else np.nan
        row = dict(set=name, pairs=len(q), share_m_ge1=float(np.mean(m >= 1)),
                   share_m1_given_ge1=float(np.mean(m[m >= 1] == 1)), mean_m_given_ge1=float(m[m >= 1].mean()),
                   shared_protein_hub_share=hub_share, hub_degree_cut=float(hub_cut))
        for key in HOPS:
            if key in r:
                row[key] = float(r[key].mean())
        rows.append(row)
    return pd.DataFrame(rows)


def two_hop_theory(g, pos, neg):
    """Eq. (6) for indications and decoys under random edge removal."""
    alive = np.ones(len(g.uv), bool)
    r = g.retrieval(np.vstack([pos, neg]), alive, max_hops=2)
    m_pos, m_neg = r["m"][:len(pos)], r["m"][len(pos):]
    return pd.DataFrame([dict(frac_removed=f, R2_pos_theory=theory.R_edge(1 - f, m_pos[m_pos > 0]) * np.mean(m_pos > 0),
                              R2_neg_theory=theory.R_edge(1 - f, m_neg[m_neg > 0]) * np.mean(m_neg > 0))
                         for f in RANDOM_GRID])


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    nodes, edges = load_nodes(GID), load_edges(GID)
    g = Graph(nodes, edges)
    relations = drug_disease_relations(Path(sys.argv[1]) if len(sys.argv) > 1 else RAW)
    pos, neg, contra, rel = benchmark(nodes, relations)
    pd.DataFrame(np.vstack([pos, neg]), columns=["drug", "disease"]).assign(
        label=np.r_[np.ones(len(pos), int), np.zeros(len(neg), int)]).to_csv(
        OUT / "indication_benchmark.csv", index=False, lineterminator="\n")
    summary = intact_summary(g, pos, neg, contra)
    summary.to_csv(OUT / "indication_intact_summary.csv", index=False, lineterminator="\n")
    print(summary.round(4).to_string())
    cm = configuration_model(g, pos, neg)
    cm.to_csv(OUT / "indication_config_model.csv", index=False, lineterminator="\n")
    print(cm.round(4).to_string())
    unc = intact_uncertainty(g, pos, relations, nodes)
    unc.to_csv(OUT / "indication_intact_uncertainty.csv", index=False, lineterminator="\n")
    th = two_hop_theory(g, pos, neg)
    th.to_csv(OUT / "indication_two_hop_theory.csv", index=False, lineterminator="\n")
    scan = damage_scan(g, pos, neg)
    scan.to_csv(OUT / "indication_damage_scan.csv", index=False, lineterminator="\n")
