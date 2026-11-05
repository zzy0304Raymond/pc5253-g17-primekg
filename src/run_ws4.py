"""WS4: theory tables, correlation penalty, equal damage, prediction, checks.

Inputs are the frozen graph plus the A, B and C results already in the repository.
Run from the repository root: python -m src.run_ws4 primekg_5000_bfs_v1
"""
import argparse
import platform

import numpy as np
import pandas as pd

from . import prediction, theory
from .common import (EDGE_LEVELS, NODE_LEVELS, RESULT_COLUMNS, ROOT, SEEDS, graph_dir, load_edges,
                     load_nodes, load_order, load_queries, n_removed, sha256, write_json)
from .percolation import nz_edges, nz_nodes
from .retrieval import Retriever

BOUNDARY_GAP = .05
ATTACKS = ("node_degree", "node_betweenness")


def long_row(gid, strategy, seed, frac, removed, metric, value):
    return gid, strategy, seed, frac, removed, metric, float(value)


def frame(rows):
    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


def hop_scan(gid, queries):
    """All four hop limits for all ten official seeds, through C's Retriever."""
    retriever = Retriever(gid)
    total = len(retriever.edges)
    proteins = int(load_nodes(gid).node_type.eq("gene/protein").sum())
    rows = []
    for seed in SEEDS:
        order = load_order(gid, f"edge_random_s{seed}")
        for frac in EDGE_LEVELS:
            removed = n_removed(frac, total)
            alive = np.ones(total, dtype=bool)
            alive[order[:removed]] = False
            distance = retriever.evaluate(queries, edge_alive=alive, compute_dist=True).d_ppi.to_numpy()
            values = {"R_L2": distance == 0, "R_L3": distance <= 1, "R_L4": distance <= 2,
                      "R_Linf": np.isfinite(distance)}
            for metric, success in values.items():
                rows.append(long_row(gid, "edge_random", seed, frac, removed, metric, success.mean()))
            ppi = retriever.ppi_edges[alive[retriever.ppi_ids]]
            rows.append(long_row(gid, "edge_random", seed, frac, removed, "ppi_gcc_frac",
                                 largest_component(retriever.n, ppi) / proteins))
    return frame(rows)


def failure_channels(gid, queries):
    """Why L = infinity fails: a lost terminal link, or a disconnected PPI route."""
    retriever = Retriever(gid)
    total = len(retriever.edges)
    entity = retriever.terminal_edges[:, 0]
    rows = []
    for seed in SEEDS:
        order = load_order(gid, f"edge_random_s{seed}")
        for frac in EDGE_LEVELS:
            removed = n_removed(frac, total)
            alive = np.ones(total, dtype=bool)
            alive[order[:removed]] = False
            distance = retriever.evaluate(queries, edge_alive=alive, compute_dist=True).d_ppi.to_numpy()
            attached = set(entity[alive[retriever.terminal_ids]].tolist())
            ends = np.array([q["drug_nid"] in attached and q["disease_nid"] in attached for q in queries])
            success = np.isfinite(distance)
            rows.append(long_row(gid, "edge_random", seed, frac, removed, "fail_terminal", (~ends).mean()))
            rows.append(long_row(gid, "edge_random", seed, frac, removed, "fail_disconnected", (ends & ~success).mean()))
    return frame(rows)


def largest_component(n, uv):
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    graph = coo_matrix((np.ones(len(uv)), (uv[:, 0], uv[:, 1])), shape=(n, n))
    _, labels = connected_components(graph, directed=False)
    return np.bincount(labels).max()


def theory_table(gid, queries):
    features = pd.read_csv(graph_dir(gid) / "node_features.csv")
    degree = features.degree.to_numpy(dtype=np.int64)
    ppi = features[features.node_type == "gene/protein"].ppi_degree.to_numpy(dtype=np.int64)
    m = np.array([q["redundancy_m"] for q in queries])
    groups = np.array([q["group"] for q in queries])
    edges, nodes = len(load_edges(gid)), len(features)
    rows = []
    # Dense grids keep curves smooth in the figures; the official levels stay included.
    edge_grid = sorted(set(EDGE_LEVELS) | set(np.round(np.arange(0, 1.0001, .01), 2)))
    for frac in edge_grid:
        removed = n_removed(frac, edges)
        p = 1 - removed / edges
        values = {"R_L2": theory.R_edge(p, m), "R_L2_single": theory.R_edge(p, m[groups == "single"]),
                  "R_L2_multi": theory.R_edge(p, m[groups == "multi"]),
                  "R_Linf": theory.R_inf_edge(p, gid, queries),
                  "R_Linf_union": theory.R_inf_edge_union(p, gid, queries),
                  "R_attachment_bound": theory.R_attachment_bound(p, gid, queries),
                  "gcc_frac": theory.gcc_bond(degree, p), "ppi_gcc_frac": theory.gcc_bond(ppi, p)}
        for metric, value in values.items():
            rows.append(long_row(gid, "theory_bond", -1, frac, removed, metric, value))
    for frac in sorted(set(NODE_LEVELS) | set(np.round(np.arange(0, 1.0001, .05), 2))):
        removed = n_removed(frac, nodes)
        phi = 1 - removed / nodes
        rows.append(long_row(gid, "theory_site", -1, frac, removed, "R_L2", theory.R_node(phi, m)))
        rows.append(long_row(gid, "theory_site", -1, frac, removed, "gcc_frac", theory.gcc_site(degree, phi)))
        rows.append(long_row(gid, "theory_attack", -1, frac, removed, "gcc_frac",
                             theory.gcc_degree_attack(degree, removed / nodes)))
    return frame(rows)


