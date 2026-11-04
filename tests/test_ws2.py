"""Tests for WS2 centrality and analysis helpers."""

import unittest

import networkx as nx
import numpy as np

from src.common import check_order
from src.analyze_ws2 import jaccard


class WS2Tests(unittest.TestCase):

    def test_check_order_accepts_valid_permutation(self):
        """A valid attack order must contain every ID exactly once."""
        order = np.array([3, 0, 2, 1], dtype=np.int64)

        checked = check_order(order, 4)

        np.testing.assert_array_equal(
            checked,
            np.array([3, 0, 2, 1]),
        )

    def test_check_order_rejects_duplicate(self):
        """Duplicate node IDs must not be accepted."""
        order = np.array([0, 1, 1, 3], dtype=np.int64)

        with self.assertRaises(ValueError):
            check_order(order, 4)

    def test_degree_ranking_logic(self):
        """Nodes must be ranked by decreasing degree, then increasing nid."""
        g = nx.Graph()

        g.add_nodes_from([0, 1, 2, 3, 4])

        g.add_edges_from([
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 2),
            (3, 4),
        ])

        degree = dict(g.degree())

        order = sorted(
            g.nodes(),
            key=lambda nid: (-degree[nid], nid),
        )

        # Degrees:
        # node 0 -> 3
        # nodes 1,2,3 -> 2
        # node 4 -> 1
        #
        # Tie among 1,2,3 must be resolved by nid.
        self.assertEqual(
            order,
            [0, 1, 2, 3, 4],
        )

    def test_jaccard(self):
        """Jaccard = intersection / union."""
        a = [1, 2, 3, 4, 5]
        b = [1, 2, 3, 6, 7]

        result = jaccard(a, b)

        self.assertAlmostEqual(
            result,
            3 / 7,
        )


if __name__ == "__main__":
    unittest.main()