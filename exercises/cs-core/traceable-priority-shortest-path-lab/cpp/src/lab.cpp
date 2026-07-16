#include "traceable_priority_shortest_path_lab/lab.hpp"

#include <algorithm>
#include <functional>
#include <limits>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <tuple>
#include <utility>

namespace traceable_priority_shortest_path_lab {
namespace {

std::pair<std::size_t, std::size_t> sift_down(
    std::vector<std::int64_t>& values, std::size_t start) {
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  auto index = start;
  while (true) {
    const auto left = index * 2 + 1;
    if (left >= values.size()) {
      break;
    }
    const auto right = left + 1;
    auto child = left;
    if (right < values.size()) {
      ++comparisons;
      if (values[right] < values[left]) {
        child = right;
      }
    }
    ++comparisons;
    if (!(values[child] < values[index])) {
      break;
    }
    std::swap(values[index], values[child]);
    ++swaps;
    index = child;
  }
  return {comparisons, swaps};
}

bool priority_less(const PriorityEntry& left, const PriorityEntry& right) {
  return std::tie(left.priority, left.sequence) < std::tie(right.priority, right.sequence);
}

std::string join_ints(const std::vector<std::int64_t>& values) {
  std::ostringstream output;
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index > 0) output << ", ";
    output << values[index];
  }
  return output.str();
}

std::string join_vertices(const std::vector<std::size_t>& values) {
  std::ostringstream output;
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index > 0) output << ", ";
    output << values[index];
  }
  return output.str();
}

}  // namespace

bool is_min_heap(const std::vector<std::int64_t>& values) {
  for (std::size_t index = 1; index < values.size(); ++index) {
    if (values[index] < values[(index - 1) / 2]) return false;
  }
  return true;
}

HeapBuildTrace build_min_heap(const std::vector<std::int64_t>& values) {
  auto items = values;
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  for (std::size_t index = items.size() / 2; index > 0; --index) {
    const auto [step_comparisons, step_swaps] = sift_down(items, index - 1);
    comparisons += step_comparisons;
    swaps += step_swaps;
  }
  return {items, comparisons, swaps};
}

HeapMutation TraceableMinHeap::push(std::int64_t value) {
  values_.push_back(value);
  auto index = values_.size() - 1;
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  while (index > 0) {
    const auto parent = (index - 1) / 2;
    ++comparisons;
    if (!(values_[index] < values_[parent])) break;
    std::swap(values_[index], values_[parent]);
    ++swaps;
    index = parent;
  }
  return {value, comparisons, swaps, values_};
}

std::int64_t TraceableMinHeap::peek_min() const {
  if (values_.empty()) throw std::out_of_range("peek from empty heap");
  return values_.front();
}

HeapPop TraceableMinHeap::pop_min() {
  if (values_.empty()) throw std::out_of_range("pop from empty heap");
  const auto value = values_.front();
  const auto last = values_.back();
  values_.pop_back();
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  if (!values_.empty()) {
    values_.front() = last;
    const auto counts = sift_down(values_, 0);
    comparisons = counts.first;
    swaps = counts.second;
  }
  return {value, comparisons, swaps, values_};
}

const std::vector<std::int64_t>& TraceableMinHeap::values() const noexcept { return values_; }
std::size_t TraceableMinHeap::size() const noexcept { return values_.size(); }
bool TraceableMinHeap::empty() const noexcept { return values_.empty(); }

PriorityMutation StableMinPriorityQueue::push(std::string label, std::int64_t priority) {
  PriorityEntry entry{priority, next_sequence_++, std::move(label)};
  entries_.push_back(entry);
  auto index = entries_.size() - 1;
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  while (index > 0) {
    const auto parent = (index - 1) / 2;
    ++comparisons;
    if (!priority_less(entries_[index], entries_[parent])) break;
    std::swap(entries_[index], entries_[parent]);
    ++swaps;
    index = parent;
  }
  return {entry, comparisons, swaps, entries_};
}

const PriorityEntry& StableMinPriorityQueue::peek() const {
  if (entries_.empty()) throw std::out_of_range("peek from empty priority queue");
  return entries_.front();
}

PriorityPop StableMinPriorityQueue::pop() {
  if (entries_.empty()) throw std::out_of_range("pop from empty priority queue");
  const auto entry = entries_.front();
  auto last = entries_.back();
  entries_.pop_back();
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  if (!entries_.empty()) {
    entries_.front() = std::move(last);
    std::size_t index = 0;
    while (true) {
      const auto left = index * 2 + 1;
      if (left >= entries_.size()) break;
      const auto right = left + 1;
      auto child = left;
      if (right < entries_.size()) {
        ++comparisons;
        if (priority_less(entries_[right], entries_[left])) child = right;
      }
      ++comparisons;
      if (!priority_less(entries_[child], entries_[index])) break;
      std::swap(entries_[index], entries_[child]);
      ++swaps;
      index = child;
    }
  }
  return {entry, comparisons, swaps, entries_};
}

