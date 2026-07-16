#pragma once

#include <cstddef>
#include <optional>
#include <span>
#include <string>
#include <utility>
#include <vector>

namespace traceable_graph_traversal_lab {

struct Edge {
  std::size_t u;
  std::size_t v;
  bool operator==(const Edge&) const = default;
};

struct GraphSummary {
  std::size_t vertex_count;
  std::size_t edge_count;
  std::size_t adjacency_entries;
};

class UndirectedGraph {
 public:
  UndirectedGraph(std::size_t vertex_count, std::span<const Edge> edges);

  [[nodiscard]] std::size_t vertex_count() const noexcept;
  [[nodiscard]] const std::vector<Edge>& edges() const noexcept;
  [[nodiscard]] const std::vector<std::size_t>& neighbors(std::size_t vertex) const;

 private:
  std::size_t vertex_count_;
  std::vector<Edge> edges_;
  std::vector<std::vector<std::size_t>> adjacency_;
};

struct BfsTrace {
  std::vector<std::size_t> order;
  std::vector<std::optional<std::size_t>> distances;
  std::vector<std::optional<std::size_t>> parents;
  std::size_t visits;
  std::size_t edge_checks;
  std::size_t max_frontier;
};

struct PathTrace {
  std::vector<std::size_t> path;
  std::optional<std::size_t> distance;
};

struct DfsTrace {
  std::vector<std::vector<std::size_t>> components;
  std::size_t visits;
  std::size_t edge_checks;
  int max_depth;
  std::optional<Edge> cycle_edge;
};

struct ComponentLabels {
  std::vector<std::size_t> labels;
  std::size_t component_count;
};

[[nodiscard]] GraphSummary describe_graph(const UndirectedGraph& graph);
[[nodiscard]] std::vector<std::vector<bool>> build_adjacency_matrix(const UndirectedGraph& graph);
[[nodiscard]] std::vector<std::size_t> degree_sequence(const UndirectedGraph& graph);
[[nodiscard]] bool has_edge(const UndirectedGraph& graph, std::size_t u, std::size_t v);
[[nodiscard]] BfsTrace breadth_first(const UndirectedGraph& graph, std::size_t start);
[[nodiscard]] PathTrace shortest_path(const UndirectedGraph& graph, std::size_t start, std::size_t target);
[[nodiscard]] std::vector<std::size_t> reachable_within(const UndirectedGraph& graph, std::size_t start,
                                                        std::size_t max_distance);
[[nodiscard]] DfsTrace depth_first_components(const UndirectedGraph& graph);
[[nodiscard]] ComponentLabels build_component_labels(const UndirectedGraph& graph);

[[nodiscard]] std::string build_graph_report();
[[nodiscard]] std::string build_bfs_report();
[[nodiscard]] std::string build_dfs_report();

}  // namespace traceable_graph_traversal_lab
