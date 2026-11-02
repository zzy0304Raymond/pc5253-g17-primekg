# primekg_full_v1: data quality and scope

- Nodes: 30,968; semantic/structural edges: 426,954/426,954.
- Types: {'gene/protein': 19093, 'drug': 6282, 'disease': 5593}.
- Relations: {'disease_protein': 80411, 'drug_protein': 25468, 'protein_protein': 321075}.
- Multiple-relation pairs: 0.
- Original GCC: 30,921; components: 23; isolates: 0.
- Proteins with PPI degree zero: 739; retain these proteins in C/D inputs.
- Query groups: {}; query split: {}.
- Unique selected drug/disease endpoints: 0/0.
- Core data manifest SHA-256: `55b3b75b0d8e02f669b43787dd4ac933a4ac2b875e7f6aef64f9f8b65858821f`.
- All selected queries have independently verified intact two-hop paths. Every random order is a complete seed-reproducible permutation.
- Structural validation covers both removal modes at five fractions; independent PPI reference fixtures are supplied where queries exist.

## Scope limitation

Structural comparison only. queries.json=[] is intentional; no retrieval benchmark is defined and R must not be reported as zero.
