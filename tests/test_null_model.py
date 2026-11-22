"""Checks for the degree-preserving rewirings in src/run_null_model.py."""
import unittest

import networkx as nx
import numpy as np

from src import run_null_model as N


def toy():
    """Small typed graph: 6 drugs, 8 diseases, 60 proteins on a BA backbone."""
    rng = np.random.default_rng(0)
    types = np.array(["drug"] * 6 + ["disease"] * 8 + ["gene/protein"] * 60)
    proteins = np.arange(14, 74)
    edges, relation = set(), {}
    for a, b in nx.barabasi_albert_graph(60, 2, seed=1).edges():
        key = tuple(sorted((int(proteins[a]), int(proteins[b]))))
        edges.add(key)
        relation[key] = "protein_protein"
    for entity, count, rel in ((range(6), 3, "drug_protein"), (range(6, 14), 6, "disease_protein")):
        for e in entity:
            for p in rng.choice(proteins, count, replace=False):
                key = tuple(sorted((int(e), int(p))))
                edges.add(key)
                relation[key] = rel
    keys = sorted(edges)
    return np.array(keys, dtype=np.int64), np.array([relation[k] for k in keys]), types


class Rewiring(unittest.TestCase):
    def setUp(self):
        self.uv, self.relation, self.types = toy()
        self.degree = np.bincount(self.uv.ravel(), minlength=len(self.types))

    def assert_simple_same_degrees(self, uv):
        self.assertTrue(np.array_equal(np.bincount(uv.ravel(), minlength=len(self.types)), self.degree))
        self.assertFalse(np.any(uv[:, 0] == uv[:, 1]))
        self.assertEqual(len({tuple(sorted(e)) for e in uv.tolist()}), len(uv))

    def test_full_rewiring_keeps_degrees(self):
        uv = self.uv.copy()
        accepted = N.rewire_full(uv, self.relation, self.degree, np.random.default_rng(3))
        self.assertGreater(accepted, 0)
        self.assert_simple_same_degrees(uv)

    def test_typed_rewiring_keeps_typed_degrees(self):
        uv = self.uv.copy()
        N.rewire_typed(uv, self.relation, self.degree, self.types)(np.random.default_rng(3))
        self.assert_simple_same_degrees(uv)
        for rel in np.unique(self.relation):
            before = np.bincount(self.uv[self.relation == rel].ravel(), minlength=len(self.types))
            after = np.bincount(uv[self.relation == rel].ravel(), minlength=len(self.types))
            self.assertTrue(np.array_equal(before, after), rel)
        drug_side = np.isin(uv, np.arange(6))
        self.assertTrue(np.all(drug_side[self.relation == "drug_protein"].sum(axis=1) == 1))

    def test_2k_rewiring_keeps_joint_degree_distribution(self):
        uv = self.uv.copy()
        N.rewire_2k(uv, self.relation, self.degree, np.random.default_rng(3))
        self.assert_simple_same_degrees(uv)
        joint = lambda e: sorted(tuple(sorted((self.degree[a], self.degree[b]))) for a, b in e.tolist())
        self.assertEqual(joint(uv), joint(self.uv))
        self.assertAlmostEqual(N.assortativity(uv, self.degree), N.assortativity(self.uv, self.degree))


if __name__ == "__main__":
    unittest.main()