def correlation_penalty(gid, queries):
    """Delta(f) and its exact split into hub-endpoint and hub-path channels.

    With phi^2 and C_th the formula's endpoint and path factors, and E and C the
    measured ones: Delta = (phi^2 - E) C_th + E (C_th - C).
    """
    m = np.array([q["redundancy_m"] for q in queries])
    nodes = len(load_nodes(gid))
    rows = []
    for strategy in ATTACKS:
        path = ROOT / "results" / "ws3" / f"{gid}__perquery__{strategy}__s-1.csv"
        data = pd.read_csv(path)
        for frac in NODE_LEVELS:
            removed = n_removed(frac, nodes)
            phi = 1 - removed / nodes
            level = data[data.frac_removed == frac]
            endpoint = (level.drug_alive & level.disease_alive).mean()
            measured = (level.s_alive > 0).mean()
            formula = theory.R_node(phi, m)
            if phi == 0:
                continue
            path_formula = formula / phi ** 2
            given = measured / endpoint if endpoint else 0.0
            values = {"corr_penalty": formula - measured, "R_L2": measured, "R_L2_formula": formula,
                      "endpoint_alive": endpoint, "path_given_endpoints": given,
                      "penalty_endpoint": (phi ** 2 - endpoint) * path_formula,
                      "penalty_path": endpoint * (path_formula - given)}
            for metric, value in values.items():
                rows.append(long_row(gid, strategy, -1, frac, removed, metric, value))
    return frame(rows)


def hub_exposure(gid, queries):
    """How much of the benchmark sits on the nodes a 5% attack removes."""
    features = pd.read_csv(graph_dir(gid) / "node_features.csv")
    degree = features.degree.to_numpy()
    proteins = features.node_type.eq("gene/protein").to_numpy()
    inter = np.array(sorted({x for q in queries for x in q["intermediates"]}))
    paths = np.array([x for q in queries for x in q["intermediates"]])
    rows = {"median_degree_all_proteins": float(np.median(degree[proteins])),
            "median_degree_query_intermediate_proteins": float(np.median(degree[inter])),
            "median_degree_query_path_weighted": float(np.median(degree[paths]))}
    count = n_removed(.05, len(degree))
    for strategy in ATTACKS:
        top = set(load_order(gid, strategy)[:count].tolist())
        for group in ("single", "multi"):
            subset = [q for q in queries if q["group"] == group]
            rows[f"{strategy}_top5pct_all_intermediates_{group}"] = float(
                np.mean([all(x in top for x in q["intermediates"]) for q in subset]))
        rows[f"{strategy}_top5pct_disease_endpoint"] = float(np.mean([q["disease_nid"] in top for q in queries]))
        rows[f"{strategy}_top5pct_drug_endpoint"] = float(np.mean([q["drug_nid"] in top for q in queries]))
    return rows


