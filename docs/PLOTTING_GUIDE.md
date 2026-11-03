# G17 shared plotting guide

E maintains `src/plotting.py`. Use the project's Python 3.11 environment and
run module commands from the repository root. Text files use UTF-8.

## Minimal usage

```python
import matplotlib.pyplot as plt
from src.plotting import setup, STYLE, mean_sd, panel_label, save

setup()
fig, ax = plt.subplots()
mean_sd(ax, x, means, sample_sd, "edge_random")
ax.set(xlabel="Fraction removed f", ylabel="Largest component / original N")
ax.legend()
fig.tight_layout()
save(fig, "act1", "my_figure")
plt.close(fig)
```

`x`, `means` and `sample_sd` are arrays computed from your actual experiment.
Group by each damage level and compute sample SD across seeds (`ddof=1`).
Do not treat queries as independent seed repeats. For deterministic results:
`ax.plot(x, values, **STYLE["node_degree"])`, with no fabricated uncertainty.

## Conventions

- White background, Arial, 12 pt default, 6 × 4 inch single panel, 300 dpi PNG.
- Use `panel_label(ax, "a")` for multi-panel figures. Scale figure dimensions
  to fit readable labels; use shared legends where appropriate.
- Existing experiment colors match Work Plan appendix C. New restoration keys:
  `restore_random` (gray), `restore_edge_betweenness` (blue),
  `restore_relation_type` (gold), `restore_task_aware` (purple).
- Use `NODE_COLORS` for node types and `HEATMAP` for sequential heatmaps.
  For bounded success fractions, fix heatmap limits to 0 and 1 across panels.
- Light SD bands use alpha 0.16. No smoothing or clipping is applied by the helper.
- For bar charts, use the matching strategy color and show seed SD with `yerr`.
- Theory uses a black dashed line; identify the actual model in the caption.
- Recovery x-axis: fraction of **removed** edges restored. Report actual counts.
  Recovery gain: compute the before/after difference within each seed first,
  then summarize those paired gains across seeds.
- `save(fig, act, name)` creates `figures/{act}` under the repository root,
  even when called from another working directory. It exports PNG and PDF.
  Add editable SVG with `formats=("png", "pdf", "svg")`.

These defaults apply when called; existing member scripts with hardcoded colors
or grids must use these constants explicitly. E's tool does not rewrite A-D code.

## Preview

```powershell
python -m scripts.preview_plotting --output-dir D:/path/to/previews
```

The output directory is created automatically. The preview uses archived A/WS1
curves in a clean two-panel layout, not simulated WS5 measurements.
Its source hash and seed definition are
recorded alongside PNG, PDF, SVG and summary CSVs.
