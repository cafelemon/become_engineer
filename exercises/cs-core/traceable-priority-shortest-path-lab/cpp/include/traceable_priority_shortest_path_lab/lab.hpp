#pragma once

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace traceable_priority_shortest_path_lab {

struct HeapMutation {
  std::int64_t value;
  std::size_t comparisons;
  std::size_t swaps;
  std::vector<std::int64_t> values;
};

struct HeapPop {
  std::int64_t value;
  std::size_t comparisons;
  std::size_t swaps;
  std::vector<std::int64_t> values;
};

struct HeapBuildTrace {
  std::vector<std::int64_t> values;
  std::size_t comparisons;
  std::size_t swaps;
};

bool is_min_heap(const std::vector<std::int64_t>& values);
HeapBuildTrace build_min_heap(const std::vector<std::int64_t>& values);

class TraceableMinHeap {
 public:
  HeapMutation push(std::int64_t value);
  std::int64_t peek_min() const;
  HeapPop pop_min();
  const std::vector<std::int64_t>& values() const noexcept;
  std::size_t size() const noexcept;
  bool empty() const noexcept;

 private:
  std::vector<std::int64_t> values_;
};

struct PriorityEntry {
  std::int64_t priority;
  std::size_t sequence;
  std::string label;
};

struct PriorityMutation {
  PriorityEntry entry;
  std::size_t comparisons;
  std::size_t swaps;
  std::vector<PriorityEntry> entries;
};

struct PriorityPop {
  PriorityEntry entry;
  std::size_t comparisons;
  std::size_t swaps;
  std::vector<PriorityEntry> entries;
};

class StableMinPriorityQueue {
 public:
  PriorityMutation push(std::string label, std::int64_t priority);
  const PriorityEntry& peek() const;
  PriorityPop pop();
  const std::vector<PriorityEntry>& entries() const noexcept;
  std::size_t size() const noexcept;
  bool empty() const noexcept;

 private:
  std::vector<PriorityEntry> entries_;
  std::size_t next_sequence_{0};
};

std::vector<PriorityEntry> drain_by_priority(
    const std::vector<std::pair<std::string, std::int64_t>>& tasks);

struct WeightedEdge {
  std::size_t u;
  std::size_t v;
  std::int64_t weight;
};

class WeightedGraph {
 public:
  WeightedGraph(std::size_t vertex_count, const std::vector<WeightedEdge>& edges);
  std::size_t vertex_count() const noexcept;
  const std::vector<WeightedEdge>& edges() const noexcept;
  const std::vector<std::pair<std::size_t, std::int64_t>>& neighbors(std::size_t vertex) const;
  void check_vertex(std::size_t vertex) const;

 private:
  std::size_t vertex_count_;
  std::vector<WeightedEdge> edges_;
  std::vector<std::vector<std::pair<std::size_t, std::int64_t>>> adjacency_;
};

struct RelaxationEvent {
  std::size_t from_vertex;
  std::size_t to_vertex;
  std::optional<std::int64_t> old_distance;
  std::int64_t candidate;
  bool updated;
};

struct DijkstraTrace {
  std::vector<std::size_t> settled;
  std::vector<std::optional<std::int64_t>> distances;
  std::vector<std::optional<std::size_t>> parents;
  std::size_t edge_checks;
  std::size_t relaxations;
  std::size_t queue_pushes;
  std::size_t stale_pops;
  std::size_t max_frontier;
  std::vector<RelaxationEvent> events;
};

struct WeightedPath {
  std::vector<std::size_t> path;
  std::optional<std::int64_t> distance;
};

DijkstraTrace dijkstra(const WeightedGraph& graph, std::size_t start);
WeightedPath shortest_path(const WeightedGraph& graph, std::size_t start, std::size_t target);
std::vector<std::size_t> vertices_within_distance(
    const WeightedGraph& graph, std::size_t start, std::int64_t max_distance);
WeightedGraph sample_weighted_graph();

std::string build_heap_report();
std::string build_queue_report();
std::string build_dijkstra_report();

}  // namespace traceable_priority_shortest_path_lab