def equal_damage(gid):
    """S and R for the three node strategies at each common damage level."""
    structure = pd.read_csv(ROOT / "results" / gid / "ws2_attack_results_long.csv")
    retrieval = pd.read_csv(ROOT / "results" / "ws3" / f"{gid}__retrieval.csv")
    rows = []
    names = {"random": "node_random", "degree": "node_degree", "betweenness": "node_betweenness"}
    for source, strategy in names.items():
        for frac in NODE_LEVELS:
            s = structure[(structure.strategy == source) & (structure.metric == "gcc_frac")
                          & np.isclose(structure.frac_removed, frac)]
            r = retrieval[(retrieval.strategy == strategy) & (retrieval.metric == "R_L2")
                          & (retrieval.frac_removed == frac)]
            deterministic = strategy != "node_random"
            for _, row in s.iterrows():
                rows.append(long_row(gid, strategy, -1 if deterministic else int(row.seed), frac,
                                     int(row.n_removed), "gcc_frac", row.value))
            for _, row in r.iterrows():
                rows.append(long_row(gid, strategy, int(row.seed), frac, int(row.n_removed), "R_L2", row.value))
    data = frame(rows)
    mean = data.groupby(["strategy", "frac_removed", "metric"]).value.mean().unstack("metric").reset_index()
    wide = mean.pivot(index="frac_removed", columns="strategy", values=["gcc_frac", "R_L2"])
    summary = []
    for frac, row in wide.iterrows():
        order = lambda metric: tuple(sorted(names.values(), key=lambda s: row[(metric, s)]))
        summary.append(dict(frac_removed=frac, rank_by_S=" < ".join(order("gcc_frac")),
                            rank_by_R=" < ".join(order("R_L2")),
                            same_order=order("gcc_frac") == order("R_L2"),
                            S_gap_random_minus_degree=row[("gcc_frac", "node_random")] - row[("gcc_frac", "node_degree")],
                            R_gap_random_minus_degree=row[("R_L2", "node_random")] - row[("R_L2", "node_degree")],
                            S_gap_degree_minus_betweenness=row[("gcc_frac", "node_degree")] - row[("gcc_frac", "node_betweenness")],
                            R_gap_degree_minus_betweenness=row[("R_L2", "node_degree")] - row[("R_L2", "node_betweenness")]))
    return data, pd.DataFrame(summary)


def attack_overlay(gid, table):
    """B's curves with shared strategy names and D's theory, every 5% removal."""
    structure = pd.read_csv(ROOT / "results" / gid / "ws2_attack_results_long.csv")
    grid = np.round(np.arange(0, 1.0001, .05), 2)
    rows = []
    for source, strategy in (("random", "node_random"), ("degree", "node_degree"), ("betweenness", "node_betweenness")):
        part = structure[(structure.strategy == source) & (structure.metric == "gcc_frac")]
        for frac in grid:
            for _, row in part[np.isclose(part.frac_removed, frac)].iterrows():
                seed = -1 if strategy != "node_random" else int(row.seed)
                rows.append(long_row(gid, strategy, seed, frac, int(row.n_removed), "gcc_frac", row.value))
    theory_rows = table[(table.strategy == "theory_attack") & table.frac_removed.isin(grid)]
    return pd.concat([frame(rows), theory_rows], ignore_index=True)


def hop_boundary(scan):
    """First official f at which each hop limit falls BOUNDARY_GAP below L = infinity."""
    mean = scan.groupby(["metric", "frac_removed"]).value.mean().unstack("metric")
    rows = []
    for metric in ("R_L2", "R_L3", "R_L4"):
        gap = mean["R_Linf"] - mean[metric]
        rows.append(dict(metric=metric, gap=BOUNDARY_GAP, first_f=float(gap[gap >= BOUNDARY_GAP].index.min())))
    return pd.DataFrame(rows)


def monte_carlo(gid, queries, n_orders=5000, seed=20261105):
    """Mean R over fresh orders; separates sampling noise from model error."""
    edges, nodes = load_edges(gid), load_nodes(gid)
    lookup = {(row.u, row.v): row.eid for row in edges.itertuples()}
    paths = []
    for i, q in enumerate(queries):
        for x in q["intermediates"]:
            ends = [lookup[(min(a, x), max(a, x))] for a in (q["drug_nid"], q["disease_nid"])]
            paths.append((i, ends[0], ends[1], x))
    paths = np.array(paths)
    m = np.array([q["redundancy_m"] for q in queries])
    drug = np.array([q["drug_nid"] for q in queries])
    disease = np.array([q["disease_nid"] for q in queries])
    rng = np.random.default_rng(seed)
    rows = []
    for kind, levels, total, formula in (("edge", EDGE_LEVELS, len(edges), theory.R_edge),
                                         ("node", NODE_LEVELS, len(nodes), theory.R_node)):
        samples = np.zeros((n_orders, len(levels)))
        for t in range(n_orders):
            rank = rng.permutation(total)
            for j, frac in enumerate(levels):
                cut = n_removed(frac, total)
                success = np.zeros(len(queries), dtype=bool)
                if kind == "edge":
                    np.logical_or.at(success, paths[:, 0], np.minimum(rank[paths[:, 1]], rank[paths[:, 2]]) >= cut)
                else:
                    alive = rank >= cut
                    np.logical_or.at(success, paths[:, 0], alive[paths[:, 3]])
                    success &= alive[drug] & alive[disease]
                samples[t, j] = success.mean()
        for j, frac in enumerate(levels):
            keep = 1 - n_removed(frac, total) / total
            rows.append(dict(kind=kind, frac_removed=frac, n_orders=n_orders, mc_mean=samples[:, j].mean(),
                             mc_se=samples[:, j].std(ddof=1) / np.sqrt(n_orders), seed_sd=samples[:, j].std(ddof=1),
                             formula=formula(keep, m)))
    return pd.DataFrame(rows)


