# 1. Introduction and motivation

Knowledge graphs organize entities and their relationships into a network that can support queries across several connected facts. In biomedicine, a question connecting a drug with a disease may involve proteins associated with both endpoints. PrimeKG provides a multimodal graph linking biomedical entities for precision-medicine analyses ([Chandak et al., 2023](https://doi.org/10.1038/s41597-023-01960-3)). Such a graph makes it possible to study how losing entities or relations changes access to particular association paths.

Complex-network research examines robustness by removing nodes or edges and measuring the surviving connected structure. Random failures and targeted attacks can produce different connectivity trajectories ([Albert et al., 2000](https://doi.org/10.1038/35019019)). For a knowledge graph, however, a retrieval task imposes additional conditions on the paths that count as useful. The largest connected component may contain most of the original vertices while the specific relation pattern required by a query has disappeared. A structural measure and a semantic query therefore need not respond in the same way to the same damage.

We study this relationship on a shared PrimeKG-derived graph containing drugs, diseases and proteins. A two-hop query succeeds when at least one protein retains both its drug and disease relations. Extending the horizon to three hops allows one protein–protein interaction between the terminal proteins. This controlled definition connects the functional metric directly to the available relations. It also provides a way to ask whether the importance of an edge changes when a task can use a longer route.

Our experiments combine random failure, targeted removal, retrieval evaluation and limited-budget restoration. All workstreams use fixed graph IDs, query definitions and removal orders so that structural and functional measurements can be compared on matching damaged states. The principal graph contains 5,000 nodes and 117,891 semantic edges. Its 200 selected queries all have an intact two-hop path. The smaller 2,000-node graph supports development, while the filtered full graph provides structural context for the sampled network.

The restoration experiment asks which deleted relations should receive a limited repair budget. We compare random selection, original edge betweenness, a relation-type control and a static score based on unsuccessful training queries. The relation-type control separates gains from restoring terminal relations from gains due to selecting particular task-relevant edges. We evaluate restored connectivity and held-out query success at two query horizons. Together, these measurements test how repair performance depends on the network structure, the query definition and the available budget.

The functional outcome is the availability of typed association paths in a selected positive-query benchmark. Its interpretation is bounded by the BFS sampling procedure and the query construction. Query-level training and test splits can share entities. These experiments address graph retrieval reliability and do not establish therapeutic efficacy.

## References for integration

- Chandak, P., Huang, K. and Zitnik, M. *Building a knowledge graph to enable precision medicine*. Scientific Data 10, 67 (2023). https://doi.org/10.1038/s41597-023-01960-3
- Albert, R., Jeong, H. and Barabási, A.-L. *Error and attack tolerance of complex networks*. Nature 406, 378–382 (2000). https://doi.org/10.1038/35019019
