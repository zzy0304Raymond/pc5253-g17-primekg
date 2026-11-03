import unittest

import networkx as nx
import numpy as np
import pandas as pd

from src.restoration import (restore, rank_random, rank_edge_betweenness,
                             rank_relation_type, training_path_eids,
                             task_aware_scores, rank_task_aware)
from src.restoration_evaluation import EdgeRestorationReference, gcc_fraction, evaluate_c


def fixture():
    nodes = pd.DataFrame({"nid": range(5), "node_type": ["drug", "disease"]+["gene/protein"]*3})
    uv = [(0,2),(1,2),(0,3),(1,3),(2,3),(0,4),(1,4),(3,4)]
    rel = ["drug_protein","disease_protein","drug_protein","disease_protein",
           "protein_protein","drug_protein","disease_protein","protein_protein"]
    edges = pd.DataFrame({"eid": range(8), "u": [a for a,b in uv], "v": [b for a,b in uv], "relation": rel})
    query = dict(query_id=0, drug_nid=0, disease_nid=1, intermediates=[2,3,4], split="train")
    return nodes, edges, query


class RestorationTests(unittest.TestCase):
    def test_budget_rounding_nesting_immutability_and_full_recovery(self):
        damaged = np.array([True,False,False,False,False,False])
        before = damaged.copy()
        rank = rank_random(np.flatnonzero(~damaged), 101)
        previous = damaged.copy()
        for budget in (0,.1,.2,.5,1):
            out = restore(damaged,rank,budget)
            self.assertFalse((previous & ~out).any())
            self.assertEqual(int((out & ~damaged).sum()), round(budget*5))
            previous = out
        self.assertTrue(out.all())
        np.testing.assert_array_equal(before,damaged)
        self.assertIsNot(out,damaged)

    def test_invalid_candidate_masks_and_budgets(self):
        mask=np.array([True,False])
        for order in (np.array([0]),np.array([1,1]),np.array([2]),np.array([1.0])):
            with self.assertRaises(ValueError): restore(mask,order,.5)
        for budget in (-.1,1.1,float("nan")):
            with self.assertRaises(ValueError): restore(mask,np.array([1]),budget)
        with self.assertRaises(ValueError): restore([1,0],np.array([1]),1)

    def test_random_and_betweenness_order(self):
        removed=np.array([0,2,5])
        np.testing.assert_array_equal(rank_random(removed,100),rank_random(removed,100))
        np.testing.assert_array_equal(rank_edge_betweenness(removed,np.array([5,4,3,2,1,0])),[5,2,0])

    def test_relation_type_exhaustion_never_restores_ppi(self):
        _,edges,_=fixture()
        mask=np.zeros(8,bool)
        ranked=rank_relation_type(np.arange(8),edges,100)
        self.assertEqual(set(ranked),{0,1,2,3,5,6})
        out=restore(mask,ranked,1)
        self.assertEqual(out.sum(),6)
        self.assertFalse(out[[4,7]].any())

    def test_task_scores_count_only_completable_failed_training_paths(self):
        _,edges,q=fixture()
        paths=training_path_eids(edges,[q])
        mask=np.array([False,True,False,False,True,True,False,True])
        scores=task_aware_scores(mask,paths)
        np.testing.assert_array_equal(scores,[1,0,0,0,0,0,1,0])
        removed=np.flatnonzero(~mask)
        rank=rank_task_aware(removed,mask,paths,100)
        self.assertEqual(set(rank[:2]),{0,6})
        np.testing.assert_array_equal(rank,rank_task_aware(removed,mask,paths,100))
        mask[0]=True  # one path is now alive: entire query no longer contributes
        self.assertEqual(task_aware_scores(mask,paths).sum(),0)
        q_test={**q,"split":"test"}
        with self.assertRaisesRegex(ValueError,"training queries only"):
            training_path_eids(edges,[q_test])

    def test_reference_all_masks_against_independent_graph_paths(self):
        nodes,edges,q=fixture()
        evaluator=EdgeRestorationReference(nodes,edges)
        for bits in range(256):
            mask=np.array([bool(bits & (1 << i)) for i in range(8)])
            graph=nx.Graph(); graph.add_nodes_from(range(5))
            graph.add_edges_from(edges.loc[mask,["u","v"]].itertuples(index=False,name=None))
            semantic=[]
            for path in nx.all_simple_paths(graph,0,1,cutoff=3):
                if all(nodes.node_type.iloc[n]=="gene/protein" for n in path[1:-1]):
                    semantic.append(path)
            got=evaluator.evaluate([q],mask).iloc[0]
            self.assertEqual(got.s_alive,sum(len(p)==3 for p in semantic))
            self.assertEqual(got.success_L2,any(len(p)<=3 for p in semantic))
            self.assertEqual(got.success_L3,bool(semantic))
            expected=max(map(len,nx.connected_components(graph)))/5
            self.assertEqual(gcc_fraction(5,edges,mask),expected)

    def test_c_adapter_checks_full_ids_and_infinite_distance(self):
        _,_,q=fixture()
        class Retriever:
            def evaluate(self, queries, **kwargs):
                return pd.DataFrame([dict(query_id=0,drug_alive=True,disease_alive=True,s_alive=0,d_ppi=np.inf)])
        out=evaluate_c(Retriever(),[q],np.ones(8,bool))
        self.assertFalse(out.success_L3.iloc[0])
        with self.assertRaisesRegex(ValueError,"query IDs"):
            evaluate_c(Retriever(),[{**q,"query_id":10}],np.ones(8,bool))


if __name__ == "__main__": unittest.main()
