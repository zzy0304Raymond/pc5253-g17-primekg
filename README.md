# G17 — PrimeKG structural and functional robustness

The governing specification is `G17_Work_Plan.md`. The repository includes A's shared data and random-failure analysis, B's centrality and targeted attacks, C's retrieval experiments, and E's restoration and plotting tools. D's final theory module is pending.

Member entry points: `docs/WS2_targeted_attack.md` (B), `C_README.md` (C), and `docs/E_HANDOFF.md` (E). C's integration checks are recorded in `docs/C_INTEGRATION_REVIEW.md`.

## Start here

1. Read `docs/DATA_CONTRACT.md` before using any IDs, masks or metrics.
2. Use `primekg_5000_bfs_v1` for the principal slides, `primekg_2000_bfs_v1` for development. `toy_v1` is synthetic. `primekg_full_v1` is for structural comparisons and has no defined query benchmark.
3. Run `python -m src.validate_data primekg_5000_bfs_v1` to verify content and frozen hashes.
4. Read `docs/HANDOFF.md` for B/C/D/E entry points and pending integration decisions.

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

## Theory and plot integration

Until D supplies `src/theory.py`, WS1 explicitly uses `src/ws1_theory_reference.py` (A's configuration-model reference, not D approval). Switch with:

```powershell
python -m src.run_ws1 primekg_5000_bfs_v1 --theory-module src.theory
```

When E supplies `src/plotting.py`, the plotter uses its `setup()`. Until then it uses the exact font, colors and dimensions in the work-plan appendix. Plot export remains relative to the repository root and includes PNG and PDF. No placeholder `theory.py`, `plotting.py`, `retrieval.py`, `centrality.py` or `restoration.py` is installed over another member's files.

## Main outputs

- `data/processed/{gid}/`: schema-compatible nodes, semantic edges, fixed queries, random orders, manifest and node features.
- `results/validation/`: graph audits, independent NetworkX structural checks, per-query reference values.
- `results/ws1/`: unified long tables and source/data provenance.
- `figures/act1/`: degree CCDF, edge/node percolation, fragmentation, full-vs-BFS comparison.
- `slides/`: A's two-slide handoff and speaking notes when generated.
- `report/`: data/protocol, random-failure results, reproducibility and individual contribution draft.

GF predictions are idealized configuration-model references; differences on an empirical finite graph are not automatically bugs. Query R refers to a selected positive-path benchmark, not all drug–disease pairs, and paths do not establish therapeutic efficacy.
