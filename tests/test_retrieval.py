"""Cross-check C against A's independent NetworkX fixtures and E's adapter."""

import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.common import ROOT, edge_alive_mask, load_queries, node_alive_mask
from src.restoration_evaluation import EdgeRestorationReference, evaluate_c
from src.retrieval import Retriever


class RetrievalTests(unittest.TestCase):
    def test_toy_and_2000_match_independent_reference(self):
        for gid in ("toy_v1", "primekg_2000_bfs_v1"):
            retriever = Retriever(gid)
            queries = load_queries(gid)
            reference = pd.read_csv(ROOT / "results" / "validation" / f"{gid}__retrieval_reference.csv")
            for (strategy, seed, f), expected in reference.groupby(["strategy", "seed", "frac_removed"]):
                with self.subTest(gid=gid, strategy=strategy, fraction=f):
                    order = f"{strategy}_s{seed}"
                    masks = ({"edge_alive": edge_alive_mask(gid, order, f)}
                             if strategy == "edge_random"
                             else {"node_alive": node_alive_mask(gid, order, f)})
                    got = retriever.evaluate(queries, compute_dist=True, **masks)
                    expected = expected[got.columns].reset_index(drop=True)
                    pd.testing.assert_frame_equal(got, expected, check_dtype=False)
                    fast = retriever.evaluate(queries, **masks)
                    self.assertTrue(fast.d_ppi.isna().all())
                    pd.testing.assert_frame_equal(fast.drop(columns="d_ppi"), got.drop(columns="d_ppi"))

    def test_combined_masks_and_alternative_ppi_path(self):
        nodes = pd.DataFrame({"node_type": ["drug", "disease"] + ["gene/protein"] * 3})
        edges = pd.DataFrame([
            (0, 2, "drug_protein"), (0, 3, "drug_protein"),
            (1, 2, "disease_protein"), (1, 4, "disease_protein"),
            (3, 4, "protein_protein"),
        ], columns=["u", "v", "relation"])
        queries = [{"query_id": 1, "drug_nid": 0, "disease_nid": 1}]
        with patch("src.retrieval.load_nodes", return_value=nodes), patch(
            "src.retrieval.load_edges", return_value=edges
        ):
            retriever = Retriever("fixture")
        node_mask = np.array([True, True, False, True, True])
        edge_mask = np.ones(5, dtype=bool)
        row = retriever.evaluate(queries, edge_mask, node_mask, compute_dist=True).iloc[0]
        self.assertEqual((row.s_alive, row.d_ppi), (0, 1))
        edge_mask[-1] = False
        row = retriever.evaluate(queries, edge_mask, node_mask, compute_dist=True).iloc[0]
        self.assertTrue(np.isinf(row.d_ppi))
        node_mask[0] = False
        row = retriever.evaluate(queries, edge_mask, node_mask, compute_dist=True).iloc[0]
        self.assertFalse(row.drug_alive)
        self.assertEqual(row.s_alive, 0)
        np.testing.assert_array_equal(edge_mask, [True, True, True, True, False])
        np.testing.assert_array_equal(node_mask, [False, True, False, True, True])

    def test_e_adapter_matches_independent_edge_evaluator(self):
        from src.common import load_nodes

        gid = "toy_v1"
        retriever = Retriever(gid)
        reference = EdgeRestorationReference(load_nodes(gid), retriever.edges)
        queries = load_queries(gid)
        mask = edge_alive_mask(gid, "edge_random_s0", .5)
        pd.testing.assert_frame_equal(evaluate_c(retriever, queries, mask),
                                      reference.evaluate(queries, mask))
