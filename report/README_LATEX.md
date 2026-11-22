# PC5253 G17 integrated LaTeX report

This directory integrates the existing member Markdown drafts into one LaTeX report.

- Existing `.md` and `.csv` files in the repository `report/` directory should be kept as source/handoff records.
- The final LaTeX assembly uses `main.tex` and `sections/*.tex`.
- Repository compilation expects this directory at `repository_root/report/`; figures are resolved from `../figures/`.
- The Overleaf preview bundle may also contain copies under `report/figures/`; these preview copies do not need to be committed to GitHub.
- Sections 3 (theory) and 6 (prediction), the abstract, the findings list at the end of Section 1, and the D parts of Section 8 and the appendix are complete. All numbers trace to `results/ws4/`.
- Build with `latexmk -pdf main.tex` from this directory.
