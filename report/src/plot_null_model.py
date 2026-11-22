"""Figure for the degree-attack null models (run src.run_null_model first).

Run from the repository root: python -m src.plot_null_model primekg_5000_bfs_v1
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .common import ROOT
from .plotting import BAND_ALPHA, panel_label, save, setup

MODELS = (
    ("real", dict(color="#d62728", marker="^", label="PrimeKG (degree attack)")),
    ("rewire_2k", dict(color="#9472C4", marker="s", label="2K rewiring (keeps degree correlations)")),
    ("rewire_typed", dict(color="#E3AE53", marker="D", label="Typed rewiring (keeps typed degrees)")),
    ("rewire_full", dict(color="#3B8DB5", marker="o", label="Full rewiring (keeps degrees only)")),
)


def main(gid):
    setup()
    data = pd.read_csv(ROOT / "results" / "ws4" / f"{gid}__null_model_attack.csv")
    gcc = data[data.metric == "gcc_frac"]
    stats = gcc.groupby(["strategy", "frac_removed"]).value.agg(["mean", "std"]).reset_index()
    theory = stats[stats.strategy == "theory_attack"].set_index("frac_removed")["mean"]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), layout="constrained")
    for name, style in MODELS:
        part = stats[stats.strategy == name].set_index("frac_removed")
        x = part.index.to_numpy()
        mean = part["mean"].to_numpy()
        sd = part["std"].fillna(0).to_numpy()
        for ax, y in ((axes[0], mean), (axes[1], mean - theory.loc[x].to_numpy())):
            if name != "real":
                ax.fill_between(x, y - sd, y + sd, color=style["color"], alpha=BAND_ALPHA, linewidth=0)
            ax.plot(x, y, color=style["color"], marker=style["marker"], ms=3.5,
                    label=style["label"] if ax is axes[0] else None)
    axes[0].plot(theory.index, theory.values, color="black", ls="--", label="GF theory (configuration model)")
    axes[1].axhline(0, color="black", ls="--", lw=1.2)
    axes[0].set(xlabel="Fraction of nodes removed f", ylabel="Giant component fraction S", xlim=(0, .7))
    axes[1].set(xlabel="Fraction of nodes removed f", ylabel="S − GF theory", xlim=(0, .5), ylim=(-.13, .02))
    panel_label(axes[0], "a")
    panel_label(axes[1], "b")
    fig.legend(loc="lower center", bbox_to_anchor=(.5, -.2), ncol=2, fontsize=9)
    save(fig, "act1", "fig_attack_null_model", output_dir=ROOT / "figures" / "act1" / gid,
         formats=("png", "pdf", "svg"))
    plt.close(fig)
    print("Saved fig_attack_null_model for", gid)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gids", nargs="*", default=["primekg_5000_bfs_v1"])
    for gid in parser.parse_args().gids:
        main(gid)
