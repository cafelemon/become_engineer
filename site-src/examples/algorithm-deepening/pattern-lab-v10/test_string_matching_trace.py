from __future__ import annotations
import subprocess,tempfile,unittest
from pathlib import Path
from string_matching_trace import Trie,fixed_report,kmp_matches,prefix_function
ROOT=Path(__file__).resolve().parent
class StringMatchingTests(unittest.TestCase):
 def make_trie(self):
  trie=Trie()
  for word in ("to","tea","ten","inn"):trie.insert(word)
  return trie
 def test_trie_distinguishes_word_from_prefix(self):
  trie=self.make_trie();self.assertFalse(trie.contains("te"));self.assertTrue(trie.contains("tea"));self.assertEqual(trie.complete("te"),("tea","ten"))
 def test_trie_is_deterministic_and_duplicate_insert_is_idempotent(self):
  trie=self.make_trie();self.assertEqual(trie.node_count,9);trie.insert("tea");self.assertEqual(trie.node_count,9);self.assertEqual(trie.complete(""),("inn","tea","ten","to"))
 def test_kmp_prefix_and_fixed_match(self):
  self.assertEqual(prefix_function("ababd"),(0,0,1,2,0));self.assertEqual(kmp_matches("ababcabcabababd","ababd"),(10,))
 def test_kmp_keeps_overlapping_matches(self): self.assertEqual(kmp_matches("aaaaa","aaa"),(0,1,2))
 def test_missing_and_empty_contracts(self):
  self.assertEqual(kmp_matches("abc","z"),())
  with self.assertRaises(ValueError):prefix_function("")
  with self.assertRaises(ValueError):self.make_trie().insert("")
 def test_python_and_cpp_fixed_reports_match(self):
  with tempfile.TemporaryDirectory() as temp:
   binary=Path(temp)/"string_matching_trace";built=subprocess.run(["c++","-std=c++20","-Wall","-Wextra","-Werror","string_matching_trace.cpp","-o",str(binary)],cwd=ROOT,capture_output=True,text=True)
   self.assertEqual(built.returncode,0,built.stderr);run=subprocess.run([str(binary)],capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(run.stdout.strip(),fixed_report())
if __name__=="__main__":unittest.main()

