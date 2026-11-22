"""Appendix figure: entity types among the most central nodes of the sample (redrawn).

Run from the repository root: python -m src.plot_appendix
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .common import ROOT, load_nodes, load_order
from .plotting import panel_label, save, setup

GID = "primekg_5000_bfs_v1"
TYPES = (("gene/protein", "Protein", "#9DA8BA"), ("disease", "Disease", "#3B8DB5"), ("drug", "Drug", "#D9822B"))


def main():
    setup()
    nodes = load_nodes(GID)
    types = nodes.node_type.to_numpy()
    cuts = (.01, .05, .10)
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.2), layout="constrained", sharey=True)
    rows = []
    for ax, (name, title) in zip(axes, (("node_degree", "Degree ranking"), ("node_betweenness", "Betweenness ranking"))):
        order = load_order(GID, name)
        x = np.arange(len(cuts) + 1)
        labels = [f"Top {int(100 * c)}%" for c in cuts] + ["All nodes"]
        shares = []
        for c in cuts:
            top = types[order[:int(round(c * len(types)))]]
            shares.append([np.mean(top == t) for t, _, _ in TYPES])
        shares.append([np.mean(types == t) for t, _, _ in TYPES])
        shares = np.array(shares)
        for j, (t, lab, col) in enumerate(TYPES):
            ax.bar(x + (j - 1) * .27, 100 * shares[:, j], width=.26, color=col, label=lab)
            for i, v in enumerate(shares[:, j]):
                ax.text(x[i] + (j - 1) * .27, 100 * v + 1.5, f"{100 * v:.1f}", ha="center", fontsize=6.5)
        for i, lab in enumerate(labels):
            rows.append(dict(ranking=name, subset=lab, **{t: shares[i, j] for j, (t, _, _) in enumerate(TYPES)}))
        ax.set_xticks(x, labels, fontsize=8.5)
        ax.set_title(title, fontsize=10.5)
    axes[0].set_ylabel("Share of nodes (%)")
    axes[0].set_ylim(0, 108)
    axes[1].legend(loc="upper right", fontsize=8, ncol=3)
    for a, lab in zip(axes, "ab"):
        panel_label(a, lab)
    save(fig, "act1", "fig_hub_composition", output_dir=ROOT / "figures" / "act1" / GID, formats=("png", "pdf"))
    plt.close(fig)
    pd.DataFrame(rows).to_csv(ROOT / "results" / "ws7" / "hub_composition.csv", index=False, lineterminator="\n")
    print(pd.DataFrame(rows).round(3).to_string())


if __name__ == "__main__":
    main()
