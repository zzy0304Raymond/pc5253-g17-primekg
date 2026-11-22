"""Report-stage checks for D (Sections 3 and 6).

1. ``mincut``      - drug-disease edge connectivity lambda for every query, and the
                     L = infinity "min-cut form" 1 - G_lambda(1 - p) against the
                     600 fresh orders of run_ws4.
2. ``uncertainty`` - why the seed bands are wide: seed-to-seed SD of R_2 compared
                     with the SD expected if the 200 queries failed independently.
3. ``restoration`` - zero-parameter prediction of E's random and relation-type
                     repair gains at L = 2 from the two-hop formula.

Run from the repository root: python -m src.run_ws4_report primekg_5000_bfs_v1
"""
import argparse

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow

from .common import ROOT, load_edges, load_nodes, load_queries, n_removed
from . import theory


def edge_connectivity(gid, queries):
    edges = load_edges(gid)
    n = len(load_nodes(gid))
    u, v = edges.u.to_numpy(), edges.v.to_numpy()
    graph = csr_matrix((np.ones(2 * len(u), dtype=np.int32), (np.r_[u, v], np.r_[v, u])), shape=(n, n))
    graph.sort_indices()
    return np.array([maximum_flow(graph, q["drug_nid"], q["disease_nid"]).flow_value for q in queries])


def mincut(gid, queries):
    edges = load_edges(gid)
    degree = np.bincount(edges[["u", "v"]].to_numpy().ravel(), minlength=len(load_nodes(gid)))
    lam = edge_connectivity(gid, queries)
    drug = np.array([degree[q["drug_nid"]] for q in queries])
    disease = np.array([degree[q["disease_nid"]] for q in queries])
    per_query = pd.DataFrame(dict(query_id=[q["query_id"] for q in queries], edge_connectivity=lam,
                                  drug_degree=drug, disease_degree=disease,
                                  equals_min_endpoint_degree=lam == np.minimum(drug, disease)))
    fresh = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__hop_fresh_orders.csv")
    curves = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__theory.csv")
    total = len(edges)
    rows = []
    for _, row in fresh.iterrows():
        frac = row.frac_removed
        p = 1 - n_removed(frac, total) / total
        gf = curves[(curves.strategy == "theory_bond") & (curves.metric == "R_Linf")
                    & np.isclose(curves.frac_removed, frac)].value.iloc[0]
        rows.append(dict(frac_removed=frac, R_Linf_fresh=row.R_Linf_mean, R_Linf_fresh_se=row.R_Linf_se,
                         mincut_form=float(np.mean(1 - (1 - p) ** lam)), gf_R_Linf=gf,
                         attachment_bound=theory.R_attachment_bound(p, gid, queries)))
    return per_query, pd.DataFrame(rows)


def uncertainty(gid, queries):
    m = np.array([q["redundancy_m"] for q in queries])
    total = len(load_edges(gid))
    mc = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__monte_carlo_check.csv")
    mc = mc[mc.kind == "edge"]
    measured = pd.read_csv(ROOT / "results" / "ws3" / f"{gid}__retrieval.csv")
    measured = measured[(measured.strategy == "edge_random") & (measured.metric == "R_L2")]
    rows = []
    for _, row in mc.iterrows():
        frac = row.frac_removed
        p = 1 - n_removed(frac, total) / total
        r = 1 - (1 - p * p) ** m
        independent = float(np.sqrt((r * (1 - r)).sum()) / len(m))
        seeds = measured[np.isclose(measured.frac_removed, frac)].value
        rows.append(dict(frac_removed=frac, formula=row.formula, fresh_mean=row.mc_mean, fresh_se=row.mc_se,
                         sd_one_damage_state=row.seed_sd, sd_if_queries_independent=independent,
                         variance_inflation=(row.seed_sd / independent) ** 2 if independent else np.nan,
                         official_10_seed_mean=seeds.mean(), official_10_seed_sd=seeds.std(ddof=1),
                         official_10_seed_se=seeds.std(ddof=1) / np.sqrt(len(seeds))))
    return pd.DataFrame(rows)


def restoration(gid, queries):
    edges = load_edges(gid)
    total = len(edges)
    terminal = int((edges.relation != "protein_protein").sum())
    m = np.array([q["redundancy_m"] for q in queries if q["split"] == "test"])
    summary = pd.read_csv(ROOT / "results" / "ws5" / "final" / gid / f"{gid}__summary.csv")
    rows = []
    for frac in (.3, .5):
        deleted = n_removed(frac, total)
        p = 1 - deleted / total
        base = theory.R_edge(p, m)
        for budget in (.05, .1, .2):
            restored = int(round(budget * deleted))
            p_random = 1 - (deleted - restored) / total
            # Relation-type repair spends the whole budget on deleted terminal edges.
            p_terminal = 1 - max(frac * terminal - restored, 0) / terminal
            for strategy, keep in (("restore_random", p_random), ("restore_relation_type", p_terminal)):
                hit = summary[(summary.strategy == strategy) & (summary.metric == "R_L2")
                              & np.isclose(summary.damage_frac, frac) & np.isclose(summary.budget_frac, budget)]
                measured, sd = 100 * hit.gain_mean.iloc[0], 100 * hit.gain_sd.iloc[0]
                predicted = 100 * (theory.R_edge(keep, m) - base)
                rows.append(dict(strategy=strategy, damage_frac=frac, budget_frac=budget,
                                 predicted_gain_pp=predicted, measured_gain_pp=measured, measured_sd_pp=sd,
                                 within_one_sd=abs(measured - predicted) <= sd))
    return pd.DataFrame(rows)


def run(gid):
    out = ROOT / "results" / "ws4"
    queries = load_queries(gid)
    per_query, curve = mincut(gid, queries)
    per_query.to_csv(out / f"{gid}__mincut_per_query.csv", index=False, lineterminator="\n")
    curve.to_csv(out / f"{gid}__mincut_Linf.csv", index=False, lineterminator="\n")
    uncertainty(gid, queries).to_csv(out / f"{gid}__uncertainty.csv", index=False, lineterminator="\n")
    restoration(gid, queries).to_csv(out / f"{gid}__restoration_prediction.csv", index=False, lineterminator="\n")
    print(f"lambda equals min endpoint degree for {per_query.equals_min_endpoint_degree.sum()} of {len(per_query)} queries")
    print(curve.round(4).to_string())
    print(uncertainty(gid, queries).round(4).to_string())
    print(restoration(gid, queries).round(2).to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gids", nargs="*", default=["primekg_5000_bfs_v1"])
    for gid in parser.parse_args().gids:
        run(gid)
