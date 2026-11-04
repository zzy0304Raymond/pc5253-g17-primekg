# Member C individual report draft

**Name:** [Your name]

**Project:** PC5253 Group 17, functional robustness of PrimeKG retrieval

My assigned workstream was to measure whether the same drug–disease queries remained retrievable as nodes and edges disappeared. The C implementation provides a reusable retrieval interface that counts surviving shared-protein routes and, when requested, finds the shortest distance between the drug's target proteins and the disease's associated proteins. The batch experiment holds the query set fixed and uses A and B's removal orders. I use the per-query results to connect the structural measurements from A and B to the prediction work in D and the repair evaluation in E.

I checked the toy and 2,000-node cases against an independent NetworkX reference and verified that all intact-graph counts match the query metadata. On the 5,000-node graph, at 50% random edge loss, 98.2% of nodes remained in the largest component while only 43.3% of queries retained a two-hop path. Comparing hop limits on the same three seeds showed that allowing one protein–protein step raised mean retrieval success from 40.3% to 84.5% at this damage level. The results apply to the sampled graph and selected benchmark. The different seed sets used for the full edge-removal baseline and the hop scan explain why the two-hop averages differ.

The deliverables for this workstream include the retrieval interface for E, per-query and summary tables for D, four result figures, and the slides and report section for the team.
