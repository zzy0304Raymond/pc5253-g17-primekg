import unittest

import numpy as np
import pandas as pd

from src.run_ws6_indications import Graph, information
from src.run_ws7_horizon_attack import crossing, mean_field_attack


def toy():
    # drug 0, disease 1, proteins 2..5; routes 0-2-1 and 0-3-1; 3-4, 4-5 PPI
    nodes = pd.DataFrame(dict(nid=range(6), x_index=range(6),
                              node_type=["drug", "disease"] + ["gene/protein"] * 4, node_name=list("abcdef")))
    edges = pd.DataFrame(dict(eid=range(6), u=[0, 2, 0, 3, 3, 4], v=[2, 1, 3, 1, 4, 5],
                              relation=["drug_protein", "disease_protein", "drug_protein", "disease_protein",
                                        "protein_protein", "protein_protein"]))
    return Graph(nodes, edges)


class TestIndications(unittest.TestCase):
    def test_information_limits(self):
        self.assertAlmostEqual(float(information(.5, .5)), 0.0, places=9)
        self.assertAlmostEqual(float(information(1.0, 0.0)), 1.0, places=6)

    def test_retrieval_counts_routes(self):
        g = toy()
        r = g.retrieval(np.array([[0, 1]]), np.ones(len(g.uv), bool))
        self.assertEqual(int(r["m"][0]), 2)
        self.assertTrue(r["R2"][0] and r["R3"][0] and r["Rinf"][0])
        alive = np.ones(len(g.uv), bool)
        alive[[0, 2]] = False  # drug loses both targets
        r = g.retrieval(np.array([[0, 1]]), alive)
        self.assertFalse(r["R2"][0] or r["Rinf"][0])

    def test_mean_field_removing_one_route_protein(self):
        g = toy()
        # each route protein carries k_D k_Y = 1 route, so removing protein 2 cuts h = 1/2
        out = mean_field_attack(g, np.array([[0, 1]]), {"x": np.array([2, 3, 4, 5, 0, 1])}, [1 / 6])
        self.assertAlmostEqual(out.h_predicted.iloc[0], .5)
        self.assertAlmostEqual(out.route_survival_mean_field.iloc[0], 1 - .5 ** 2)
        self.assertEqual(out.route_survival_measured.iloc[0], 1.0)

    def test_crossing_interpolates(self):
        self.assertAlmostEqual(crossing(np.array([0, .5, 1.]), np.array([1, .75, .25])), .75)



class TestChanceHubs(unittest.TestCase):
    def test_auroc(self):
        from src.run_ws8_chance_hubs import auroc
        self.assertAlmostEqual(auroc(np.array([2., 3.]), np.array([0., 1.])), 1.0)
        self.assertAlmostEqual(auroc(np.array([1., 1.]), np.array([1., 1.])), 0.5)


if __name__ == "__main__":
    unittest.main()
