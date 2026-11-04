"""Prepare E's measured report tables and presentation assets from final runs."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.common import ROOT, load_edges, load_nodes, load_queries, load_order, n_removed
from src.figure_templates import draw, legend, render
from src.plotting import setup, save, STYLE
from src.restoration import training_path_eids, task_aware_scores


def main():
    gid = "primekg_5000_bfs_v1"
    working = ROOT / ".build/e_delivery"
    assets = working / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    folder = ROOT / "results/ws5/final" / gid
    metadata = json.loads((folder / "provenance.json").read_text(encoding="utf-8"))
    if metadata["evaluator"] != "c" or metadata["status"] != "complete" or metadata["missing_strategies"]:
        raise ValueError("A complete four-strategy C-evaluator run is required")
    nodes, edges, queries = load_nodes(gid), load_edges(gid), load_queries(gid)
    train = [q for q in queries if q["split"] == "train"]
    paths = training_path_eids(edges, train)
    table = pd.read_csv(folder / f"{gid}__summary.csv")
    table["gain_pp"] = 100 * table.gain_mean
    table["sd_pp"] = 100 * table.gain_sd
    table.to_csv(ROOT / "report/E_results_table.csv", index=False, lineterminator="\n")
    diagnostic = []
    for damage in metadata["damages"]:
        for seed in metadata["seeds"]:
            removed = load_order(gid, f"edge_random_s{seed}")[:n_removed(damage, len(edges))]
            alive = np.ones(len(edges), bool)
            alive[removed] = False
            scores = task_aware_scores(alive, paths)
            for budget in metadata["budgets"]:
                count = n_removed(budget, len(removed))
                positive = int((scores[removed] > 0).sum())
                diagnostic.append(dict(damage_frac=damage, seed=seed, budget_frac=budget,
                                       n_removed=len(removed), requested_n_restored=count,
                                       positive_score_candidates=positive,
                                       zero_score_selected=max(0, count-positive),
                                       positive_share=min(count,positive)/count if count else np.nan))
    diagnostic = pd.DataFrame(diagnostic)
    diagnostic.to_csv(ROOT / "report/E_static_score_diagnostics.csv", index=False, lineterminator="\n")
    counts = pd.read_csv(folder / f"{gid}__restored_edge_types.csv")
    counts = counts[counts.budget_frac > 0].copy()
    counts["fraction"] = counts["count"] / counts.n_restored
    composition = counts.groupby(["damage_frac", "budget_frac", "strategy", "relation"]).fraction.agg(["mean", "std"]).reset_index()
    composition.to_csv(ROOT / "report/E_edge_type_composition.csv", index=False, lineterminator="\n")

    # Re-render A's existing measurements with the shared visual style.
    a = pd.read_csv(ROOT / f"results/ws1/{gid}__random.csv")
    for name, data in [("fig_degree_dist", pd.read_csv(ROOT / f"data/processed/{gid}/node_features.csv")),
                       ("fig_S_random_edge", a), ("fig_S_random_node", a)]:
        fig = render(name, data)
        save(fig, "act0", name, output_dir=assets)
        plt.close(fig)

    # B's result labels are mapped explicitly; no theory curve is fabricated.
    b = pd.read_csv(ROOT / f"results/{gid}/ws2_attack_results_long.csv")
    b["strategy"] = b.strategy.map({"random": "node_random", "degree": "node_degree", "betweenness": "node_betweenness"})
    if b.strategy.isna().any():
        raise ValueError("Unexpected B strategy names")
    # B stores ranking-construction seeds (0/42) on fixed attack trajectories.
    # Map those rows to the shared deterministic convention in this plotting copy.
    b.loc[b.strategy.isin(["node_degree", "node_betweenness"]), "seed"] = -1
    setup()
    plt.rcParams.update({"font.size": 10, "xtick.labelsize": 9, "ytick.labelsize": 9})
    fig, ax = plt.subplots(figsize=(5.6, 3.9), layout="constrained")
    for strategy in ("node_random", "node_degree", "node_betweenness"):
        draw(ax, b, strategy, "gcc_frac", style={**STYLE[strategy], "marker": None})
    ax.set(xlabel="Fraction removed f", ylabel="GCC fraction", xlim=(0,1))
    legend(fig, [ax])
    save(fig, "act0", "fig_B_attack", output_dir=assets)
    plt.close(fig)
    hubs = pd.read_csv(ROOT / f"results/{gid}/ws2_hub_composition.csv")
    hubs["strategy"] = hubs.ranking.map({"degree":"node_degree", "betweenness":"node_betweenness"})
    hubs = hubs.rename(columns={"top_fraction":"top_frac"})
    index = pd.MultiIndex.from_product([("node_degree","node_betweenness"),(.01,.05,.1),
                                       ("drug","disease","gene/protein")],names=["strategy","top_frac","node_type"])
    hubs = hubs.set_index(["strategy","top_frac","node_type"])[["fraction"]].reindex(index, fill_value=0).reset_index()
    fig = render("fig_hub_composition", hubs)
    save(fig, "act0", "fig_B_hubs", output_dir=assets)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(4.5, 3.9), layout="constrained")
    bottom = np.zeros(2)
    for typ, color, label in [("drug","#3B8DB5","Drug"), ("disease","#D97B7B","Disease"),
                              ("gene/protein","#9DA8BA","Protein")]:
        subset = hubs[(hubs.top_frac == .01) & (hubs.node_type == typ)].set_index("strategy")
        values = subset.loc[["node_degree","node_betweenness"],"fraction"].to_numpy()
        ax.bar([0,1], values, bottom=bottom, width=.55, color=color, label=label)
        bottom += values
    ax.set_xticks([0,1],["Degree","Betweenness"])
    ax.set(ylabel="Fraction of top 1% nodes", ylim=(0,1.03))
    legend(fig,[ax])
    save(fig,"act0","fig_B_hubs_top1",output_dir=assets)
    plt.close(fig)

    c = pd.read_csv(ROOT / f"results/ws3/{gid}__retrieval.csv")
    c50 = c[(c.frac_removed == .5) & (c.strategy == "edge_random")]
    c_means = c50.groupby("metric").value.mean().to_dict()
    scan_means = c50[c50.seed.isin([0,1,2])].groupby("metric").value.mean().to_dict()
    b50 = b[(b.frac_removed == .5) & (b.metric == "gcc_frac")].groupby("strategy").value.mean().to_dict()
    a50 = a[(a.frac_removed == .5) & (a.strategy == "edge_random") & (a.metric == "gcc_frac")].value.mean()
    evidence = dict(gid=gid, n_nodes=len(nodes), n_edges=len(edges), n_queries=len(queries),
                    n_train=len(train), n_test=len(queries)-len(train),
                    A_edge_GCC_f50=float(a50), B_node_GCC_f50=b50,
                    C_R_f50=c_means, C_matched_three_seed_R_f50=scan_means,
                    E_gain_pp_at_budget20=table[table.budget_frac == .2].to_dict("records"),
                    static_positive_candidates=diagnostic.groupby("damage_frac").positive_score_candidates.agg(["min","max","mean"]).reset_index().to_dict("records"),
                    static_max_positive_share_at_budget05=float(diagnostic[diagnostic.budget_frac == .05].positive_share.max()),
                    edge_composition_budget20=composition[composition.budget_frac == .2].to_dict("records"))
    (working / "evidence.json").write_text(json.dumps(evidence, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"static_positive_candidates": evidence["static_positive_candidates"],
                      "max_positive_share_at_5pct_budget": evidence["static_max_positive_share_at_budget05"],
                      "C_R_f50": c_means}, indent=2))


if __name__ == "__main__":
    main()
