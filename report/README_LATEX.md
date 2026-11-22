# PC5253 G17 final report (LaTeX)

Build with `latexmk -pdf main.tex` from this directory. Figures are resolved from `../figures/`.

## Structure (final version, 22 Nov)

After an independent review, the report was restructured into one argument. Every member's results are kept; only the organisation and wording changed.

| File | Section | Main sources |
|---|---|---|
| `sections/01_introduction.tex` | 1 Introduction, summary figure, contributions, beyond the course | all |
| `sections/02_data_protocol.tex` | 2 Data, benchmark, damage model; BFS-sample caveat | A |
| `sections/03_theory.tex` | 3 Theory: survival as redundancy | D |
| `sections/04_blind_damage.tex` | 4 Blind damage: connectivity, two-hop, horizon, uncertainty | A, C, D |
| `sections/05_targeted_damage.tex` | 5 Targeted damage: attacks, null models, retrieval penalty | B, D |
| `sections/06_repair.tex` | 6 Repair under a budget | E, D |
| `sections/07_discussion.tex` | 7 Discussion, limitations, conclusion | B, all |
| `sections/appendix_reproducibility.tex` | A Reproducibility; B Additional figures | A, B |

No longer used by `main.tex` (their content has been merged above): `04_1_random_failures.tex`, `04_2_targeted_attacks.tex`, `05_functional_robustness.tex`, `06_prediction.tex`, `07_restoration.tex`, `08_discussion_conclusion.tex`.

Numbering rule: expected values under blind damage are long-run means over independent damage orders (5,000 for two-hop, 600 for other hop limits); the ten fixed orders are used for stored damage states and to show spread.

The `.md` and `.csv` files in this directory are earlier drafts and handoff records.
