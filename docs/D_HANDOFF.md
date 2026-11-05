# D handoff: WS4 theory and prediction

Run from the repository root:

```bash
python -m src.run_ws4 primekg_5000_bfs_v1 primekg_2000_bfs_v1
python -m src.plot_ws4 primekg_5000_bfs_v1
python scripts/build_d_slides.py   # also needs python-pptx and Pillow
python -m unittest discover -s tests
```

## Files

| Content | Location |
|---|---|
| Analytic functions | `src/theory.py` |
| Per-query prediction | `src/prediction.py` |
| All WS4 experiments and checks | `src/run_ws4.py` |
| Figures | `src/plot_ws4.py`, `figures/act2/{gid}/`, `figures/act1/{gid}/fig_attack_theory.*` |
| Result tables | `results/ws4/` |
| Slides | `slides/D_slides_9-11.pptx`, `slides/G17_working_draft_with_D.pptx` |
| Speaker notes and theory Q&A | `slides/D_speaker_notes.md` |

## Main results on `primekg_5000_bfs_v1`

| Question | Result |
|---|---|
| Two-hop formula, random edges and nodes | Within 0.0011 of the mean over 5,000 fresh damage orders |
| Which query fails, random edges | AUC 0.713 / 0.720 for the formula, 0.712 / 0.712 for logistic regression, at 30% / 50% damage |
| Penalty at 5% degree attack | 57.4 pp: 17.4 pp lost endpoints, 40.0 pp lost paths (average of both orders) |
| Penalty at 5% betweenness attack | 63.9 pp: 17.0 pp lost endpoints, 47.0 pp lost paths (average of both orders) |
| Hop limit starts to bind | About 10%, 50%, 85% edge loss for L = 2, 3, 4 (600 fresh orders) |
| L = infinity formula | Within 0.009 of the mean over 600 fresh orders |
| PPI threshold | Molloy-Reed estimate 0.0062 here, 0.0054 on the filtered full graph; not measured, because the scan stops at p = 0.01 |
| L = infinity failures | More than 90% have lost every terminal link at one end at every level; up to 90% edge loss, more than 90% are a drug with no surviving target |

## Differences from the plan

- **No sharp collapse at L = infinity.** The plan expected threshold behaviour near the PPI percolation point. The PPI giant component outlasts the drug target links on this benchmark, so "bottleneck moves" is the supported statement. Do not describe `fig_phase_diagram` as a phase transition.
- **Ten seeds are a small sample for hop limits.** They sit up to 6 pp from the long-run mean. `__hop_fresh_orders.csv` gives the long-run values: L = 3 at 50% loss is 84.5% with seeds 0-2, 81.9% with ten seeds and 79.2% over 600 fresh orders.
- **Hop scan uses all ten seeds.** It took seconds through C's unchanged Retriever. C's seeds 0-2 results and slide 8 are unchanged, so slide 11 differs slightly from slide 8.
- **`fig_phase_diagram` uses f on the heatmap**, following the work plan's shared x-axis rule rather than the template's p axis.
- **Additions beyond the plan:** the endpoint/path split of the penalty, `failure_channels`, `hop_fresh_orders`, `fig_ppi_giant`, and cross-validated prediction under attack, which is exploratory.
- **WS1 stored results were not rerun**, because D's module matches A's reference to within 1e-12.

## Changes to other members' slides

In `slides/G17_working_draft_with_D.pptx` only:

- Slide 4: speaker note no longer says the GF curve is pending.
- Slide 5: attack figure replaced by `fig_attack_theory`, which adds the theory line, and the speaker note updated.
- Slide 14: speaker note no longer says D's pages are pending.

## Still to do for the report

Section 3 (theory), section 6 (prediction), the degree-attack null-model test with B, and the individual report.
