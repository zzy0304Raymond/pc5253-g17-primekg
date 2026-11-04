"""Export the four C figures using the team's shared plotting templates."""

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .common import ROOT
from .figure_templates import render
from .plotting import save
from .run_ws3 import SCAN_SEEDS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gid", nargs="?", default="primekg_5000_bfs_v1")
    gid = parser.parse_args().gid
    retrieval = pd.read_csv(ROOT / "results" / "ws3" / f"{gid}__retrieval.csv")
    structure = pd.read_csv(ROOT / "results" / "ws1" / f"{gid}__random.csv")
    edge_r = retrieval[retrieval.strategy == "edge_random"]
    s = structure[(structure.strategy == "edge_random") & (structure.metric == "gcc_frac")]
    r = edge_r[edge_r.metric == "R_L2"]
    keys = ["gid", "strategy", "seed", "frac_removed", "n_removed"]
    pairs = s.merge(r, on=keys, how="outer", indicator=True, validate="one_to_one")
    if not pairs._merge.eq("both").all():
        raise ValueError("WS1 and WS3 edge-random states must match by seed and removal count")
    hop_data = edge_r[edge_r.seed.isin(SCAN_SEEDS)]
    inputs = {
        "fig_S_vs_R": pd.concat([s, r], ignore_index=True),
        "fig_R_by_group": edge_r,
        "fig_R_L_curves": hop_data,
        "fig_R_L_heatmap": hop_data,
    }
    folder = ROOT / "figures" / "act2" / gid
    for name, data in inputs.items():
        fig = render(name, data)
        save(fig, "act2", name, output_dir=folder, formats=("png", "pdf", "svg"))
        plt.close(fig)
    print(f"Saved four figures in {folder}")


if __name__ == "__main__":
    main()
