# Reproducibility appendix — A

## Fixed source

- PrimeKG, Harvard Dataverse DOI: 10.7910/DVN/IXA7BM.
- File ID: 6180620; filename: kg.csv.
- Download: https://dataverse.harvard.edu/api/access/datafile/6180620 .
- Size: 981,751,236 bytes.
- Official MD5, verified: aac8191d4fbc5bf09cdf8c3c78b4e75f.
- SHA-256: 0a5a010fcd88dcec572a573d98c26c1c244a11567092b6161d3ded611cfb5c69.
- Source metadata and processing audit are in data/raw; raw CSV is excluded from the handoff archive and version control.

## Reproduction

Create a Python 3.11 environment and install requirements-lock.txt. In this workspace the interpreter is `.venv/Scripts/python.exe` (3.11.9). Run from the repository root:

```text
python -m unittest discover -s tests -v
python scripts/download_data.py
python scripts/run_a_pipeline.py
```

The downloader requires data/raw/dataverse_metadata.json; README gives the exact metadata download command. It supports resume and verifies each range response plus the official checksum. Pipeline stages refuse to overwrite frozen core graph files. To rebuild without existing outputs, use a fresh directory with the code and raw source, or a separate G17_ROOT. `scripts/check_reproducibility.py` demonstrates an isolated build and compares scientific-file hashes.

The final formal runs use Python 3.11.9 with requirements-lock.txt. Initial graph generation used Python 3.14.3; manifests preserve this history. Rebuilding under 3.11.9 reproduced nodes, edges, queries and random orders exactly: 68 scientific files match SHA-256. Environment fields and other descriptive metadata are not claimed byte-identical across interpreters. Source fingerprints in results/ws1/*__provenance.json connect each result to its data and algorithm.

## Determinism

Original node IDs are parsed as integers. BFS starts at original disease ID 32617 and visits neighbors in ascending ID order. The subgraph is induced. Nodes are assigned local IDs in ascending original-ID order. Edges are sorted by relation,u,v before assigning eid. Queries are sorted before independent seed-42 group permutations; selected index positions are re-sorted. The training split uses a separate default_rng(42) permutation. Damage seeds are 0–9 and masks use fixed permutation prefixes with round(f*total).

Cross-graph entity joins use x_index. Random orders belong to one gid and one ID universe. Library versions matter for sampled centrality; B should record them separately. A's frozen manifest excludes future B-owned centrality files and should not be rewritten to register them.

## Validation evidence

- results/validation/reproducibility.json: 68 byte-identical files and BFS prefix check.
- tests/test_percolation.py: all-state comparison on 80 small graphs, semantic duplicates, edge cases and input validation.
- tests/test_theory.py: exact 3-regular formula and isolated/empty degree cases.
- results/validation/{gid}__networkx_checks.csv: 10 real-graph states per gid, six counts per state.
- results/validation/{gid}__retrieval_reference.csv: independent semantic-path/distance reference for downstream consumers; not a claim that C's module has been tested.
- slides/A_slides_3_4.pptx: two editable slides with native charts and an editable table; the scientific PNG/PDF plots retain shaded SD bands, while the native slides show SD bounds.

## Limits and responsibilities

The full graph's queries.json is intentionally empty because this release defines only structural full-graph comparisons. It is not an R=0 dataset. The 2,000-node graph contains 112 queries and only three drugs. Report functions must handle actual group sizes. Query splits allow entity overlap.

The GF reference is A's isolated implementation pending D's final module. Use `--theory-module src.theory` when it arrives. E can supply plotting.py without changing scientific data. Full group integration, rehearsal, institutional submission and peer grading are not performed by these scripts.
