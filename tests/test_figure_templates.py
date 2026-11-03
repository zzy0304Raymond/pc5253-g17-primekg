"""Numerical guards for scientific templates, independent of rendered styling."""
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.figure_templates import draw, render, RESTORE


class FigureTemplateTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_curve_does_not_pool_missing_seeds_or_duplicates(self):
        frame = pd.DataFrame({"strategy": ["edge_random"]*3, "metric": ["gcc_frac"]*3,
                              "seed": [0, 1, 0], "frac_removed": [0,0,.5], "value": [1,1,.4]})
        _, ax = plt.subplots()
        with self.assertRaisesRegex(ValueError, "same set"):
            draw(ax, frame, "edge_random", "gcc_frac")
        frame = pd.concat([frame, frame.iloc[[0]]])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            draw(ax, frame, "edge_random", "gcc_frac")

    def test_deterministic_curve_has_no_uncertainty(self):
        frame = pd.DataFrame({"strategy": ["node_degree"]*2, "metric": ["gcc_frac"]*2,
                              "seed": [-1,-1], "frac_removed": [0,.5], "value": [1,.2]})
        _, ax = plt.subplots()
        draw(ax, frame, "node_degree", "gcc_frac")
        self.assertEqual(len(ax.collections), 0)
        np.testing.assert_allclose(ax.lines[0].get_ydata(), [1,.2])

    def test_paired_recovery_cancels_seed_baseline_variation(self):
        rows=[]
        for damage in (.3,.5):
            for metric in ("R_L2","R_L3"):
                for strategy in RESTORE:
                    for seed, baseline in ((0,.2),(1,.7)):
                        for budget, count, gain in ((0,0,0),(.1,100,.1)):
                            rows.append(dict(gid="g", damage_frac=damage, frac_removed=damage,
                                             metric=metric,strategy=strategy,seed=seed,
                                             budget_frac=budget,n_restored=count,value=baseline+gain))
        data=pd.DataFrame(rows)
        fig=render("fig_restoration",data)
        for ax in fig.axes:
            np.testing.assert_allclose(ax.lines[0].get_ydata(), [0,10])
            # Equal within-seed gains produce zero spread even though raw baselines differ.
            vertices=ax.collections[0].get_paths()[0].vertices
            np.testing.assert_allclose(vertices[vertices[:,0] == .1,1],10,atol=1e-12)
        efficiency=render("fig_gain_per_edge",data)
        np.testing.assert_allclose(efficiency.axes[0].lines[0].get_ydata(), [1])
        data.loc[(data.strategy == RESTORE[0]) & (data.seed == 0) & (data.budget_frac == 0), "value"] = .21
        with self.assertRaisesRegex(ValueError, "different zero-budget"):
            render("fig_restoration",data)

    def test_multiple_graphs_are_not_pooled(self):
        data=pd.DataFrame({"gid":["a","b"],"strategy":["edge_random"]*2,
                           "seed":[0,1],"frac_removed":[0,0],"metric":["gcc_frac"]*2,"value":[1,1]})
        with self.assertRaisesRegex(ValueError,"one gid"):
            render("fig_S_random_edge",data)


if __name__ == "__main__":
    unittest.main()
