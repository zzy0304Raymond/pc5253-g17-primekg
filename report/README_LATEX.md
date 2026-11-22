# PC5253 G17 final report (LaTeX)

Build with `latexmk -pdf main.tex` from this directory. Figures are resolved from `../figures/`.

## Structure (final version, 22 Nov, after five independent reviews; 23 pages)

The report was restructured around the full graph and PrimeKG's approved indications; the BFS sample is a controlled testbed. Every member's results are kept (some moved to appendices), and the group agreed that D could edit all sections.

| File | Section |
|---|---|
| `sections/01_introduction.tex` | 1 Introduction; Figure 1 (full graph, real indications) |
| `sections/02_data_protocol.tex` | 2 Data, queries (indications and decoys; sample benchmark), damage |
| `sections/03_theory.tex` | 3 Theory: redundancy, GF connectivity, exact two-hop formula, chance paths, size-biased mean field, longer horizons |
| `sections/04_specificity.tex` | 4 Which paths carry evidence (full graph) |
| `sections/05_hubs_attack.tex` | 5 Hubs and targeted damage (full graph and sample) |
| `sections/06_sample_tests.tex` | 6 Controlled tests on the sample (connectivity, horizon, null models) |
| `sections/07_discussion.tex` | 7 Discussion, limitations, conclusion |
| `sections/appendix_repair.tex` | A Repair under a budget (exploratory, condensed) |
| `sections/appendix_reproducibility.tex` | B Reproducibility |

`sections/appendix_uncertainty.tex` is no longer included; its content was folded into Section 6.1.

No longer used by `main.tex` (content merged above): `04_blind_damage.tex`, `05_targeted_damage.tex`, `06_indications.tex`, `06_repair.tex`, `04_1_random_failures.tex`, `04_2_targeted_attacks.tex`, `05_functional_robustness.tex`, `06_prediction.tex`, `07_restoration.tex`, `08_discussion_conclusion.tex`.

Analysis code added for the final version: `src/run_ws6_indications.py` (needs `data/raw/kg.csv` from `scripts/download_data.py`), `src/run_ws7_horizon_attack.py`, `src/run_ws8_chance_hubs.py`, `src/plot_ws6.py`, `src/plot_appendix.py`; tests in `tests/test_ws6_ws7.py`. Outputs in `results/ws6/`, `results/ws7/`, `results/ws8/`, `figures/act6/`.

The `.md` and `.csv` files in this directory are earlier drafts and handoff records.
