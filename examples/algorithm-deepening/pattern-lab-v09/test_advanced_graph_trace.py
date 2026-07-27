from __future__ import annotations
import subprocess,tempfile,unittest
from pathlib import Path
from advanced_graph_trace import condensation_edges,fixed_report,multi_source_distances,strongly_connected_components,topological_order
ROOT=Path(__file__).resolve().parent
N=list("ABCDEF")
D=[("A","C"),("B","C"),("C","D"),("C","E"),("D","F"),("E","F")]
C=[("A","B"),("B","C"),("C","A"),("C","D"),("D","E"),("E","D"),("E","F")]
class AdvancedGraphTests(unittest.TestCase):
 def test_topological_order_respects_every_edge(self):
  order=topological_order(N,D);self.assertEqual(order,tuple("ABCDEF"));position={node:i for i,node in enumerate(order or ())};self.assertTrue(all(position[a]<position[b] for a,b in D))
 def test_cycle_is_explicit(self): self.assertIsNone(topological_order(N,C))
 def test_scc_and_condensation(self):
  components=strongly_connected_components(N,C);self.assertEqual(components,(("A","B","C"),("D","E"),("F",)));self.assertEqual(condensation_edges(components,C),((0,1),(1,2)))
 def test_multi_source_first_discovery_distances(self): self.assertEqual(multi_source_distances(N,D,["B","A"]),{"A":0,"B":0,"C":1,"D":2,"E":2,"F":3})
 def test_invalid_graph_and_sources(self):
  with self.assertRaises(ValueError): topological_order(["A"],[("A","B")])
  with self.assertRaises(ValueError): multi_source_distances(N,D,[])
 def test_python_and_cpp_fixed_reports_match(self):
  with tempfile.TemporaryDirectory() as temp:
   binary=Path(temp)/"advanced_graph_trace";built=subprocess.run(["c++","-std=c++20","-Wall","-Wextra","-Werror","advanced_graph_trace.cpp","-o",str(binary)],cwd=ROOT,capture_output=True,text=True)
   self.assertEqual(built.returncode,0,built.stderr);run=subprocess.run([str(binary)],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(run.stdout.strip(),fixed_report())
if __name__=="__main__":unittest.main()