def configuration_check(gid, realisations=10, seed=20261105):
    """D1: on a stub-matched graph with the same degrees, theory must agree."""
    degree = pd.read_csv(graph_dir(gid) / "node_features.csv").degree.to_numpy(dtype=np.int64)
    n = len(degree)
    rng = np.random.default_rng(seed)
    records = []
    levels = (.1, .3, .5, .7, .9, .95, .98)
    node_levels = (.1, .3, .5, .7, .9)
    attack_levels = (.05, .1, .2, .3, .4, .5, .6)
    for r in range(realisations):
        stubs = rng.permutation(np.repeat(np.arange(n), degree))
        stubs = stubs[:len(stubs) // 2 * 2].reshape(-1, 2)
        uv = stubs[stubs[:, 0] != stubs[:, 1]]
        out = nz_edges(n, uv, rng.permutation(len(uv)))
        for f in levels:
            records.append(("bond", r, f, out["gcc_size"][n_removed(f, len(uv))] / n))
        out = nz_nodes(n, uv, rng.permutation(n))
        for f in node_levels:
            records.append(("site", r, f, out["gcc_size"][n_removed(f, n)] / n))
        ranking = np.lexsort((rng.random(n), -degree))
        out = nz_nodes(n, uv, ranking)
        for f in attack_levels:
            records.append(("attack", r, f, out["gcc_size"][n_removed(f, n)] / n))
    data = pd.DataFrame(records, columns=["kind", "realisation", "frac_removed", "value"])
    agg = data.groupby(["kind", "frac_removed"]).value.agg(["mean", "std"]).reset_index()
    formulas = {"bond": lambda f: theory.gcc_bond(degree, 1 - f), "site": lambda f: theory.gcc_site(degree, 1 - f),
                "attack": lambda f: theory.gcc_degree_attack(degree, f)}
    agg["theory"] = [formulas[k](f) for k, f in zip(agg.kind, agg.frac_removed)]
    return agg


def crosscheck_reference(gid):
    """A's WS1 overlay used a separate solver; both must give the same curve."""
    from . import ws1_theory_reference as reference
    degree = pd.read_csv(graph_dir(gid) / "node_features.csv").degree.to_numpy(dtype=np.int64)
    grid = np.linspace(0, 1, 201)
    return float(max(max(abs(theory.gcc_bond(degree, p) - reference.gcc_bond(degree, p)),
                         abs(theory.gcc_site(degree, p) - reference.gcc_site(degree, p))) for p in grid))


def run(gid):
    out = ROOT / "results" / "ws4"
    out.mkdir(parents=True, exist_ok=True)
    queries = load_queries(gid)
    def save(table, name):
        table.to_csv(out / f"{gid}__{name}.csv", index=False, lineterminator="\n")
    scan = hop_scan(gid, queries)
    save(scan, "hop_scan_10seeds")
    save(hop_boundary(scan), "hop_boundary")
    save(failure_channels(gid, queries), "failure_channels")
    table = theory_table(gid, queries)
    save(table, "theory")
    save(attack_overlay(gid, table), "attack_overlay")
    save(correlation_penalty(gid, queries), "corr_penalty")
    data, summary = equal_damage(gid)
    save(data, "equal_damage")
    save(summary, "equal_damage_summary")
    table_p, detail = prediction.run(gid)
    save(table_p, "prediction")
    save(detail, "prediction_detail")
    save(monte_carlo(gid, queries), "monte_carlo_check")
    save(configuration_check(gid), "configuration_model_check")
    features = pd.read_csv(graph_dir(gid) / "node_features.csv")
    ppi = features[features.node_type == "gene/protein"].ppi_degree.to_numpy(dtype=np.int64)
    write_json(out / f"{gid}__provenance.json", {
        "gid": gid, "python": platform.python_version(),
        "manifest_sha256": sha256(graph_dir(gid) / "manifest.json"),
        "pc_bond_full_graph": theory.pc_bond(features.degree.to_numpy(dtype=np.int64)),
        "pc_bond_ppi": theory.pc_bond(ppi),
        "max_abs_difference_from_A_reference_gcc": crosscheck_reference(gid),
        "pairs_with_multiple_relations": 0,
        "hub_exposure": hub_exposure(gid, queries),
        "hop_scan_note": "Ten official seeds through C's Retriever; slide 8 uses seeds 0-2.",
        "source_sha256": {name: sha256(ROOT / "src" / name)
                          for name in ("theory.py", "prediction.py", "run_ws4.py", "retrieval.py")},
    })
    print(f"Saved WS4 tables for {gid} in {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gids", nargs="*", default=["primekg_5000_bfs_v1"])
    for gid in parser.parse_args().gids:
        run(gid)