const std::vector<PriorityEntry>& StableMinPriorityQueue::entries() const noexcept { return entries_; }
std::size_t StableMinPriorityQueue::size() const noexcept { return entries_.size(); }
bool StableMinPriorityQueue::empty() const noexcept { return entries_.empty(); }

std::vector<PriorityEntry> drain_by_priority(
    const std::vector<std::pair<std::string, std::int64_t>>& tasks) {
  StableMinPriorityQueue queue;
  for (const auto& [label, priority] : tasks) queue.push(label, priority);
  std::vector<PriorityEntry> result;
  while (!queue.empty()) result.push_back(queue.pop().entry);
  return result;
}

WeightedGraph::WeightedGraph(std::size_t vertex_count, const std::vector<WeightedEdge>& edges)
    : vertex_count_(vertex_count), adjacency_(vertex_count) {
  std::vector<std::pair<std::size_t, std::size_t>> seen;
  for (const auto& raw : edges) {
    if (raw.u >= vertex_count || raw.v >= vertex_count) throw std::invalid_argument("edge endpoint out of range");
    if (raw.u == raw.v) throw std::invalid_argument("self-loops are not allowed");
    if (raw.weight < 0) throw std::invalid_argument("edge weight must be non-negative");
    const auto u = std::min(raw.u, raw.v);
    const auto v = std::max(raw.u, raw.v);
    if (std::find(seen.begin(), seen.end(), std::pair{u, v}) != seen.end()) {
      throw std::invalid_argument("duplicate edges are not allowed");
    }
    seen.emplace_back(u, v);
    edges_.push_back({u, v, raw.weight});
  }
  std::sort(edges_.begin(), edges_.end(), [](const WeightedEdge& left, const WeightedEdge& right) {
    return std::tie(left.u, left.v, left.weight) < std::tie(right.u, right.v, right.weight);
  });
  for (const auto& edge : edges_) {
    adjacency_[edge.u].emplace_back(edge.v, edge.weight);
    adjacency_[edge.v].emplace_back(edge.u, edge.weight);
  }
  for (auto& neighbors : adjacency_) std::sort(neighbors.begin(), neighbors.end());
}

std::size_t WeightedGraph::vertex_count() const noexcept { return vertex_count_; }
const std::vector<WeightedEdge>& WeightedGraph::edges() const noexcept { return edges_; }
const std::vector<std::pair<std::size_t, std::int64_t>>& WeightedGraph::neighbors(std::size_t vertex) const {
  check_vertex(vertex);
  return adjacency_[vertex];
}
void WeightedGraph::check_vertex(std::size_t vertex) const {
  if (vertex >= vertex_count_) throw std::out_of_range("vertex out of range");
}

DijkstraTrace dijkstra(const WeightedGraph& graph, std::size_t start) {
  graph.check_vertex(start);
  using QueueEntry = std::tuple<std::int64_t, std::size_t, std::size_t>;
  std::priority_queue<QueueEntry, std::vector<QueueEntry>, std::greater<>> queue;
  std::vector<std::optional<std::int64_t>> distances(graph.vertex_count());
  std::vector<std::optional<std::size_t>> parents(graph.vertex_count());
  distances[start] = 0;
  queue.emplace(0, 0, start);
  std::size_t sequence = 1;
  DijkstraTrace trace{{}, distances, parents, 0, 0, 1, 0, 1, {}};
  while (!queue.empty()) {
    const auto [distance, ignored_sequence, vertex] = queue.top();
    static_cast<void>(ignored_sequence);
    queue.pop();
    if (trace.distances[vertex] != distance) {
      ++trace.stale_pops;
      continue;
    }
    trace.settled.push_back(vertex);
    for (const auto& [neighbor, weight] : graph.neighbors(vertex)) {
      ++trace.edge_checks;
      if (distance > std::numeric_limits<std::int64_t>::max() - weight) {
        throw std::overflow_error("shortest-path distance exceeds signed 64-bit range");
      }
      const auto candidate = distance + weight;
      const auto old_distance = trace.distances[neighbor];
      const bool updated = !old_distance.has_value() || candidate < *old_distance;
      trace.events.push_back({vertex, neighbor, old_distance, candidate, updated});
      if (updated) {
        trace.distances[neighbor] = candidate;
        trace.parents[neighbor] = vertex;
        ++trace.relaxations;
        queue.emplace(candidate, sequence++, neighbor);
        ++trace.queue_pushes;
        trace.max_frontier = std::max(trace.max_frontier, queue.size());
      }
    }
  }
  return trace;
}

