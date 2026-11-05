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
| Two-hop formula, random edges and nodes | Within 0.001 of the mean over 5,000 fresh damage orders |
| Which query fails, random edges | AUC 0.713 / 0.720 for the formula, 0.712 / 0.712 for logistic regression, at 30% / 50% damage |
| Penalty at 5% degree attack | 57.4 pp: 23.6 pp lost endpoints, 33.8 pp lost paths |
| Penalty at 5% betweenness attack | 63.9 pp: 24.6 pp lost endpoints, 39.3 pp lost paths |
| Hop limit starts to bind | About 10%, 50%, 80% edge loss for L = 2, 3, 4 |
| L = infinity formula | Within 0.062 of the ten-seed mean |
| PPI threshold | p_c = 0.0062 here, 0.0054 on the filtered full graph |
| L = infinity failures | More than 92% have lost a terminal link, at every damage level |

## Differences from the plan

- **No sharp collapse at L = infinity.** The plan expected threshold behaviour near the PPI percolation point. The PPI giant component outlasts the terminal links, so "bottleneck moves" is the supported statement. Do not describe `fig_phase_diagram` as a phase transition.
- **Hop scan uses all ten seeds.** It took seconds through C's unchanged Retriever. C's seeds 0-2 results and slide 8 are unchanged, so slide 11 differs slightly from slide 8.
- **`fig_phase_diagram` uses f on the heatmap**, following the work plan's shared x-axis rule rather than the template's p axis.
- **Additions beyond the plan:** the endpoint/path split of the penalty, `failure_channels`, `fig_ppi_giant`, and cross-validated prediction under attack, which is exploratory.
- **WS1 stored results were not rerun**, because D's module matches A's reference to within 1e-12.

## Changes to other members' slides

In `slides/G17_working_draft_with_D.pptx` only:

- Slide 4: speaker note no longer says the GF curve is pending.
- Slide 5: attack figure replaced by `fig_attack_theory`, which adds the theory line, and the speaker note updated.

## Still to do for the report

Section 3 (theory), section 6 (prediction), the degree-attack null-model test with B, and the individual report.
