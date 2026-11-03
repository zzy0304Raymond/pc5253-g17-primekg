import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.run_ws5 import run, STRATEGIES
from test_restoration import fixture


class WS5RunnerTests(unittest.TestCase):
    def test_all_four_strategies_end_to_end_with_test_only_evaluation(self):
        nodes, edges, q = fixture()
        queries = [q, {**q, "query_id": 7, "split": "test"}]
        def order(gid, name):
            if name == "edge_betweenness":
                return np.arange(len(edges)-1,-1,-1)
            return np.random.default_rng(int(name[-1])).permutation(len(edges))
        with tempfile.TemporaryDirectory() as temp, \
             patch("src.run_ws5.load_nodes", return_value=nodes), \
             patch("src.run_ws5.load_edges", return_value=edges), \
             patch("src.run_ws5.load_queries", return_value=queries), \
             patch("src.run_ws5.load_order", side_effect=order), \
             contextlib.redirect_stdout(io.StringIO()):
            folder=Path(temp)/"run"
            table=run("test",folder,evaluator="reference",strategies=STRATEGIES,seeds=(0,1))
            self.assertEqual(len(table),2*2*4*4*3)
            self.assertEqual(set(table.strategy),{"restore_"+s for s in STRATEGIES})
            self.assertTrue((table.n_restored<=table.requested_n_restored).all())
            pq=pd.read_csv(folder/"test__test_perquery.csv")
            self.assertEqual(set(pq.query_id),{7})
            self.assertFalse((pq.success_L2 & ~pq.success_L3).any())
            self.assertTrue((table[table.budget_frac==0].groupby(["damage_frac","seed","metric"]).value.nunique()==1).all())
            meta=json.loads((folder/"provenance.json").read_text())
            self.assertEqual(meta["status"],"complete")
            self.assertEqual(meta["missing_strategies"],[])
            self.assertEqual(meta["test_query_ids"],[7])
            with self.assertRaises(FileExistsError):
                run("test",folder,evaluator="reference",strategies=STRATEGIES,seeds=(0,1))


if __name__ == "__main__": unittest.main()