WeightedPath shortest_path(const WeightedGraph& graph, std::size_t start, std::size_t target) {
  graph.check_vertex(target);
  const auto trace = dijkstra(graph, start);
  if (!trace.distances[target].has_value()) return {{}, std::nullopt};
  std::vector<std::size_t> path;
  std::optional<std::size_t> current = target;
  while (current.has_value()) {
    path.push_back(*current);
    current = trace.parents[*current];
  }
  std::reverse(path.begin(), path.end());
  return {path, trace.distances[target]};
}

std::vector<std::size_t> vertices_within_distance(
    const WeightedGraph& graph, std::size_t start, std::int64_t max_distance) {
  if (max_distance < 0) throw std::invalid_argument("max_distance must be non-negative");
  const auto trace = dijkstra(graph, start);
  std::vector<std::size_t> result;
  for (const auto vertex : trace.settled) {
    if (trace.distances[vertex].has_value() && *trace.distances[vertex] <= max_distance) {
      result.push_back(vertex);
    }
  }
  return result;
}

WeightedGraph sample_weighted_graph() {
  return WeightedGraph(7, {{0, 1, 4}, {0, 2, 1}, {2, 1, 2}, {1, 3, 1},
                           {2, 3, 5}, {3, 4, 3}, {1, 4, 7}, {4, 5, 1}});
}

std::string build_heap_report() {
  TraceableMinHeap heap;
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  for (const auto value : {7, 3, 9, 1, 5}) {
    const auto event = heap.push(value);
    comparisons += event.comparisons;
    swaps += event.swaps;
  }
  const auto values = heap.values();
  const auto popped = heap.pop_min();
  std::ostringstream output;
  output << "可追踪最小堆\n"
         << "push：7, 3, 9, 1, 5\n"
         << "heap：" << join_ints(values) << "\n"
         << "comparisons=" << comparisons << "，swaps=" << swaps << "\n"
         << "pop_min=" << popped.value << "\n"
         << "remaining：" << join_ints(popped.values) << "\n"
         << "pop_comparisons=" << popped.comparisons << "，pop_swaps=" << popped.swaps;
  return output.str();
}

std::string build_queue_report() {
  StableMinPriorityQueue queue;
  queue.push("review", 2);
  queue.push("test", 1);
  queue.push("lint", 1);
  queue.push("deploy", 3);
  std::ostringstream heap_array;
  for (std::size_t index = 0; index < queue.entries().size(); ++index) {
    if (index > 0) heap_array << ", ";
    heap_array << queue.entries()[index].label << '@' << queue.entries()[index].priority;
  }
  const auto peek = queue.peek();
  std::ostringstream order;
  bool first = true;
  while (!queue.empty()) {
    const auto entry = queue.pop().entry;
    if (!first) order << ", ";
    first = false;
    order << entry.label << '@' << entry.priority;
  }
  std::ostringstream output;
  output << "稳定优先队列\n"
         << "push：review@2, test@1, lint@1, deploy@3\n"
         << "heap_array：" << heap_array.str() << "\n"
         << "peek：" << peek.label << '@' << peek.priority << "\n"
         << "pop_order：" << order.str() << "\n"
         << "equal_priority_fifo=yes";
  return output.str();
}

std::string build_dijkstra_report() {
  const auto graph = sample_weighted_graph();
  const auto trace = dijkstra(graph, 0);
  const auto path = shortest_path(graph, 0, 5);
  std::ostringstream distances;
  std::ostringstream parents;
  for (std::size_t index = 0; index < trace.distances.size(); ++index) {
    if (index > 0) {
      distances << ", ";
      parents << ", ";
    }
    if (trace.distances[index].has_value()) distances << *trace.distances[index];
    else distances << "unreachable";
    if (trace.parents[index].has_value()) parents << *trace.parents[index];
    else parents << "none";
  }
  std::ostringstream output;
  output << "非负权最短路\n"
         << "start=0\n"
         << "settled：" << join_vertices(trace.settled) << "\n"
         << "distances：" << distances.str() << "\n"
         << "parents：" << parents.str() << "\n"
         << "edge_checks=" << trace.edge_checks << "，relaxations=" << trace.relaxations << "\n"
         << "queue_pushes=" << trace.queue_pushes << "，stale_pops=" << trace.stale_pops
         << "，max_frontier=" << trace.max_frontier << "\n"
         << "path 0->5：" << join_vertices(path.path) << "，distance=" << *path.distance;
  return output.str();
}

}  // namespace traceable_priority_shortest_path_lab
