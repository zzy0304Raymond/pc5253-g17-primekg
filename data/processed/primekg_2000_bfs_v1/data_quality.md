# primekg_2000_bfs_v1: data quality and scope

- Nodes: 2,000; semantic/structural edges: 32,468/32,468.
- Types: {'gene/protein': 1951, 'drug': 3, 'disease': 46}.
- Relations: {'disease_protein': 8904, 'drug_protein': 53, 'protein_protein': 23511}.
- Multiple-relation pairs: 0.
- Original GCC: 2,000; components: 1; isolates: 0.
- Proteins with PPI degree zero: 161; retain these proteins in C/D inputs.
- Query groups: {'single': 46, 'multi': 66}; query split: {'single_train': 30, 'single_test': 16, 'multi_train': 48, 'multi_test': 18}.
- Unique selected drug/disease endpoints: 3/46.
- Core data manifest SHA-256: `65a9a73d9083290f0d5fa000b51cc7f17640c91d4234e137b4be02f18e8923cc`.
- All selected queries have independently verified intact two-hop paths. Every random order is a complete seed-reproducible permutation.
- Structural validation covers both removal modes at five fractions; independent PPI reference fixtures are supplied where queries exist.

## Important limitation

Only three drugs occur in the prescribed BFS prefix. All 46 single and 66 multi queries are retained, so benchmark size is 112, not 200. Use for validation, not as an equivalent query sample to the standard graph.
