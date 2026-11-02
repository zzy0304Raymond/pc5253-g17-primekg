# primekg_5000_bfs_v1: data quality and scope

- Nodes: 5,000; semantic/structural edges: 117,891/117,891.
- Types: {'gene/protein': 4643, 'drug': 74, 'disease': 283}.
- Relations: {'disease_protein': 27228, 'drug_protein': 476, 'protein_protein': 90187}.
- Multiple-relation pairs: 0.
- Original GCC: 5,000; components: 1; isolates: 0.
- Proteins with PPI degree zero: 92; retain these proteins in C/D inputs.
- Query groups: {'single': 100, 'multi': 100}; query split: {'single_train': 68, 'single_test': 32, 'multi_train': 72, 'multi_test': 28}.
- Unique selected drug/disease endpoints: 39/127.
- Core data manifest SHA-256: `b067933d08ac95e3d432c8e2695a912d248cfdaccb7c112bfcbc4e8c51e16c96`.
- All selected queries have independently verified intact two-hop paths. Every random order is a complete seed-reproducible permutation.
- Structural validation covers both removal modes at five fractions; independent PPI reference fixtures are supplied where queries exist.

## Interpretation

The 200 selected queries are balanced positive-path tasks, not a random sample of all possible drug–disease pairs. BFS composition differs materially from the filtered full graph; see sampling comparison.
