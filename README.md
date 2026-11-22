# G17 — PrimeKG structural and functional robustness

The final group report is [`report/G17_final_report.pdf`](report/G17_final_report.pdf), with LaTeX source and build notes in [`report/`](report/README_LATEX.md). This repository contains the shared PrimeKG data pipeline, random-failure and targeted-attack analyses, typed retrieval experiments, theory and prediction, restoration, and the full-graph indication and specificity analyses. `G17_Work_Plan.md` records the original work plan; the final report describes the completed study.

Workstream notes: `docs/WS2_targeted_attack.md` (B), `C_README.md` (C), `docs/D_HANDOFF.md` (D), and `docs/E_HANDOFF.md` (E). C's integration checks are in `docs/C_INTEGRATION_REVIEW.md`.

## Start here

1. Read `docs/DATA_CONTRACT.md` before using any IDs, masks or metrics.
2. Use `primekg_5000_bfs_v1` for the controlled sample, `primekg_2000_bfs_v1` for development, and `primekg_full_v1` for the full graph. The final report also uses approved indications and degree-preserving decoys from the fixed PrimeKG source; `toy_v1` is synthetic.
3. Run `python -m src.validate_data primekg_5000_bfs_v1` to verify content and frozen hashes.
4. Read `report/README_LATEX.md` for the final report structure and its new analysis modules. Earlier handoff notes preserve the development history.

## Environment

The primary verified runtime is Python 3.11.9; exact dependency pins are in `requirements-lock.txt`. A local environment is available at `.venv/Scripts/python.exe`. Initial data construction also ran under Python 3.14.3; a clean 3.11 rebuild reproduced all 68 scientific data files byte-for-byte. Manifests retain the original construction environment; WS1 provenance records the final run environment.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python -m unittest discover -s tests -v
```

Commands below run from the repository root. `python -m src...` avoids ambiguous imports. `common` and `percolation` also support B's legacy `PYTHONPATH=src` imports. `G17_ROOT` can point to a separate dataset root; set it before importing modules.

## Reproduce from the fixed raw file

Raw CSV is not committed or included in the handoff ZIP. The data source is [PrimeKG](https://github.com/mims-harvard/PrimeKG); the exact protocol file is [Dataverse file 6180620](https://dataverse.harvard.edu/api/access/datafile/6180620). The downloader checks the official MD5 and records SHA-256.

```powershell
New-Item -ItemType Directory -Force data/raw
curl.exe --fail -sS -L 'https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/IXA7BM' -o data/raw/dataverse_metadata.json
python scripts/download_data.py
python scripts/run_a_pipeline.py
```

The downloader is Windows-oriented (`curl.exe`); on other systems replace it with `curl`, or download the fixed URL manually and create matching `source.json` using the recorded digest. The scientific modules are platform-independent.

The pipeline checks existing frozen data rather than modifying it. If source/protocol changes, use a new gid or an independent `G17_ROOT`; do not delete or overwrite an already shared version. Results can be regenerated from frozen data. Pipeline output includes complete full-graph edge and node runs, although the original plan made the full graph optional for slides.

## Individual stages

```powershell
python -m src.make_toy
python -m src.build_graph
python -m src.make_queries primekg_5000_bfs_v1
python -m src.make_orders primekg_5000_bfs_v1
python -m src.validate_data primekg_5000_bfs_v1 --freeze
python -m src.check_integration primekg_5000_bfs_v1
python -m src.run_ws1 primekg_5000_bfs_v1
python -m src.plot_ws1 primekg_5000_bfs_v1
```

Run individual generation stages only before a gid is frozen. The one-command pipeline is the normal entry point and handles already completed stages.

## Final analyses

`src/theory.py`, `src/plotting.py`, `src/retrieval.py`, `src/centrality.py`, and `src/restoration.py` are integrated. The full-graph analyses added for the final report use `src/run_ws6_indications.py`, `src/run_ws7_horizon_attack.py`, and `src/run_ws8_chance_hubs.py`; their stored results are in `results/ws6/`, `results/ws7/`, and `results/ws8/`. The first of these requires the fixed raw `kg.csv`, which the downloader obtains and checks. See `report/README_LATEX.md` and `docs/D_HANDOFF.md` for the analysis and figure entry points.

## Main outputs

- `data/processed/{gid}/`: schema-compatible nodes, semantic edges, fixed queries, random orders, manifest and node features.
- `results/validation/`: graph audits, independent NetworkX structural checks, per-query reference values.
- `results/ws1/`: unified long tables and source/data provenance.
- `results/primekg_*/` and `results/ws3/` through `results/ws8/`: targeted attacks, retrieval, theory, restoration, and full-graph analyses.
- `figures/act1/`: degree CCDF, edge/node percolation, fragmentation, full-vs-BFS comparison.
- `figures/act6/`: final full-graph indication, information, attack, and frontier figures.
- `slides/`: group presentation and speaker notes.
- `report/`: final PDF, LaTeX source, build notes, and earlier workstream drafts.

GF predictions are idealized configuration-model references; differences on an empirical finite graph are not automatically bugs. The 200-query sample benchmark was selected for positive two-hop paths; the final report separately analyzes approved indications and decoys on the full graph. A typed path does not by itself establish therapeutic efficacy.
