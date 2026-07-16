#include "traceable_graph_traversal_lab/lab.hpp"

#include <algorithm>
#include <deque>
#include <functional>
#include <limits>
#include <sstream>
#include <stdexcept>

namespace traceable_graph_traversal_lab {

UndirectedGraph::UndirectedGraph(std::size_t vertex_count, std::span<const Edge> edges)
    : vertex_count_(vertex_count), edges_(), adjacency_(vertex_count) {
  edges_.reserve(edges.size());
  for (const Edge raw : edges) {
    if (raw.u >= vertex_count_ || raw.v >= vertex_count_) {
      throw std::invalid_argument("edge endpoint out of range");
    }
    if (raw.u == raw.v) {
      throw std::invalid_argument("self-loops are not allowed");
    }
    edges_.push_back({std::min(raw.u, raw.v), std::max(raw.u, raw.v)});
  }
  std::sort(edges_.begin(), edges_.end(), [](const Edge left, const Edge right) {
    return left.u < right.u || (left.u == right.u && left.v < right.v);
  });
  if (std::adjacent_find(edges_.begin(), edges_.end()) != edges_.end()) {
    throw std::invalid_argument("duplicate edges are not allowed");
  }
  for (const Edge edge : edges_) {
    adjacency_[edge.u].push_back(edge.v);
    adjacency_[edge.v].push_back(edge.u);
  }
  for (auto& neighbors_list : adjacency_) {
    std::sort(neighbors_list.begin(), neighbors_list.end());
  }
}

std::size_t UndirectedGraph::vertex_count() const noexcept { return vertex_count_; }
const std::vector<Edge>& UndirectedGraph::edges() const noexcept { return edges_; }

const std::vector<std::size_t>& UndirectedGraph::neighbors(std::size_t vertex) const {
  if (vertex >= vertex_count_) {
    throw std::out_of_range("vertex out of range");
  }
  return adjacency_[vertex];
}

GraphSummary describe_graph(const UndirectedGraph& graph) {
  return {graph.vertex_count(), graph.edges().size(), graph.edges().size() * 2};
}

std::vector<std::vector<bool>> build_adjacency_matrix(const UndirectedGraph& graph) {
  std::vector<std::vector<bool>> matrix(graph.vertex_count(), std::vector<bool>(graph.vertex_count(), false));
  for (const Edge edge : graph.edges()) {
    matrix[edge.u][edge.v] = true;
    matrix[edge.v][edge.u] = true;
  }
  return matrix;
}

std::vector<std::size_t> degree_sequence(const UndirectedGraph& graph) {
  std::vector<std::size_t> result;
  result.reserve(graph.vertex_count());
  for (std::size_t vertex = 0; vertex < graph.vertex_count(); ++vertex) {
    result.push_back(graph.neighbors(vertex).size());
  }
  return result;
}

bool has_edge(const UndirectedGraph& graph, std::size_t u, std::size_t v) {
  const auto& neighbors_list = graph.neighbors(u);
  static_cast<void>(graph.neighbors(v));
  return std::binary_search(neighbors_list.begin(), neighbors_list.end(), v);
}

BfsTrace breadth_first(const UndirectedGraph& graph, std::size_t start) {
  static_cast<void>(graph.neighbors(start));
  std::vector<std::optional<std::size_t>> distances(graph.vertex_count());
  std::vector<std::optional<std::size_t>> parents(graph.vertex_count());
  distances[start] = 0;
  std::deque<std::size_t> frontier{start};
  std::vector<std::size_t> order;
  std::size_t edge_checks = 0;
  std::size_t max_frontier = 1;
  while (!frontier.empty()) {
    const std::size_t vertex = frontier.front();
    frontier.pop_front();
    order.push_back(vertex);
    for (const std::size_t neighbor : graph.neighbors(vertex)) {
      ++edge_checks;
      if (!distances[neighbor].has_value()) {
        distances[neighbor] = *distances[vertex] + 1;
        parents[neighbor] = vertex;
        frontier.push_back(neighbor);
        max_frontier = std::max(max_frontier, frontier.size());
      }
    }
  }
  return {order, distances, parents, order.size(), edge_checks, max_frontier};
}

PathTrace shortest_path(const UndirectedGraph& graph, std::size_t start, std::size_t target) {
  static_cast<void>(graph.neighbors(target));
  const BfsTrace trace = breadth_first(graph, start);
  if (!trace.distances[target].has_value()) {
    return {{}, std::nullopt};
  }
  std::vector<std::size_t> path;
  std::optional<std::size_t> cursor = target;
  while (cursor.has_value()) {
    path.push_back(*cursor);
    cursor = trace.parents[*cursor];
  }
  std::reverse(path.begin(), path.end());
  return {path, trace.distances[target]};
}

std::vector<std::size_t> reachable_within(const UndirectedGraph& graph, std::size_t start,
                                          std::size_t max_distance) {
  const BfsTrace trace = breadth_first(graph, start);
  std::vector<std::size_t> result;
  for (const std::size_t vertex : trace.order) {
    if (trace.distances[vertex].has_value() && *trace.distances[vertex] <= max_distance) {
      result.push_back(vertex);
    }
  }
  return result;
}

DfsTrace depth_first_components(const UndirectedGraph& graph) {
  std::vector<bool> visited(graph.vertex_count(), false);
  std::vector<std::vector<std::size_t>> components;
  std::size_t visits = 0;
  std::size_t edge_checks = 0;
  int max_depth = -1;
  std::optional<Edge> cycle_edge;

  const auto visit = [&](const auto& self, std::size_t vertex, std::optional<std::size_t> parent, int depth,
                         std::vector<std::size_t>& component) -> void {
    visited[vertex] = true;
    ++visits;
    max_depth = std::max(max_depth, depth);
    component.push_back(vertex);
    for (const std::size_t neighbor : graph.neighbors(vertex)) {
      ++edge_checks;
      if (!visited[neighbor]) {
        self(self, neighbor, vertex, depth + 1, component);
      } else if ((!parent.has_value() || neighbor != *parent) && !cycle_edge.has_value()) {
        cycle_edge = Edge{std::min(vertex, neighbor), std::max(vertex, neighbor)};
      }
    }
  };

  for (std::size_t start = 0; start < graph.vertex_count(); ++start) {
    if (!visited[start]) {
      std::vector<std::size_t> component;
      visit(visit, start, std::nullopt, 0, component);
      components.push_back(std::move(component));
    }
  }
  return {components, visits, edge_checks, max_depth, cycle_edge};
}

ComponentLabels build_component_labels(const UndirectedGraph& graph) {
  const DfsTrace trace = depth_first_components(graph);
  std::vector<std::size_t> labels(graph.vertex_count(), std::numeric_limits<std::size_t>::max());
  for (std::size_t label = 0; label < trace.components.size(); ++label) {
    for (const std::size_t vertex : trace.components[label]) {
      labels[vertex] = label;
    }
  }
  return {labels, trace.components.size()};
}

namespace {

UndirectedGraph sample_graph() {
  const std::vector<Edge> edges{{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {5, 6}};
  return UndirectedGraph(7, edges);
}

template <typename T>
std::string join_values(std::span<const T> values) {
  std::ostringstream output;
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index > 0) {
      output << ", ";
    }
    output << values[index];
  }
  return output.str();
}

std::string join_optional(std::span<const std::optional<std::size_t>> values, const std::string& empty) {
  std::ostringstream output;
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index > 0) {
      output << ", ";
    }
    output << (values[index].has_value() ? std::to_string(*values[index]) : empty);
  }
  return output.str();
}

}  // namespace

