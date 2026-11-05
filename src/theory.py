"""D's analytic predictions: GF percolation and PGF retrieval (WS4).

Every function evaluates an idealised ensemble, never a fit:

* ``R_edge`` and ``R_node`` are exact for independent random removal on the
  two-hop benchmark, because two paths through different proteins share no edge.
* ``gcc_*`` assume an uncorrelated, locally tree-like configuration model with
  the empirical degree sequence. Differences on a real graph are findings.
* ``R_inf_edge`` is the L -> infinity approximation of the review document,
  section 5.2. ``R_inf_edge_union`` adds the two-hop route, which survives even
  when neither endpoint reaches the PPI giant component.

``keep`` arguments are surviving fractions. Callers should pass the realised
value ``1 - n_removed / total``, as agreed in docs/DATA_CONTRACT.md.
"""
import numpy as np
import pandas as pd
from scipy.optimize import brentq

from .common import graph_dir, load_edges, load_nodes


def _fraction(value, name):
    value = float(value)
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must lie in [0, 1]")
    return value


def _redundancy(m_list):
    m = np.asarray(m_list)
    if m.ndim != 1 or not len(m) or not np.issubdtype(m.dtype, np.integer) or np.any(m < 1):
        raise ValueError("m_list must be a nonempty list of integers >= 1")
    return m


def _degrees(degrees):
    k = np.asarray(degrees)
    if k.ndim != 1 or not np.issubdtype(k.dtype, np.integer) or np.any(k < 0):
        raise ValueError("degrees must be nonnegative integers")
    return k.astype(np.int64)


def R_edge(p, m_list):
    """Two-hop success after edge removal: 1 - G(1 - p^2)."""
    p, m = _fraction(p, "p"), _redundancy(m_list)
    return float(np.mean(1 - (1 - p * p) ** m))


def R_node(phi, m_list):
    """Two-hop success after node removal: phi^2 [1 - G(1 - phi)]."""
    phi, m = _fraction(phi, "phi"), _redundancy(m_list)
    return float(np.mean(phi * phi * (1 - (1 - phi) ** m)))


def pc_bond(degrees):
    """Molloy-Reed bond threshold <k> / (<k^2> - <k>)."""
    k = _degrees(degrees).astype(float)
    excess = (k * k).sum() - k.sum()
    return float(k.sum() / excess) if excess > 0 else 1.0


def _smallest_root(k, weight, q):
    """Smallest u in [0, 1] solving u = q + sum_k weight[k] u^(k-1).

    The right side is increasing and convex, so F(u) = RHS - u has at most one
    root below 1. It lies left of the minimum of F, found from F'(u) = 0.
    """
    use = (k >= 1) & (weight > 0)
    k, weight = k[use], weight[use]

    def slope(u):
        high = k >= 2
        return float(np.dot(weight[high] * (k[high] - 1), u ** (k[high] - 2)))

    def excess(u):
        return float(q + np.dot(weight, u ** (k - 1)) - u)

    if slope(1.0) <= 1:
        return 1.0
    if excess(0.0) <= 0:
        return 0.0
    turn = 0.0 if slope(0.0) >= 1 else brentq(lambda u: slope(u) - 1, 0.0, 1.0, xtol=1e-14)
    return brentq(excess, 0.0, turn, xtol=1e-13)


def _table(degrees):
    k = _degrees(degrees)
    if not len(k) or k.sum() == 0:
        return None
    values, counts = np.unique(k, return_counts=True)
    pk = counts / len(k)
    return values, pk, float(np.dot(values, pk))


def gcc_bond(degrees, p):
    """S = 1 - g0(u), with u = 1 - p + p g1(u)."""
    p, table = _fraction(p, "p"), _table(degrees)
    if table is None or p == 0:
        return 0.0
    k, pk, mean = table
    u = _smallest_root(k, p * k * pk / mean, 1 - p)
    return float(max(0.0, 1 - np.dot(pk, u ** k)))


