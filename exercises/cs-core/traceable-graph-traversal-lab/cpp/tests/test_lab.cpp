#include "traceable_graph_traversal_lab/lab.hpp"

#include <cassert>
#include <stdexcept>
#include <string>
#include <vector>

using namespace traceable_graph_traversal_lab;

int main() {
  {
    const std::vector<Edge> edges{{2, 0}, {2, 1}};
    const UndirectedGraph graph(3, edges);
    assert((graph.edges() == std::vector<Edge>{{0, 2}, {1, 2}}));
    assert((graph.neighbors(2) == std::vector<std::size_t>{0, 1}));
    assert((degree_sequence(graph) == std::vector<std::size_t>{1, 1, 2}));
    assert(has_edge(graph, 0, 2));
    assert(!has_edge(graph, 0, 1));
    const auto matrix = build_adjacency_matrix(graph);
    assert(matrix[0][2] && matrix[2][0] && !matrix[0][1]);
  }
  {
    const std::vector<std::vector<Edge>> invalid_edges{{{0, 2}}, {{1, 1}}, {{0, 2}, {2, 0}}};
    for (const std::vector<Edge>& edges : invalid_edges) {
      bool failed = false;
      try {
        static_cast<void>(UndirectedGraph(2, edges));
      } catch (const std::invalid_argument&) {
        failed = true;
      }
      assert(failed);
    }
  }
  const std::vector<Edge> sample_edges{{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {5, 6}};
  const UndirectedGraph graph(7, sample_edges);
  {
    const BfsTrace trace = breadth_first(graph, 0);
    assert((trace.order == std::vector<std::size_t>{0, 1, 2, 3, 4}));
    assert(trace.distances[4] == 3 && !trace.distances[6].has_value());
    assert(trace.parents[3] == 1);
    assert(trace.visits == 5 && trace.edge_checks == 10 && trace.max_frontier == 2);
    const PathTrace path = shortest_path(graph, 0, 4);
    assert((path.path == std::vector<std::size_t>{0, 1, 3, 4}) && path.distance == 3);
    assert(shortest_path(graph, 0, 6).path.empty());
    assert((reachable_within(graph, 0, 2) == std::vector<std::size_t>{0, 1, 2, 3}));
  }
  {
    const DfsTrace trace = depth_first_components(graph);
    assert((trace.components == std::vector<std::vector<std::size_t>>{{0, 1, 3, 2, 4}, {5, 6}}));
    assert(trace.visits == 7 && trace.edge_checks == 12 && trace.max_depth == 3);
    assert((trace.cycle_edge == Edge{0, 2}));
    const ComponentLabels labels = build_component_labels(graph);
    assert((labels.labels == std::vector<std::size_t>{0, 0, 0, 0, 0, 1, 1}));
  }
  {
    const std::vector<Edge> path_edges{{0, 1}, {1, 2}};
    const DfsTrace trace = depth_first_components(UndirectedGraph(3, path_edges));
    assert(!trace.cycle_edge.has_value());
  }
  {
    const std::vector<Edge> no_edges;
    const UndirectedGraph empty(0, no_edges);
    const DfsTrace trace = depth_first_components(empty);
    assert(trace.components.empty() && trace.max_depth == -1);
  }
  assert(build_graph_report().find("adjacency_entries=12") != std::string::npos);
  assert(build_bfs_report().find("path 0->4：0, 1, 3, 4，distance=3") != std::string::npos);
  assert(build_dfs_report().find("cycle=yes，first_edge=(0, 2)") != std::string::npos);
  return 0;
}
