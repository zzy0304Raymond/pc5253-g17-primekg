"""Render E's restoration results; partial runs require an explicit flag."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from .figure_templates import render, draw, legend
from .plotting import save, setup, NODE_COLORS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run_dir", type=Path)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--allow-partial", action="store_true")
    a = p.parse_args()
    meta = json.loads((a.run_dir / "provenance.json").read_text(encoding="utf-8"))
    if meta["status"] != "complete":
        p.error("Only completed runs can be plotted")
    preliminary = meta["evaluator"] != "c" or bool(meta["missing_strategies"])
    if preliminary and not a.allow_partial:
        p.error("This is a local/reference or incomplete strategy run; use --allow-partial to label it explicitly")
    table = pd.read_csv(a.run_dir / f"{meta['gid']}__restoration.csv")
    paired = pd.read_csv(a.run_dir / f"{meta['gid']}__paired_gains.csv")
    for name in ("fig_restoration", "fig_gain_per_edge"):
        fig = render(name, table, restoration_strategies=tuple("restore_"+s for s in meta["strategies"]))
        if preliminary:
            fig.suptitle("Local check · independent evaluator · " + str(len(meta["strategies"])) + "/4 strategies", fontsize=10)
        save(fig, "act3", name, output_dir=a.output_dir, formats=("png", "pdf", "svg"))
        plt.close(fig)
    for metric in ("R_L2", "R_L3"):
        setup()
        plt.rcParams.update({"font.size": 11, "legend.fontsize": 9, "axes.titlesize": 11})
        fig, axes = plt.subplots(1, 2, figsize=(8, 3.6), layout="constrained")
        for ax, damage in zip(axes, meta["damages"]):
            frame = paired[(paired.damage_frac == damage) & (paired.metric == metric)].copy()
            frame["value"] = 100*frame.gain
            for strategy in meta["strategies"]:
                draw(ax, frame, "restore_"+strategy, metric, x="budget_frac")
            ax.set(title=f"{damage:.0%} edges removed", xlabel="Removed edges restored", ylabel="Success gain (pp)")
            ax.set_xticks([0,.05,.1,.2],["0%","5%","10%","20%"])
        if preliminary:
            fig.suptitle("Independent local evaluation · 3 strategies", fontsize=10)
        legend(fig, axes)
        save(fig, "act3", "fig_restoration_"+metric[2:], output_dir=a.output_dir, formats=("png","pdf","svg"))
        plt.close(fig)
    setup()
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 10, "xtick.labelsize": 8,
                         "ytick.labelsize": 8, "legend.fontsize": 8})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), layout="constrained")
    for ax, damage in zip(axes, meta["damages"]):
        for strategy in meta["strategies"]:
            draw(ax, table[table.damage_frac == damage], "restore_"+strategy, "gcc_frac", x="budget_frac")
        ax.set(title=f"{damage:.0%} edges removed", xlabel="Removed edges restored", ylabel="GCC fraction")
        ax.set_xticks([0,.05,.1,.2],["0%","5%","10%","20%"])
    if preliminary:
        fig.suptitle("Local check · " + str(len(meta["strategies"])) + "/4 strategies", fontsize=10)
    legend(fig, axes)
    save(fig, "act3", "fig_restoration_gcc", output_dir=a.output_dir, formats=("png","pdf","svg"))
    plt.close(fig)
    edge_types = pd.read_csv(a.run_dir / f"{meta['gid']}__restored_edge_types.csv")
    chosen_budget = max(meta["budgets"])
    composition = edge_types[edge_types.budget_frac == chosen_budget].copy()
    if (composition.n_restored <= 0).any():
        raise ValueError("Edge-type composition requires a positive actual restored count")
    composition["fraction"] = composition["count"] / composition.n_restored
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), layout="constrained", sharey=True)
    relation_styles = [("drug_protein", "Drug–protein", NODE_COLORS["drug"]),
                       ("disease_protein", "Disease–protein", NODE_COLORS["disease"]),
                       ("protein_protein", "Protein–protein", NODE_COLORS["gene/protein"])]
    for ax, damage in zip(axes, meta["damages"]):
        group = composition[composition.damage_frac == damage]
        for offset,(relation,label,color) in enumerate(relation_styles):
            values = group[group.relation == relation].groupby("strategy").fraction.agg(["mean","std"])
            values = values.loc[["restore_"+s for s in meta["strategies"]]]
            ax.bar(np.arange(len(values))+(offset-1)*.23, values["mean"], yerr=values["std"],
                   width=.21, color=color, label=label, error_kw={"lw": .7, "capsize": 2})
        labels = {"random":"Random", "relation_type":"Relation type", "task_aware":"Task-aware",
                  "edge_betweenness":"Betweenness"}
        ax.set_xticks(range(len(meta["strategies"])), [labels[s] for s in meta["strategies"]])
        ax.set(title=f"{damage:.0%} removed · {chosen_budget:.0%} budget", ylabel="Fraction of restored edges", ylim=(0,1.05))
    if preliminary:
        fig.suptitle("Local check · edge-type composition", fontsize=10)
    legend(fig, axes)
    save(fig, "act3", "fig_restored_edge_types", output_dir=a.output_dir, formats=("png","pdf","svg"))
    plt.close(fig)
    note = ("Recovery gains are paired within damage seed; mean ± sample SD. "
            "Budgets are fractions of removed edges. See summary CSV for actual restored counts. "
            "Relation-type strategy stops at candidate exhaustion; equal budget limits may mean unequal spend. "
            "Only test queries are evaluated. " + ("Local check; B/C integration pending." if preliminary else "C Retriever integrated."))
    (a.output_dir / "caption.txt").write_text(note+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
