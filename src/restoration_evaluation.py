"""E-owned independent edge-only checks; not a replacement src.retrieval module."""
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


def gcc_fraction(n_nodes, edges, edge_alive):
    if not n_nodes:
        return 0.0
    uv = edges.loc[edge_alive, ["u", "v"]].to_numpy()
    matrix = coo_matrix((np.ones(len(uv), dtype=bool), (uv[:, 0], uv[:, 1])),
                        shape=(n_nodes, n_nodes)).tocsr()
    _, labels = connected_components(matrix, directed=False)
    return float(np.bincount(labels).max() / n_nodes)


class EdgeRestorationReference:
    """Exactly check allowed L2/L3 paths after edge loss with all nodes retained.

    Deliberately does not expose C's Retriever interface or claim full PPI
    distances. L3 success allows zero or one surviving PPI edge.
    """
    def __init__(self, nodes, edges):
        self.n = len(nodes)
        self.edges = edges
        self.types = nodes.node_type.to_numpy()

    def evaluate(self, queries, edge_alive):
        adjacency = {}
        uv_ppi = []
        for u, v, relation in self.edges.loc[edge_alive, ["u", "v", "relation"]].itertuples(index=False, name=None):
            if relation == "protein_protein":
                uv_ppi.append((u, v))
                continue
            entity, protein = (v, u) if self.types[u] == "gene/protein" else (u, v)
            adjacency.setdefault(int(entity), set()).add(int(protein))
        ppi = [set() for _ in range(self.n)]
        for u, v in uv_ppi:
            ppi[u].add(v)
            ppi[v].add(u)
        rows = []
        for q in queries:
            a = adjacency.get(q["drug_nid"], set())
            b = adjacency.get(q["disease_nid"], set())
            count = len(a & b)
            l3 = bool(count) or any(ppi[p] & b for p in a)
            rows.append(dict(query_id=q["query_id"], s_alive=count,
                             success_L2=bool(count), success_L3=l3))
        return pd.DataFrame(rows, columns=["query_id", "s_alive", "success_L2", "success_L3"])


def evaluate_c(retriever, queries, edge_alive):
    """Validate and adapt C's contract to E's two bounded success indicators."""
    frame = retriever.evaluate(queries, edge_alive=edge_alive.copy(), compute_dist=True)
    needed = {"query_id", "drug_alive", "disease_alive", "s_alive", "d_ppi"}
    if not needed <= set(frame.columns) or frame.query_id.duplicated().any():
        raise ValueError("C's Retriever output does not meet the agreed contract")
    if set(frame.query_id) != {q["query_id"] for q in queries}:
        raise ValueError("C's Retriever omitted or added query IDs")
    if frame[list(needed)].isna().any().any():
        raise ValueError("C's Retriever returned missing values")
    alive = frame.drug_alive.astype(bool) & frame.disease_alive.astype(bool)
    if not alive.all():
        raise ValueError("Endpoints must remain alive in an edge-only experiment")
    out = frame[["query_id", "s_alive"]].copy()
    out["success_L2"] = alive & (frame.s_alive > 0)
    out["success_L3"] = alive & np.isfinite(frame.d_ppi) & (frame.d_ppi <= 1)
    if (out.success_L2 & ~out.success_L3).any():
        raise ValueError("C's distances contradict surviving two-hop paths")
    return out
