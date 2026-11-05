"""Checks for D's theory module. Analytic cases first, then the shared solver."""
import unittest

import numpy as np

from src import theory as T
from src import ws1_theory_reference as reference


class RetrievalFormula(unittest.TestCase):
    def test_single_path_is_p_squared(self):
        for p in (0, .3, .5, 1):
            self.assertAlmostEqual(T.R_edge(p, [1, 1, 1]), p * p)

    def test_review_table_values(self):
        self.assertAlmostEqual(T.R_edge(.7, [2]), .7399, places=4)
        self.assertAlmostEqual(T.R_edge(.5, [3]), .578125)

    def test_pgf_mixture_is_the_mean(self):
        self.assertAlmostEqual(T.R_edge(.5, [1, 3]), (.25 + .578125) / 2)

    def test_node_formula_needs_both_endpoints(self):
        self.assertAlmostEqual(T.R_node(.5, [1]), .125)
        self.assertEqual(T.R_node(0, [4]), 0)
        self.assertEqual(T.R_node(1, [4]), 1)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            T.R_edge(1.2, [1])
        with self.assertRaises(ValueError):
            T.R_edge(.5, [0])


class GiantComponent(unittest.TestCase):
    def test_three_regular_analytic_root(self):
        degrees = np.full(100, 3, dtype=int)
        for p in (.1, .49, .5, .6, .8, .99, 1):
            u = (1 - p) / p if p > .5 else 1
            self.assertAlmostEqual(T.gcc_bond(degrees, p), 1 - u ** 3, places=8)
            self.assertAlmostEqual(T.gcc_site(degrees, p), p * (1 - u ** 3), places=8)

    def test_molloy_reed_threshold(self):
        rng = np.random.default_rng(0)
        degrees = rng.poisson(4, 100000)
        pc = T.pc_bond(degrees)
        self.assertAlmostEqual(pc, .25, places=2)
        self.assertEqual(T.gcc_bond(degrees, pc * .98), 0)
        self.assertGreater(T.gcc_bond(degrees, pc * 1.1), 0)

    def test_agrees_with_a_independent_solver(self):
        degrees = np.random.default_rng(1).zipf(2.2, 4000).clip(1, 400)
        for keep in np.linspace(0, 1, 41):
            self.assertAlmostEqual(T.gcc_bond(degrees, keep), reference.gcc_bond(degrees, keep), places=7)
            self.assertAlmostEqual(T.gcc_site(degrees, keep), reference.gcc_site(degrees, keep), places=7)

    def test_attack_limits(self):
        degrees = np.array([1, 2, 2, 3, 3, 3, 4, 5, 8, 9] * 40)
        self.assertAlmostEqual(T.gcc_degree_attack(degrees, 0), T.gcc_bond(degrees, 1), places=10)
        self.assertEqual(T.gcc_degree_attack(degrees, 1), 0)

    def test_attack_on_regular_graph_matches_site_percolation(self):
        # All degrees tie, so a degree attack cannot differ from uniform removal.
        degrees = np.full(1000, 4, dtype=int)
        for f in (.1, .3, .5):
            self.assertAlmostEqual(T.gcc_degree_attack(degrees, f), T.gcc_site(degrees, 1 - f), places=8)


class HopLimit(unittest.TestCase):
    gid = "toy_v1"

    def test_limits_on_toy_graph(self):
        from src.common import load_queries
        queries = load_queries(self.gid)
        self.assertEqual(T.R_inf_edge(0, self.gid, queries), 0)
        self.assertLessEqual(T.R_inf_edge(.5, self.gid, queries), T.R_attachment_bound(.5, self.gid, queries) + 1e-12)
        self.assertAlmostEqual(T.R_attachment_bound(1, self.gid, queries), 1)


if __name__ == "__main__":
    unittest.main()
