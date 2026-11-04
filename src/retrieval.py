"""Typed drug–protein–disease retrieval on a damaged PrimeKG graph."""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, dijkstra

from .common import effective_edge_mask, load_edges, load_nodes

COLUMNS = ["query_id", "drug_alive", "disease_alive", "s_alive", "d_ppi"]


class Retriever:
    """Reuse the original graph across evaluations of different damage masks."""

    def __init__(self, gid):
        nodes = load_nodes(gid)
        self.edges = load_edges(gid)
        self.n = len(nodes)
        types = nodes.node_type.to_numpy()
        relations = self.edges.relation.to_numpy()
        endpoints = self.edges[["u", "v"]].to_numpy(dtype=np.int64)
        self.ppi_ids = np.flatnonzero(relations == "protein_protein")
        self.ppi_edges = endpoints[self.ppi_ids]
        self.terminal_ids = np.flatnonzero(relations != "protein_protein")
        terminal_edges = endpoints[self.terminal_ids].copy()
        reverse = types[terminal_edges[:, 0]] == "gene/protein"
        terminal_edges[reverse] = terminal_edges[reverse, ::-1]
        self.terminal_edges = terminal_edges

    def evaluate(self, queries, edge_alive=None, node_alive=None, compute_dist=False):
        """Return one row per query. NaN means distance was not evaluated."""
        nodes = np.ones(self.n, dtype=bool) if node_alive is None else np.asarray(node_alive, dtype=bool)
        if nodes.shape != (self.n,):
            raise ValueError("node mask shape mismatch")
        mask = effective_edge_mask(self.edges, edge_alive, nodes)
        adjacency = {}
        for entity, protein in self.terminal_edges[mask[self.terminal_ids]].tolist():
            adjacency.setdefault(entity, set()).add(protein)

        if compute_dist:
            ppi = self.ppi_edges[mask[self.ppi_ids]]
            graph = csr_matrix((np.ones(len(ppi)), (ppi[:, 0], ppi[:, 1])),
                               shape=(self.n, self.n))
            graph = graph + graph.T
            _, labels = connected_components(graph, directed=False)
            distances = {}
            source_components = {}

        rows = []
        for query in queries:
            drug, disease = query["drug_nid"], query["disease_nid"]
            drug_alive, disease_alive = bool(nodes[drug]), bool(nodes[disease])
            targets = adjacency.get(drug, set())
            associated = adjacency.get(disease, set())
            shared = len(targets & associated)
            distance = np.nan
            if compute_dist:
                distance = np.inf
                if shared:
                    distance = 0.0
                elif targets and associated:
                    if drug not in source_components:
                        source_components[drug] = set(labels[list(targets)])
                    destinations = list(associated)
                    if source_components[drug].intersection(labels[destinations]):
                        if drug not in distances:
                            distances[drug] = dijkstra(
                                graph, directed=False, indices=sorted(targets),
                                unweighted=True, min_only=True,
                            )
                        distance = float(distances[drug][destinations].min())
            rows.append((query["query_id"], drug_alive, disease_alive, shared, distance))
        return pd.DataFrame(rows, columns=COLUMNS)