std::string build_graph_report() {
  const UndirectedGraph graph = sample_graph();
  const GraphSummary summary = describe_graph(graph);
  std::ostringstream output;
  output << "可追踪无向图实验\n"
         << "vertices=" << summary.vertex_count << "，edges=" << summary.edge_count
         << "，adjacency_entries=" << summary.adjacency_entries;
  for (std::size_t vertex = 0; vertex < graph.vertex_count(); ++vertex) {
    output << '\n' << vertex << "：[" << join_values<std::size_t>(graph.neighbors(vertex)) << ']';
  }
  const std::vector<std::size_t> degrees = degree_sequence(graph);
  output << "\ndegrees：" << join_values<std::size_t>(degrees);
  return output.str();
}

std::string build_bfs_report() {
  const UndirectedGraph graph = sample_graph();
  const BfsTrace trace = breadth_first(graph, 0);
  const PathTrace path = shortest_path(graph, 0, 4);
  std::ostringstream output;
  output << "无权图 BFS\n"
         << "start=0\n"
         << "order：" << join_values<std::size_t>(trace.order) << '\n'
         << "distances：" << join_optional(trace.distances, "unreachable") << '\n'
         << "parents：" << join_optional(trace.parents, "none") << '\n'
         << "visits=" << trace.visits << "，edge_checks=" << trace.edge_checks
         << "，max_frontier=" << trace.max_frontier << '\n'
         << "path 0->4：" << join_values<std::size_t>(path.path) << "，distance=" << *path.distance;
  return output.str();
}

std::string build_dfs_report() {
  const UndirectedGraph graph = sample_graph();
  const DfsTrace trace = depth_first_components(graph);
  const ComponentLabels labels = build_component_labels(graph);
  std::ostringstream output;
  output << "全图 DFS\ncomponents=" << trace.components.size();
  for (std::size_t index = 0; index < trace.components.size(); ++index) {
    output << "\ncomponent " << index << "：" << join_values<std::size_t>(trace.components[index]);
  }
  output << "\nvisits=" << trace.visits << "，edge_checks=" << trace.edge_checks
         << "，max_depth=" << trace.max_depth << '\n'
         << "cycle=" << (trace.cycle_edge.has_value() ? "yes" : "no") << "，first_edge=";
  if (trace.cycle_edge.has_value()) {
    output << '(' << trace.cycle_edge->u << ", " << trace.cycle_edge->v << ')';
  } else {
    output << "none";
  }
  output << "\nlabels：" << join_values<std::size_t>(labels.labels);
  return output.str();
}

}  // namespace traceable_graph_traversal_lab
