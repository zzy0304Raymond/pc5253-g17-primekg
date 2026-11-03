"""Render one template from supplied CSVs; no result generation or demo fallback."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.figure_templates import CATALOG, render
from src.plotting import save


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("template", choices=CATALOG)
    p.add_argument("--csv", type=Path, nargs="+")
    p.add_argument("--gid")
    p.add_argument("--damage", type=float, help="Filter frac_removed; e.g. equal-damage comparison")
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    data = pd.concat([pd.read_csv(path) for path in a.csv], ignore_index=True) if a.csv else None
    before = len(data) if data is not None else 0
    if a.gid:
        if data is None or "gid" not in data:
            p.error("--gid requires a gid column")
        data = data[data.gid == a.gid]
    if a.damage is not None:
        if data is None or "frac_removed" not in data:
            p.error("--damage requires a frac_removed column")
        data = data[data.frac_removed == a.damage]
    fig = render(a.template, data)
    demo = data is not None and "demo_only" in data and data.demo_only.astype(str).str.lower().eq("true").any()
    if demo or (data is not None and "gid" in data and data.gid.eq("DEMO_ONLY").any()):
        fig.suptitle("DEMO · synthetic values", fontsize=11)
    paths = save(fig, "templates", a.template, output_dir=a.output_dir, formats=("png", "pdf", "svg"))
    plt.close(fig)
    metadata = {"template": a.template, "inputs": [str(path) for path in (a.csv or [])],
                "filters": {"gid": a.gid, "frac_removed": a.damage},
                "rows_before_filter": before, "rows_after_filter": len(data) if data is not None else 0,
                "uncertainty": "sample SD across equal seed sets (ddof=1); seed=-1 is deterministic",
                "recovery": "paired gain relative to each seed's zero budget; efficiency per 1000 restored edges",
                "demo_only": bool(demo),
                "outputs": [str(path) for path in paths]}
    (a.output_dir / f"{a.template}__plot_metadata.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print("\n".join(map(str, paths)))


if __name__ == "__main__":
    main()
