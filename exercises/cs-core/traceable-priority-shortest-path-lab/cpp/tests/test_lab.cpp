#include "traceable_priority_shortest_path_lab/lab.hpp"

#include <cassert>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using namespace traceable_priority_shortest_path_lab;

int main() {
  TraceableMinHeap heap;
  std::size_t comparisons = 0;
  std::size_t swaps = 0;
  for (const auto value : {7, 3, 9, 1, 5}) {
    const auto event = heap.push(value);
    comparisons += event.comparisons;
    swaps += event.swaps;
  }
  assert((heap.values() == std::vector<std::int64_t>{1, 3, 9, 7, 5}));
  assert(comparisons == 5 && swaps == 3);
  const auto popped = heap.pop_min();
  assert(popped.value == 1 && popped.comparisons == 3 && popped.swaps == 1);
  assert(is_min_heap(build_min_heap({9, -1, 7, -1, 3, 2}).values));
  assert(!is_min_heap({2, 1, 3}));

  StableMinPriorityQueue empty_queue;
  try {
    static_cast<void>(empty_queue.pop());
    assert(false);
  } catch (const std::out_of_range&) {
    assert(empty_queue.empty());
  }
  const auto drained = drain_by_priority({{"same", 1}, {"same", 1}, {"urgent", -1}, {"later", 2}});
  assert(drained[0].label == "urgent");
  assert(drained[1].sequence == 0 && drained[2].sequence == 1);

  const auto graph = sample_weighted_graph();
  const auto trace = dijkstra(graph, 0);
  assert((trace.settled == std::vector<std::size_t>{0, 2, 1, 3, 4, 5}));
  assert(trace.edge_checks == 16 && trace.relaxations == 8);
  assert(trace.queue_pushes == 9 && trace.stale_pops == 3 && trace.max_frontier == 4);
  assert((shortest_path(graph, 0, 5).path == std::vector<std::size_t>{0, 2, 1, 3, 4, 5}));
  assert(shortest_path(graph, 0, 6).path.empty());
  assert((vertices_within_distance(graph, 0, 4) == std::vector<std::size_t>{0, 2, 1, 3}));

  try {
    static_cast<void>(WeightedGraph(2, {{0, 1, -1}}));
    assert(false);
  } catch (const std::invalid_argument&) {
  }
  try {
    const auto overflow_graph = WeightedGraph(
        3, {{0, 1, std::numeric_limits<std::int64_t>::max()}, {1, 2, 1}});
    static_cast<void>(dijkstra(overflow_graph, 0));
    assert(false);
  } catch (const std::overflow_error&) {
  }

  assert(build_heap_report().find("comparisons=5，swaps=3") != std::string::npos);
  assert(build_queue_report().find("equal_priority_fifo=yes") != std::string::npos);
  assert(build_dijkstra_report().find("stale_pops=3，max_frontier=4") != std::string::npos);
  return 0;
}
