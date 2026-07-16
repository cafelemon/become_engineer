#include "traceable_hash_lab/hashing.hpp"

#include <algorithm>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>

namespace traceable_hash_lab {

namespace {

std::string join(const std::vector<int>& values) {
    std::ostringstream output;
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index > 0) {
            output << ", ";
        }
        output << values[index];
    }
    return output.str();
}

}  // namespace

std::size_t bucket_index(const int key, const std::ptrdiff_t bucket_count) {
    if (bucket_count <= 0) {
        throw std::invalid_argument("bucket_count must be positive");
    }
    if (key < 0) {
        throw std::invalid_argument("teaching hash only accepts non-negative keys");
    }
    return static_cast<std::size_t>(key) % static_cast<std::size_t>(bucket_count);
}

std::vector<std::vector<int>> build_bucket_chains(const std::vector<int>& keys, const std::ptrdiff_t bucket_count) {
    if (bucket_count <= 0) {
        throw std::invalid_argument("bucket_count must be positive");
    }
    std::vector<std::vector<int>> chains(static_cast<std::size_t>(bucket_count));
    for (const int key : keys) {
        chains[bucket_index(key, bucket_count)].push_back(key);
    }
    return chains;
}

std::vector<BucketEvent> trace_bucket_inserts(const std::vector<int>& keys, const std::ptrdiff_t bucket_count) {
    auto chains = build_bucket_chains({}, bucket_count);
    std::vector<BucketEvent> events;
    events.reserve(keys.size());
    for (const int key : keys) {
        const auto bucket = bucket_index(key, bucket_count);
        const auto chain_before = chains[bucket].size();
        events.push_back({key, bucket, chain_before, chain_before > 0});
        chains[bucket].push_back(key);
    }
    return events;
}

std::optional<BucketEvent> first_collision(const std::vector<int>& keys, const std::ptrdiff_t bucket_count) {
    for (const auto& event : trace_bucket_inserts(keys, bucket_count)) {
        if (event.collision) {
            return event;
        }
    }
    return std::nullopt;
}

TraceableHashMap::TraceableHashMap(const std::ptrdiff_t bucket_count) {
    if (bucket_count <= 0) {
        throw std::invalid_argument("bucket_count must be positive");
    }
    buckets_.resize(static_cast<std::size_t>(bucket_count));
}

PutTrace TraceableHashMap::put(const int key, const int value) {
    auto bucket = bucket_index(key, static_cast<std::ptrdiff_t>(bucket_count()));
    auto* chain = &buckets_[bucket];
    std::size_t comparisons = 0;
    for (auto& item : *chain) {
        ++comparisons;
        if (item.first == key) {
            item.second = value;
            return {key, bucket, comparisons, false, std::nullopt, 0};
        }
    }

    std::optional<std::size_t> rehashed_from;
    std::size_t moved = 0;
    if (size_ + 1 > bucket_count()) {
        rehashed_from = bucket_count();
        moved = size_;
        rehash(bucket_count() * 2);
        bucket = bucket_index(key, static_cast<std::ptrdiff_t>(bucket_count()));
        chain = &buckets_[bucket];
        comparisons = 0;
        for (const auto& item : *chain) {
            ++comparisons;
            if (item.first == key) {
                throw std::logic_error("new key unexpectedly appeared during rehash");
            }
        }
    }

    chain->emplace_back(key, value);
    ++size_;
    return {key, bucket, comparisons, true, rehashed_from, moved};
}

LookupTrace TraceableHashMap::get(const int key) const {
    const auto bucket = bucket_index(key, static_cast<std::ptrdiff_t>(bucket_count()));
    std::size_t comparisons = 0;
    for (const auto& [stored_key, value] : buckets_[bucket]) {
        ++comparisons;
        if (stored_key == key) {
            return {value, bucket, comparisons};
        }
    }
    return {std::nullopt, bucket, comparisons};
}

EraseTrace TraceableHashMap::erase(const int key) {
    const auto bucket = bucket_index(key, static_cast<std::ptrdiff_t>(bucket_count()));
    auto& chain = buckets_[bucket];
    std::size_t comparisons = 0;
    for (auto iterator = chain.begin(); iterator != chain.end(); ++iterator) {
        ++comparisons;
        if (iterator->first == key) {
            chain.erase(iterator);
            --size_;
            return {true, bucket, comparisons};
        }
    }
    return {false, bucket, comparisons};
}

std::size_t TraceableHashMap::size() const noexcept { return size_; }

std::size_t TraceableHashMap::bucket_count() const noexcept { return buckets_.size(); }

double TraceableHashMap::load_factor() const noexcept {
    return static_cast<double>(size_) / static_cast<double>(bucket_count());
}

