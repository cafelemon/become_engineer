#include "traceable_spanning_forest_lab/lab.hpp"
#include <cassert>
#include <cstdint>
#include <limits>
#include <stdexcept>
using namespace traceable_spanning_forest_lab;
int main() {
  DisjointSet dsu(7);
  for (const auto& edge : {std::pair{0U,1U},std::pair{2U,3U},std::pair{0U,2U},std::pair{4U,5U},std::pair{5U,6U},std::pair{3U,6U}}) assert(dsu.unite(edge.first,edge.second).merged);
  assert((dsu.parents() == std::vector<std::size_t>{0,0,0,0,0,4,4}));
  const auto found=dsu.find(5); assert(found.visits==3 && found.compressions==1 && found.root==0);
  bool range_failed=false; try { dsu.find(7); } catch(const std::out_of_range&) { range_failed=true; } assert(range_failed);
  const auto graph=sample_spanning_graph(); const auto kruskal=kruskal_forest(graph); const auto prim=lazy_prim_forest(graph);
  assert(kruskal.total_weight==7 && kruskal.component_count==2 && kruskal.edges.size()==5);
  assert(prim.edge_scans==16 && prim.queue_pushes==8 && prim.stale_pops==3 && prim.max_frontier==4);
  assert(compare_spanning_forests(graph).matching);
  bool tree_failed=false; try { minimum_spanning_tree(graph); } catch(const std::invalid_argument&) { tree_failed=true; } assert(tree_failed);
  bool duplicate_failed=false; try { SpanningGraph bad(2,{{0,1,1},{1,0,2}}); } catch(const std::invalid_argument&) { duplicate_failed=true; } assert(duplicate_failed);
  bool overflow_failed=false; try { kruskal_forest(SpanningGraph(3,{{0,1,std::numeric_limits<std::int64_t>::max()},{1,2,1}})); } catch(const std::overflow_error&) { overflow_failed=true; } assert(overflow_failed);
  assert(build_dsu_report().starts_with("可追踪并查集")); assert(build_kruskal_report().starts_with("Kruskal")); assert(build_prim_report().starts_with("Lazy Prim"));
}
