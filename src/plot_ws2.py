"""Plot final WS2 figures."""

import argparse
import matplotlib.pyplot as plt
import pandas as pd

from .common import ROOT


def plot_attack_curves(gid):
    result_dir = ROOT / "results" / gid
    figure_dir = ROOT / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(
        result_dir / "ws2_gcc_comparison.csv"
    )

    fig, ax = plt.subplots(figsize=(7.2, 5.0))

    ax.plot(
        df["frac_removed"],
        df["random_mean"],
        label="Random failure",
        linewidth=2.2,
    )

    ax.plot(
        df["frac_removed"],
        df["degree"],
        label="Degree attack",
        linewidth=2.2,
    )

    ax.plot(
        df["frac_removed"],
        df["betweenness"],
        label="Betweenness attack",
        linewidth=2.2,
    )

    ax.set_xlabel("Fraction of nodes removed")
    ax.set_ylabel("Giant component fraction $S(f)$")
    ax.set_title(
        "PrimeKG Robustness Under Node Removal"
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)

    ax.grid(alpha=0.25)
    ax.legend(frameon=False)

    fig.tight_layout()

    png_path = figure_dir / f"ws2_attack_curves_{gid}.png"
    pdf_path = figure_dir / f"ws2_attack_curves_{gid}.pdf"

    fig.savefig(png_path, dpi=300)
    fig.savefig(pdf_path)

    plt.close(fig)

    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")


def plot_hub_composition(gid):
    result_dir = ROOT / "results" / gid
    figure_dir = ROOT / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(
        result_dir / "ws2_hub_composition.csv"
    )

    # Convert to percentages for easier presentation.
    df["percent"] = 100 * df["fraction"]

    labels = {
        0.01: "Top 1%",
        0.05: "Top 5%",
        0.10: "Top 10%",
    }

    for ranking in ["degree", "betweenness"]:
        subset = df[df["ranking"] == ranking].copy()

        pivot = (
            subset
            .pivot(
                index="top_fraction",
                columns="node_type",
                values="percent",
            )
            .fillna(0)
            .reindex([0.01, 0.05, 0.10])
        )

        fig, ax = plt.subplots(figsize=(7.0, 4.8))

        pivot.plot(
            kind="bar",
            stacked=True,
            ax=ax,
        )

        ax.set_xticklabels(
            [labels[x] for x in pivot.index],
            rotation=0,
        )

        ax.set_xlabel("Centrality cutoff")
        ax.set_ylabel("Entity composition (%)")
        ax.set_ylim(0, 100)

        pretty_name = ranking.capitalize()

        ax.set_title(
            f"Entity Types Among Top {pretty_name} Nodes"
        )

        ax.legend(
            title="Node type",
            loc="upper left",
            bbox_to_anchor=(1.02, 1.0),
            frameon=False,
        )

        fig.tight_layout()

        png_path = (
            figure_dir /
            f"ws2_{ranking}_hub_composition_{gid}.png"
        )

        fig.savefig(png_path, dpi=300)
        plt.close(fig)

        print(f"Saved: {png_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Plot WS2 robustness and hub-composition results."
    )

    parser.add_argument(
        "--gid",
        default="primekg_5000_bfs_v1",
        help="Processed graph ID.",
    )

    args = parser.parse_args()
    gid = args.gid

    plot_attack_curves(gid)
    plot_hub_composition(gid)


if __name__ == "__main__":
    main()