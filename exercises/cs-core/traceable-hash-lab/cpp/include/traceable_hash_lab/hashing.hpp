#pragma once

#include <cstddef>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace traceable_hash_lab {

struct BucketEvent {
    int key;
    std::size_t bucket;
    std::size_t chain_before;
    bool collision;
    bool operator==(const BucketEvent&) const = default;
};

struct PutTrace {
    int key;
    std::size_t bucket;
    std::size_t comparisons;
    bool inserted;
    std::optional<std::size_t> rehashed_from;
    std::size_t moved;
};

struct LookupTrace {
    std::optional<int> value;
    std::size_t bucket;
    std::size_t comparisons;
};

struct EraseTrace {
    bool removed;
    std::size_t bucket;
    std::size_t comparisons;
};

struct DuplicateTrace {
    std::optional<int> value;
    std::size_t visits;
    bool operator==(const DuplicateTrace&) const = default;
};

struct FrequencyRow {
    int value;
    std::size_t count;
    bool operator==(const FrequencyRow&) const = default;
};

[[nodiscard]] std::size_t bucket_index(int key, std::ptrdiff_t bucket_count);
[[nodiscard]] std::vector<BucketEvent> trace_bucket_inserts(const std::vector<int>& keys, std::ptrdiff_t bucket_count);
[[nodiscard]] std::vector<std::vector<int>> build_bucket_chains(const std::vector<int>& keys, std::ptrdiff_t bucket_count);
[[nodiscard]] std::optional<BucketEvent> first_collision(const std::vector<int>& keys, std::ptrdiff_t bucket_count);

class TraceableHashMap {
public:
    explicit TraceableHashMap(std::ptrdiff_t bucket_count = 4);

    [[nodiscard]] PutTrace put(int key, int value);
    [[nodiscard]] LookupTrace get(int key) const;
    [[nodiscard]] EraseTrace erase(int key);
    [[nodiscard]] std::size_t size() const noexcept;
    [[nodiscard]] std::size_t bucket_count() const noexcept;
    [[nodiscard]] double load_factor() const noexcept;
    [[nodiscard]] std::vector<std::pair<int, int>> items_sorted() const;

private:
    void rehash(std::size_t new_bucket_count);

    std::vector<std::vector<std::pair<int, int>>> buckets_;
    std::size_t size_ = 0;
};

[[nodiscard]] DuplicateTrace first_duplicate(const std::vector<int>& values);
[[nodiscard]] std::vector<FrequencyRow> count_frequencies(const std::vector<int>& values);
[[nodiscard]] std::vector<int> deduplicate_preserving_order(const std::vector<int>& values);
[[nodiscard]] std::string build_hash_report();
[[nodiscard]] std::string build_table_report();
[[nodiscard]] std::string build_applications_report();

}  // namespace traceable_hash_lab
