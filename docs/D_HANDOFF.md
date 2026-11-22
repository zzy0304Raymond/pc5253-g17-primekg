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

## Report stage (22 Nov)

Done: report Sections 3 and 6, the abstract, the findings list in Section 1, the D parts of Section 8 and the appendix, and `report/D_individual_contribution_draft.md`.

New code and results:

| Content | Location |
|---|---|
| Degree-attack null models (full, typed and 2K rewiring) | `src/run_null_model.py`, `src/plot_null_model.py`, `tests/test_null_model.py` |
| Null-model results | `results/ws4/{gid}__null_model_{attack,stats,summary,provenance}.*`, `figures/act1/{gid}/fig_attack_null_model.*` |
| Minimum cut, uncertainty, restoration prediction | `src/run_ws4_report.py`, `results/ws4/{gid}__{mincut_per_query,mincut_Linf,uncertainty,restoration_prediction}.csv` |

Main new results on `primekg_5000_bfs_v1`:

- Edge connectivity between drug and disease equals the smaller endpoint degree for all 200 queries. The L = infinity "min-cut form" 1 - G_lambda(1 - p) is within 0.005 of 600 fresh orders up to f = 0.80.
- The seed SD of R_2 (0.047 at f = 0.5) is 2.2 times the variance expected for 200 independent queries, because queries share drug edges. That makes about 90 effective queries.
- The formula predicts all 12 of E's random and relation-type L = 2 repair gains within one seed SD.
- Degree attack gap to GF theory at f = 0.30 (0.102): about 10% comes from the simple-graph constraint, 39% from degree correlations (2K) and 51% from structure beyond 2K.

## Final restructure (22 Nov, evening)

An independent review graded the integrated report B+ and identified: a headline built on an exact identity, no single storyline, leftover workstream language, mixed seed sets for the same quantity, and BFS-sample artefacts presented as PrimeKG properties. The report was rewritten as one argument (23 pages instead of 36; see `report/README_LATEX.md`).

New analyses (`src/run_ws4_v2.py`, `src/plot_summary.py`):

- Connectivity far from threshold is local: for f <= 0.8, S matches 1 - g0(1 - p), the fraction of nodes keeping an edge, within 0.001. Collective behaviour appears only beyond f = 0.95.
- One principle: S, R_inf and R_2 are each 1 - PGF of a redundancy distribution (degree, min cut, shared proteins), with P(=1) = 2.0%, 21.5% and 50%.
- Full filtered graph: assortativity -0.053 (sample -0.153); neighbours of degree <= 3 nodes have mean degree 209 (sample 486; uncorrelated 190); 53% of drugs single-target (sample 69%); degree attack falls up to 0.06 below Callaway (sample 0.11).
- Null-model mixing: 9-14% of edges unchanged, hubs keep 20-29% of neighbours; transitivity 0.069 real vs 0.051-0.070 rewired. Gap shares stable for f = 0.1-0.4.
- Paired t-tests for repair: relation type beats edge betweenness at a 20% budget for L = 2 (p = 0.006 and 0.002); not at 5%; edge betweenness best at L = 3.
- Restoration predictions exceed measurements in 11 of 12 cases by at most 1.5 SE, consistent with the ten damage orders' test-set baseline (42.3%) exceeding the expected 40.2%.

## Third review and external validation (22 Nov, night)

A third independent review (B+ as framed) found that the headline was close to obvious far from p_c, that several "predictions" were identities (Eq. 10 under a deterministic ranking, the repair predictions), that limited-path percolation does have a closed form, and that the benchmark had no ground truth. Changes:

- `src/run_ws6_indications.py`: PrimeKG's 6,233 in-graph approved indications (never part of the filtered graph) against degree-preserving decoys on the full graph. Two-hop path: 31.0% vs 14.2% (ratio 2.18, drug-bootstrap 95% CI 1.92-2.47); L = 3: 1.26; L = 4: 1.01; unlimited: 1.00. Configuration-model decoy rate 13.1% at L = 2. Hub share of shared proteins: decoys 45%, indications 24%. Degree attack on 1% of nodes raises the ratio from 2.2 to 4.0.
- `src/run_ws7_horizon_attack.py`: size-biased mean field h = sum_H kD kY / sum kD kY predicts route survival 0.477 vs 0.462 (5% degree attack, sample) and 0.351 vs 0.370 (10%); worse at 1-2% and for betweenness. Real indications avoid hubs (27% of routes cut vs 44% predicted at 1%). Limited-path threshold (Lopez et al. 2007) matches the sample (0.825/0.927 vs 0.810/0.921) but not the full graph (0.63/0.85), where pairs have median 5 three-hop paths instead of 37.5.
- Figure 1 now shows the full graph with real indications; the sample summary moved to Section 4. Title: "Connected but Out of Reach".

## Fourth review and restructure (22 Nov, late)

A fourth independent review (A-, close to B+) asked for the real-data result to come first, fewer overclaims, and quantitative predictions. Changes:

- Order is now: introduction, data, theory, specificity on the full graph, hubs and attacks, controlled tests on the sample, discussion; uncertainty and repair moved to appendices.
- `src/run_ws8_chance_hubs.py`: a bundled chance-path null (drug's real targets and PPI ball, random disease links) predicts decoy rates 13.4/49.2/95.3% against 14.2/48.3/94.9% observed at L = 2/3/4. Count-based scores add little (AUROC 0.53-0.54 among pairs without a shared protein). Full-graph 5% degree attack: of 82.8 points of two-hop loss, 43.6 come from lost (mostly hub-disease) endpoints and 39.2 from routes. Two-factor mean-field test: with the indications' own route hub share the mean field is within 0.033; the graph-wide version fails because indications avoid hubs. Protein-only attack raises the indication/decoy ratio from 2.18 to 3.87 and information from 29.6 to 41.0 mbit while recall falls to 21.3%.
- The information decay under random damage is predicted by Eq. (6) within 1 mbit (L = 2) and by the independent-path estimate within 1.4 mbit (L = 3).
- Limited-path percolation is now reported as a negative result.

## Perspective (22 Nov, final)

Title changed to "Connected but Out of Reach: Robustness, Specificity and the Hop Limit in a Biomedical Knowledge Graph"; title page shows "Group 17". Section 7.1 now states the report's stance: the hop limit acts as a resolution (Figure 8, robustness-information frontier from `src/plot_ws6.py:frontier`), and Table 6 maps the measurement choices debated for neuronal avalanches and SOC (time bin, threshold, subsampling, time-scale separation) onto hop limit, null model, BFS sampling and independent deletion, each with its measured effect in this report.

## Final tightening (22 Nov, last)

After a fifth review the report was cut from 29 to 22 pages: no table of contents; Figure 2 (redundancy CCDF), the sample attack bar chart, the attack-penalty split and the appendix figures removed; uncertainty analysis folded into Section 6.1; repair and reproducibility appendices condensed. "Predicts" is now reserved for models that can fail (chance-path nulls, mean field, Callaway, limited-path threshold); Eqs. (6)-(7) "give" or "account for" results. New controls (`src/run_ws8_chance_hubs.py:controls`): two-hop decoys have 51% of routes cut by a 1% degree attack against 27% for indications; removing 619 random proteins leaves the ratio at 2.17; a 1/k-weighted score gives AUROC 0.591 against 0.586; odds ratios 2.71/1.68/1.35 at L = 2/3/4. Short first-person passages record what the team expected and got wrong (percolation collapse, the presentation question, the BFS artefact).

## Last additions (22 Nov)

- Effective excess r_L from 1 - R_real = (1 - R_chance)^{r_L} (Eq. excess; `src/run_ws8_chance_hubs.py:excess_by_horizon`): r_L - 1 = 1.42, 0.43, 0.10 (+-0.03) at L = 2, 3, 4 in the intact graph; framed as an analogy to an irrelevant perturbation under coarse-graining, explicitly not an RG calculation. Figure 7b.
- Teammates' query schematic (figures/act0/fig_query_schematic) now appears as Figure 2.
