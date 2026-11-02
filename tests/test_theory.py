import unittest
import numpy as np
from src.ws1_theory_reference import gcc_bond,gcc_site

class TheoryTests(unittest.TestCase):
    def test_regular_degree_three_exact(self):
        # Analytic nontrivial root for 3-regular graph: u=(1-p)/p above pc=1/2.
        d=np.full(100,3,dtype=int)
        for p in [0,.1,.49,.5,.5001,.6,.8,.99,1]:
            u=(1-p)/p if p>.5 else 1
            s=1-u**3
            self.assertAlmostEqual(gcc_bond(d,p),s,places=8)
            self.assertAlmostEqual(gcc_site(d,p),p*s,places=8)
    def test_isolates(self):
        self.assertEqual(gcc_bond(np.zeros(5,dtype=int),1),0)
        self.assertEqual(gcc_bond(np.array([],dtype=int),1),0)
        d=np.array([3]*100+[0]*100)
        self.assertAlmostEqual(gcc_bond(d,1),.5)

if __name__=='__main__': unittest.main()
