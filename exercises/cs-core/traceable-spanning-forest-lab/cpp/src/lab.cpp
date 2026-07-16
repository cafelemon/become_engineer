#include "traceable_spanning_forest_lab/lab.hpp"

#include <algorithm>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <tuple>
#include <utility>

namespace traceable_spanning_forest_lab {

DisjointSet::DisjointSet(std::size_t element_count)
    : parents_(element_count), sizes_(element_count, 1), component_count_(element_count) {
  std::iota(parents_.begin(), parents_.end(), 0);
}
void DisjointSet::check(std::size_t element) const { if (element >= parents_.size()) throw std::out_of_range("element out of range"); }
FindTrace DisjointSet::find(std::size_t element) {
  check(element);
  std::vector<std::size_t> path{element};
  auto current = element;
  while (parents_[current] != current) { current = parents_[current]; path.push_back(current); }
  const auto root = current;
  std::size_t compressions = 0;
  for (std::size_t index = 0; index + 1 < path.size(); ++index) {
    if (parents_[path[index]] != root) { parents_[path[index]] = root; ++compressions; }
  }
  return {root, path, path.size(), compressions};
}
UnionTrace DisjointSet::unite(std::size_t first, std::size_t second) {
  auto first_trace = find(first); auto second_trace = find(second);
  auto first_root = first_trace.root; auto second_root = second_trace.root;
  const auto visits = first_trace.visits + second_trace.visits;
  const auto compressions = first_trace.compressions + second_trace.compressions;
  if (first_root == second_root) return {false, first_root, std::nullopt, component_count_, visits, compressions};
  if (sizes_[first_root] < sizes_[second_root] || (sizes_[first_root] == sizes_[second_root] && first_root > second_root)) std::swap(first_root, second_root);
  parents_[second_root] = first_root; sizes_[first_root] += sizes_[second_root]; --component_count_;
  return {true, first_root, second_root, component_count_, visits, compressions};
}
bool DisjointSet::connected(std::size_t first, std::size_t second) { return find(first).root == find(second).root; }
const std::vector<std::size_t>& DisjointSet::parents() const noexcept { return parents_; }
const std::vector<std::size_t>& DisjointSet::sizes() const noexcept { return sizes_; }
std::size_t DisjointSet::component_count() const noexcept { return component_count_; }
std::vector<ComponentGroup> DisjointSet::groups() {
  std::map<std::size_t, std::vector<std::size_t>> grouped;
  for (std::size_t element = 0; element < parents_.size(); ++element) grouped[find(element).root].push_back(element);
  std::vector<ComponentGroup> result;
  for (auto& [root, members] : grouped) result.push_back({root, std::move(members)});
  return result;
}

bool operator==(const SpanningEdge& first, const SpanningEdge& second) noexcept { return first.u == second.u && first.v == second.v && first.weight == second.weight; }

SpanningGraph::SpanningGraph(std::size_t vertex_count, const std::vector<SpanningEdge>& edges)
    : vertex_count_(vertex_count), adjacency_(vertex_count) {
  std::vector<std::pair<std::size_t, std::size_t>> seen;
  for (auto edge : edges) {
    if (edge.u >= vertex_count || edge.v >= vertex_count) throw std::invalid_argument("edge endpoint out of range");
    if (edge.u == edge.v) throw std::invalid_argument("self-loops are not allowed");
    if (edge.u > edge.v) std::swap(edge.u, edge.v);
    const auto pair = std::pair{edge.u, edge.v};
    if (std::find(seen.begin(), seen.end(), pair) != seen.end()) throw std::invalid_argument("duplicate undirected edge");
    seen.push_back(pair); edges_.push_back(edge);
  }
  std::sort(edges_.begin(), edges_.end(), [](const auto& a, const auto& b) { return std::tie(a.u, a.v, a.weight) < std::tie(b.u, b.v, b.weight); });
  for (const auto& edge : edges_) { adjacency_[edge.u].push_back(edge); adjacency_[edge.v].push_back(edge); }
  for (std::size_t vertex = 0; vertex < adjacency_.size(); ++vertex) {
    std::sort(adjacency_[vertex].begin(), adjacency_[vertex].end(), [vertex](const auto& a, const auto& b) {
      const auto an = a.u == vertex ? a.v : a.u; const auto bn = b.u == vertex ? b.v : b.u; return an < bn;
    });
  }
}
std::size_t SpanningGraph::vertex_count() const noexcept { return vertex_count_; }
const std::vector<SpanningEdge>& SpanningGraph::edges() const noexcept { return edges_; }
const std::vector<SpanningEdge>& SpanningGraph::neighbors(std::size_t vertex) const { if (vertex >= vertex_count_) throw std::out_of_range("vertex out of range"); return adjacency_[vertex]; }

static std::int64_t safe_add(std::int64_t total, std::int64_t weight) {
  if ((weight > 0 && total > std::numeric_limits<std::int64_t>::max() - weight) ||
      (weight < 0 && total < std::numeric_limits<std::int64_t>::min() - weight)) throw std::overflow_error("forest total weight exceeds signed 64-bit range");
  return total + weight;
}

SpanningForest kruskal_forest(const SpanningGraph& graph) {
  auto ordered = graph.edges();
  std::sort(ordered.begin(), ordered.end(), [](const auto& a, const auto& b) { return std::tie(a.weight, a.u, a.v) < std::tie(b.weight, b.u, b.v); });
  DisjointSet dsu(graph.vertex_count()); SpanningForest result{{}, 0, graph.vertex_count(), {}};
  for (const auto& edge : ordered) {
    const auto before = dsu.component_count(); const auto trace = dsu.unite(edge.u, edge.v);
    if (trace.merged) { result.total_weight = safe_add(result.total_weight, edge.weight); result.edges.push_back(edge); }
    result.events.push_back({edge, trace.merged, before, dsu.component_count()});
  }
  result.component_count = dsu.component_count(); return result;
}
SpanningForest minimum_spanning_tree(const SpanningGraph& graph) { auto result = kruskal_forest(graph); if (graph.vertex_count() == 0 || result.component_count != 1) throw std::invalid_argument("graph does not have a spanning tree"); return result; }
std::vector<SpanningEdge> rejected_cycle_edges(const SpanningGraph& graph) { std::vector<SpanningEdge> result; for (const auto& event : kruskal_forest(graph).events) if (!event.accepted) result.push_back(event.edge); return result; }

struct QueueEdge { SpanningEdge edge; std::size_t from; std::size_t to; };
struct QueueGreater { bool operator()(const QueueEdge& a, const QueueEdge& b) const { return std::tie(a.edge.weight, a.edge.u, a.edge.v) > std::tie(b.edge.weight, b.edge.u, b.edge.v); } };

PrimTrace lazy_prim_forest(const SpanningGraph& graph) {
  std::vector<bool> visited(graph.vertex_count(), false); PrimTrace trace{{{}, 0, 0, {}}, {}, 0, 0, 0, 0, {}};
  auto visit = [&](std::size_t vertex, auto& queue) {
    visited[vertex] = true;
    for (const auto& edge : graph.neighbors(vertex)) {
      ++trace.edge_scans; const auto neighbor = edge.u == vertex ? edge.v : edge.u;
      if (!visited[neighbor]) { queue.push({edge, vertex, neighbor}); ++trace.queue_pushes; trace.max_frontier = std::max(trace.max_frontier, queue.size()); }
    }
  };
  for (std::size_t start = 0; start < graph.vertex_count(); ++start) {
    if (visited[start]) continue;
    ++trace.forest.component_count; trace.component_starts.push_back(start);
    std::priority_queue<QueueEdge, std::vector<QueueEdge>, QueueGreater> queue; visit(start, queue);
    while (!queue.empty()) {
      const auto item = queue.top(); queue.pop();
      if (visited[item.from] && visited[item.to]) { ++trace.stale_pops; trace.events.push_back({item.edge, false}); continue; }
      const auto next = visited[item.to] ? item.from : item.to;
      trace.forest.total_weight = safe_add(trace.forest.total_weight, item.edge.weight); trace.forest.edges.push_back(item.edge); trace.events.push_back({item.edge, true}); visit(next, queue);
    }
  }
  return trace;
}
ForestComparison compare_spanning_forests(const SpanningGraph& graph) {
  const auto kruskal = kruskal_forest(graph); const auto prim = lazy_prim_forest(graph).forest;
  const auto expected = graph.vertex_count() - kruskal.component_count;
  const bool matching = kruskal.total_weight == prim.total_weight && kruskal.component_count == prim.component_count && kruskal.edges.size() == expected && prim.edges.size() == expected;
  return {matching, kruskal.total_weight, prim.total_weight, kruskal.component_count, expected};
}
SpanningGraph sample_spanning_graph() { return {7, {{0,1,4},{0,2,1},{1,2,2},{1,3,5},{2,3,3},{2,4,6},{3,4,2},{5,6,-1}}}; }

template <typename T> static std::string join_numbers(const std::vector<T>& values) { std::ostringstream out; for (std::size_t i=0;i<values.size();++i) { if (i) out << ", "; out << values[i]; } return out.str(); }
static std::string join_edges(const std::vector<SpanningEdge>& edges) { std::ostringstream out; for (std::size_t i=0;i<edges.size();++i) { if (i) out << ", "; out << edges[i].u << '-' << edges[i].v << '@' << edges[i].weight; } return out.str(); }

std::string build_dsu_report() {
  DisjointSet dsu(7); std::size_t merged=0; for (const auto& [a,b] : std::vector<std::pair<std::size_t,std::size_t>>{{0,1},{2,3},{0,2},{4,5},{5,6},{3,6}}) merged += dsu.unite(a,b).merged ? 1U : 0U;
  const auto before=dsu.parents(); const auto found=dsu.find(5); std::ostringstream out;
  out << "可追踪并查集\nelements=7\nunions：0-1, 2-3, 0-2, 4-5, 5-6, 3-6\nmerged=" << merged << "，components=" << dsu.component_count() << "\nparents_before_find：" << join_numbers(before) << "\nfind(5)：root=" << found.root << "，visits=" << found.visits << "，compressed=" << found.compressions << "\nparents_after_find：" << join_numbers(dsu.parents()) << "\nconnected(3,6)=" << (dsu.connected(3,6) ? "yes" : "no"); return out.str();
}
std::string build_kruskal_report() {
  const auto graph=sample_spanning_graph(); auto ordered=graph.edges(); std::sort(ordered.begin(),ordered.end(),[](const auto&a,const auto&b){return std::tie(a.weight,a.u,a.v)<std::tie(b.weight,b.u,b.v);}); const auto forest=kruskal_forest(graph); std::size_t rejected=0; for(const auto&e:forest.events) rejected += e.accepted?0U:1U; std::ostringstream out;
  out << "Kruskal 最小生成森林\nedges_sorted：" << join_edges(ordered) << "\naccepted：" << join_edges(forest.edges) << "\nrejected_cycles=" << rejected << "，components=" << forest.component_count << "\ntotal_weight=" << forest.total_weight << "，edge_count=" << forest.edges.size(); return out.str();
}
std::string build_prim_report() {
  const auto graph=sample_spanning_graph(); const auto trace=lazy_prim_forest(graph); const auto comparison=compare_spanning_forests(graph); std::ostringstream out;
  out << "Lazy Prim 最小生成森林\ncomponent_starts：" << join_numbers(trace.component_starts) << "\naccepted：" << join_edges(trace.forest.edges) << "\nedge_scans=" << trace.edge_scans << "，queue_pushes=" << trace.queue_pushes << "，stale_pops=" << trace.stale_pops << "，max_frontier=" << trace.max_frontier << "\ncomponents=" << trace.forest.component_count << "，total_weight=" << trace.forest.total_weight << "\nmatches_kruskal=" << (comparison.matching?"yes":"no"); return out.str();
}

}  // namespace traceable_spanning_forest_lab