std::vector<std::pair<int, int>> TraceableHashMap::items_sorted() const {
    std::vector<std::pair<int, int>> items;
    items.reserve(size_);
    for (const auto& chain : buckets_) {
        items.insert(items.end(), chain.begin(), chain.end());
    }
    std::sort(items.begin(), items.end());
    return items;
}

void TraceableHashMap::rehash(const std::size_t new_bucket_count) {
    auto old_buckets = std::move(buckets_);
    buckets_ = std::vector<std::vector<std::pair<int, int>>>(new_bucket_count);
    for (const auto& chain : old_buckets) {
        for (const auto& item : chain) {
            buckets_[bucket_index(item.first, static_cast<std::ptrdiff_t>(new_bucket_count))].push_back(item);
        }
    }
}

DuplicateTrace first_duplicate(const std::vector<int>& values) {
    std::unordered_set<int> seen;
    std::size_t visits = 0;
    for (const int value : values) {
        ++visits;
        if (seen.contains(value)) {
            return {value, visits};
        }
        seen.insert(value);
    }
    return {std::nullopt, visits};
}

std::vector<FrequencyRow> count_frequencies(const std::vector<int>& values) {
    std::unordered_map<int, std::size_t> counts;
    for (const int value : values) {
        ++counts[value];
    }
    std::vector<FrequencyRow> rows;
    rows.reserve(counts.size());
    for (const auto& [value, count] : counts) {
        rows.push_back({value, count});
    }
    std::sort(rows.begin(), rows.end(), [](const auto& left, const auto& right) { return left.value < right.value; });
    return rows;
}

std::vector<int> deduplicate_preserving_order(const std::vector<int>& values) {
    std::unordered_set<int> seen;
    std::vector<int> result;
    for (const int value : values) {
        if (seen.insert(value).second) {
            result.push_back(value);
        }
    }
    return result;
}

std::string build_hash_report() {
    const std::vector<int> keys{1, 5, 9, 2};
    constexpr std::ptrdiff_t bucket_count = 4;
    std::ostringstream output;
    output << "可追踪哈希实验\n"
           << "bucket_count=4\n"
           << "key | bucket | chain_before | collision\n";
    for (const auto& event : trace_bucket_inserts(keys, bucket_count)) {
        output << event.key << " | " << event.bucket << " | " << event.chain_before << " | "
               << (event.collision ? "yes" : "no") << '\n';
    }
    const auto buckets = build_bucket_chains(keys, bucket_count);
    output << "buckets：";
    for (std::size_t index = 0; index < buckets.size(); ++index) {
        if (index > 0) {
            output << ' ';
        }
        output << index << "=[" << join(buckets[index]) << ']';
    }
    return output.str();
}

std::string build_table_report() {
    TraceableHashMap table;
    std::ostringstream output;
    output << "分离链接哈希表\n";
    for (const auto& [key, value] : std::vector<std::pair<int, int>>{{1, 10}, {5, 50}, {9, 90}, {2, 20}, {13, 130}}) {
        const auto trace = table.put(key, value);
        output << "put " << key << '=' << value << "：inserted=" << (trace.inserted ? "yes" : "no")
               << "，bucket=" << trace.bucket << "，comparisons=" << trace.comparisons;
        if (trace.rehashed_from.has_value()) {
            output << "，rehash=" << *trace.rehashed_from << "->" << table.bucket_count() << "，moved=" << trace.moved;
        }
        output << '\n';
    }
    const auto lookup = table.get(9);
    output << "get 9：value=" << *lookup.value << "，bucket=" << lookup.bucket << "，comparisons=" << lookup.comparisons << '\n';
    output << "size=" << table.size() << "，buckets=" << table.bucket_count() << "，load_factor="
           << std::fixed << std::setprecision(3) << table.load_factor();
    return output.str();
}

std::string build_applications_report() {
    const std::vector<int> values{7, 3, 7, 9, 3};
    const auto duplicate = first_duplicate(values);
    const auto unique = deduplicate_preserving_order(values);
    const auto frequencies = count_frequencies(values);
    std::ostringstream output;
    output << "集合与频次映射\n"
           << "data：" << join(values) << '\n'
           << "first_duplicate=" << *duplicate.value << "，visits=" << duplicate.visits << '\n'
           << "unique_in_order：" << join(unique) << '\n'
           << "frequencies：";
    for (std::size_t index = 0; index < frequencies.size(); ++index) {
        if (index > 0) {
            output << ", ";
        }
        output << frequencies[index].value << '=' << frequencies[index].count;
    }
    return output.str();
}

}  // namespace traceable_hash_lab
