"""Render the shared style using archived A/WS1 data, not fabricated results.

Run from the repository root: python -m scripts.preview_plotting --output-dir PATH
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

from src.common import ROOT
from src.plotting import STYLE, mean_sd, panel_label, save, setup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    setup()
    plt.rcParams.update({
        "font.size": 10, "axes.titlesize": 11,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "lines.linewidth": 1.5, "lines.markersize": 3.5,
        "axes.labelpad": 5, "axes.titlepad": 8,
    })
    gid = "primekg_5000_bfs_v1"
    source = ROOT / "results" / "ws1" / f"{gid}__random.csv"
    data = pd.read_csv(source)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.88, bottom=0.28, wspace=0.18)
    summaries = []
    for ax, kind, theory, letter in zip(
        axes, ("edge", "node"), ("theory_bond", "theory_site"), ("a", "b")
    ):
        strategy = f"{kind}_random"
        frame = data[(data.strategy == strategy) & (data.metric == "gcc_frac")]
        assert not frame.duplicated(["seed", "frac_removed"]).any()
        assert set(frame.seed) == set(range(10))
        agg = frame.groupby("frac_removed").value.agg(["mean", "std", "count"])
        assert (agg["count"] == 10).all()
        mean_sd(ax, agg.index, agg["mean"], agg["std"], strategy)
        reference = data[(data.strategy == theory) & (data.metric == "gcc_frac")].sort_values("frac_removed")
        ax.plot(reference.frac_removed, reference.value, **{
            **STYLE["theory"], "label": "GF reference", "lw": 1.1})
        ax.set(xlabel="Fraction removed f",
               title=f"Random {kind} removal", xlim=(-0.02, 1.02), ylim=(-0.03, 1.07))
        ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1])
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
        panel_label(ax, letter).set_fontsize(11)
        agg.reset_index().assign(strategy=strategy).to_csv(
            args.output_dir / f"preview_{kind}_summary.csv", index=False, lineterminator="\n")
        summaries.append({"panel": letter, "strategy": strategy, "n_seeds": 10,
                          "center": "mean", "spread": "sample SD, ddof=1"})
    axes[0].set_ylabel("GCC fraction")
    handles = [Line2D([], [], **{**STYLE[key], "label": label}) for key, label in
               (("edge_random", "Edge removal"), ("node_random", "Node removal"))]
    handles.append(Line2D([], [], color="black", ls="--", lw=1.1, label="GF reference"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.54, 0.025),
               ncol=3, columnspacing=2, fontsize=9)
    paths = save(fig, "style", "g17_style_preview", output_dir=args.output_dir,
                 formats=("png", "pdf", "svg"))
    plt.close(fig)
    metadata = {
        "purpose": "shared figure style preview using archived WS1 results",
        "source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "panels": summaries, "selection": "All gcc_frac rows for edge_random, node_random, theory_bond, theory_site.",
        "omissions": "Other metrics omitted because this preview demonstrates GCC curve styling only.",
        "theory": "A's ws1_theory_reference; not D's final theory module.",
        "exports": [str(path) for path in paths],
    }
    (args.output_dir / "g17_style_preview_provenance.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print("\n".join(map(str, paths)))


if __name__ == "__main__":
    main()
