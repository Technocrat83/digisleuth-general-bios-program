import unittest
from urph_harness.fixtures import CHAMBERS,run_chambers,conformance_run
class HarnessConformanceTests(unittest.TestCase):
    def test_all_seven_chambers_pass(self):
        r=run_chambers(); self.assertEqual(tuple(r),CHAMBERS); self.assertTrue(all(r.values()),r)
    def test_exact_frozen_machine_vector(self):
        _,r,aux,v,eligible=conformance_run(); self.assertTrue(all(r.values()),r); self.assertTrue(all(aux.values()),aux); self.assertEqual(v,[1]*9); self.assertTrue(eligible)
if __name__=="__main__": unittest.main()
