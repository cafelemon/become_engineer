#pragma once

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <vector>

namespace traceable_spanning_forest_lab {

struct FindTrace { std::size_t root; std::vector<std::size_t> path; std::size_t visits; std::size_t compressions; };
struct UnionTrace { bool merged; std::size_t root; std::optional<std::size_t> attached_root; std::size_t component_count; std::size_t find_visits; std::size_t compressions; };
struct ComponentGroup { std::size_t representative; std::vector<std::size_t> members; };

class DisjointSet {
 public:
  explicit DisjointSet(std::size_t element_count);
  FindTrace find(std::size_t element);
  UnionTrace unite(std::size_t first, std::size_t second);
  bool connected(std::size_t first, std::size_t second);
  const std::vector<std::size_t>& parents() const noexcept;
  const std::vector<std::size_t>& sizes() const noexcept;
  std::size_t component_count() const noexcept;
  std::vector<ComponentGroup> groups();
 private:
  void check(std::size_t element) const;
  std::vector<std::size_t> parents_;
  std::vector<std::size_t> sizes_;
  std::size_t component_count_;
};

struct SpanningEdge { std::size_t u; std::size_t v; std::int64_t weight; };
bool operator==(const SpanningEdge& first, const SpanningEdge& second) noexcept;
struct KruskalEvent { SpanningEdge edge; bool accepted; std::size_t components_before; std::size_t components_after; };
struct SpanningForest { std::vector<SpanningEdge> edges; std::int64_t total_weight; std::size_t component_count; std::vector<KruskalEvent> events; };
struct PrimEvent { SpanningEdge edge; bool accepted; };
struct PrimTrace { SpanningForest forest; std::vector<std::size_t> component_starts; std::size_t edge_scans; std::size_t queue_pushes; std::size_t stale_pops; std::size_t max_frontier; std::vector<PrimEvent> events; };
struct ForestComparison { bool matching; std::int64_t kruskal_weight; std::int64_t prim_weight; std::size_t component_count; std::size_t expected_edge_count; };

class SpanningGraph {
 public:
  SpanningGraph(std::size_t vertex_count, const std::vector<SpanningEdge>& edges);
  std::size_t vertex_count() const noexcept;
  const std::vector<SpanningEdge>& edges() const noexcept;
  const std::vector<SpanningEdge>& neighbors(std::size_t vertex) const;
 private:
  std::size_t vertex_count_;
  std::vector<SpanningEdge> edges_;
  std::vector<std::vector<SpanningEdge>> adjacency_;
};

SpanningForest kruskal_forest(const SpanningGraph& graph);
SpanningForest minimum_spanning_tree(const SpanningGraph& graph);
std::vector<SpanningEdge> rejected_cycle_edges(const SpanningGraph& graph);
PrimTrace lazy_prim_forest(const SpanningGraph& graph);
ForestComparison compare_spanning_forests(const SpanningGraph& graph);
SpanningGraph sample_spanning_graph();
std::string build_dsu_report();
std::string build_kruskal_report();
std::string build_prim_report();

}  // namespace traceable_spanning_forest_lab

