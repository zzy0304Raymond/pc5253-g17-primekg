"""WS2 targeted node-attack experiments."""

import argparse
import numpy as np
import pandas as pd

from .common import (
    ROOT,
    load_edges,
    load_nodes,
    load_order,
)
from .percolation import nz_nodes, to_levels


def run_one_attack(gid, strategy, order, levels, seed=0):
    """Run one node-removal trajectory using the shared percolation engine."""
    nodes = load_nodes(gid)
    edges = load_edges(gid)

    n = len(nodes)
    uv = edges[["u", "v"]].to_numpy(dtype=np.int64)

    print(f"Running {strategy} on {gid} ...")

    nz = nz_nodes(
        n_nodes=n,
        edges_uv=uv,
        order=order,
    )

    # Use A's actual to_levels interface.
    df = to_levels(
        nz_out=nz,
        levels=levels,
        total=n,
        gid=gid,
        strategy=strategy,
        seed=seed,
    )

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Run WS2 targeted node-attack experiments."
    )

    parser.add_argument(
        "--gid",
        default="primekg_5000_bfs_v1",
        help="Processed graph ID.",
    )

    args = parser.parse_args()
    gid = args.gid

    # Record the network every 1% of node removal.
    levels = np.linspace(0.0, 1.0, 101)

    # ---------------------------------------------------------
    # 1. Random node-removal baseline: 10 fixed A replicates
    # ---------------------------------------------------------
    random_results = []

    for seed in range(10):
        order = load_order(gid, f"node_random_s{seed}")

        df = run_one_attack(
            gid=gid,
            strategy="random",
            order=order,
            levels=levels,
            seed=seed,
        )

        random_results.append(df)

    random_all = pd.concat(random_results, ignore_index=True)

    # ---------------------------------------------------------
    # 2. Degree-targeted attack
    # ---------------------------------------------------------
    degree_order = load_order(gid, "node_degree")

    degree_df = run_one_attack(
        gid=gid,
        strategy="degree",
        order=degree_order,
        levels=levels,
        seed=0,
    )

    # ---------------------------------------------------------
    # 3. Betweenness-targeted attack
    # ---------------------------------------------------------
    betweenness_order = load_order(gid, "node_betweenness")

    betweenness_df = run_one_attack(
        gid=gid,
        strategy="betweenness",
        order=betweenness_order,
        levels=levels,
        seed=42,
    )

    # ---------------------------------------------------------
    # 4. Combine raw long-format results
    # ---------------------------------------------------------
    all_results = pd.concat(
        [random_all, degree_df, betweenness_df],
        ignore_index=True,
    )

    out_dir = ROOT / "results" / gid
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_path = out_dir / "ws2_attack_results_long.csv"
    all_results.to_csv(raw_path, index=False)

    # ---------------------------------------------------------
    # 5. Extract GCC fraction S(f)
    # ---------------------------------------------------------
    gcc = all_results[
        all_results["metric"] == "gcc_frac"
    ].copy()

    # Average the 10 random replicates.
    random_gcc = (
        gcc[gcc["strategy"] == "random"]
        .groupby("frac_removed", as_index=False)["value"]
        .mean()
        .rename(columns={"value": "random_mean"})
    )

    degree_gcc = (
        gcc[gcc["strategy"] == "degree"]
        [["frac_removed", "value"]]
        .rename(columns={"value": "degree"})
    )

    betweenness_gcc = (
        gcc[gcc["strategy"] == "betweenness"]
        [["frac_removed", "value"]]
        .rename(columns={"value": "betweenness"})
    )

    comparison = (
        random_gcc
        .merge(degree_gcc, on="frac_removed")
        .merge(betweenness_gcc, on="frac_removed")
    )

    comparison_path = out_dir / "ws2_gcc_comparison.csv"
    comparison.to_csv(comparison_path, index=False)

    print(f"\nSaved raw WS2 results to: {raw_path}")
    print(f"Saved GCC comparison to: {comparison_path}")

    # ---------------------------------------------------------
    # 6. Print useful checkpoints
    # ---------------------------------------------------------
    checkpoints = [0.00, 0.01, 0.05, 0.10, 0.20, 0.50]

    print("\nGCC fraction S(f)")
    print("-" * 62)
    print(
        f"{'f':<8}"
        f"{'Random':>12}"
        f"{'Degree':>12}"
        f"{'Betweenness':>16}"
    )

    for frac in checkpoints:
        row = comparison[
            np.isclose(comparison["frac_removed"], frac)
        ].iloc[0]

        print(
            f"{frac:<8.2f}"
            f"{row['random_mean']:>12.4f}"
            f"{row['degree']:>12.4f}"
            f"{row['betweenness']:>16.4f}"
        )


if __name__ == "__main__":
    main()