def gcc_site(degrees, phi):
    """S = phi [1 - g0(u)], with u = 1 - phi + phi g1(u)."""
    phi, table = _fraction(phi, "phi"), _table(degrees)
    if table is None or phi == 0:
        return 0.0
    k, pk, mean = table
    u = _smallest_root(k, phi * k * pk / mean, 1 - phi)
    return float(max(0.0, phi * (1 - np.dot(pk, u ** k))))


def gcc_degree_attack(degrees, f):
    """Callaway et al. 2000: remove the top fraction f by degree.

    Nodes of the cut-off degree are retained with the fraction that leaves
    exactly round(f N) nodes removed, so ties need no arbitrary order.
    S = f0(1) - f0(u), with u = 1 - f1(1) + f1(u).
    """
    f, table = _fraction(f, "f"), _table(degrees)
    if table is None or f == 1:
        return 0.0
    k, pk, mean = table
    n = len(np.asarray(degrees))
    counts = np.rint(pk * n).astype(np.int64)
    left = int(round(f * n))
    kept = counts.astype(float)
    for i in range(len(k) - 1, -1, -1):
        gone = min(left, counts[i])
        kept[i] -= gone
        left -= gone
        if not left:
            break
    keep_k = kept / counts
    weight = keep_k * k * pk / mean
    u = _smallest_root(k, weight, 1 - weight[k >= 1].sum())
    return float(max(0.0, np.dot(pk * keep_k, 1 - u ** k)))


class _Attachment:
    """Per-query PPI attachment data for one graph."""

    def __init__(self, gid):
        nodes = load_nodes(gid)
        features = pd.read_csv(graph_dir(gid) / "node_features.csv")
        protein = features.node_type.eq("gene/protein").to_numpy()
        self.ppi_all = features.ppi_degree.to_numpy(dtype=np.int64)
        self.ppi_degrees = self.ppi_all[protein]
        types = nodes.node_type.to_numpy()
        edges = load_edges(gid)
        self.partners = {}
        for relation, entity in (("drug_protein", "drug"), ("disease_protein", "disease")):
            frame = edges[edges.relation == relation]
            u, v = frame.u.to_numpy(), frame.v.to_numpy()
            left = types[u] == entity
            for a, b in zip(np.where(left, u, v), np.where(left, v, u)):
                self.partners.setdefault(int(a), []).append(int(b))
        self.partners = {a: np.array(b) for a, b in self.partners.items()}


_ATTACHMENTS = {}


def _attachment(gid):
    if gid not in _ATTACHMENTS:
        _ATTACHMENTS[gid] = _Attachment(gid)
    return _ATTACHMENTS[gid]


def _giant_attachment(p, gid, queries):
    data, p = _attachment(gid), _fraction(p, "p")
    table = _table(data.ppi_degrees)
    if table is None or p == 0:
        return np.zeros(len(queries))
    k, pk, mean = table
    u = _smallest_root(k, p * k * pk / mean, 1 - p)
    in_giant = 1 - u ** data.ppi_all
    miss = {a: float(np.prod(1 - p * in_giant[b])) for a, b in data.partners.items()}
    return np.array([(1 - miss[q["drug_nid"]]) * (1 - miss[q["disease_nid"]]) for q in queries])


def R_inf_edge(p, gid, queries):
    """L -> infinity: both endpoints attach to the PPI giant component."""
    return float(_giant_attachment(p, gid, queries).mean())


def R_attachment_bound(p, gid, queries):
    """Upper bound for any L: each endpoint keeps at least one terminal edge."""
    data, p = _attachment(gid), _fraction(p, "p")
    miss = {a: (1 - p) ** len(b) for a, b in data.partners.items()}
    return float(np.mean([(1 - miss[q["drug_nid"]]) * (1 - miss[q["disease_nid"]]) for q in queries]))


def R_inf_edge_union(p, gid, queries):
    """L -> infinity including the two-hop route, treated as independent."""
    giant = _giant_attachment(p, gid, queries)
    two_hop = 1 - (1 - p * p) ** np.array([q["redundancy_m"] for q in queries])
    return float(np.mean(1 - (1 - giant) * (1 - two_hop)))
