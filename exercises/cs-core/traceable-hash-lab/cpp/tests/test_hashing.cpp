#include "traceable_hash_lab/hashing.hpp"

#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

void require(const bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

template <typename Function>
void require_throws(Function function, const std::string& message) {
    try {
        function();
    } catch (const std::invalid_argument&) {
        return;
    }
    throw std::runtime_error(message);
}

void test_buckets() {
    using namespace traceable_hash_lab;
    require(bucket_index(9, 4) == 1, "bucket index");
    require_throws([] { static_cast<void>(bucket_index(1, 0)); }, "zero bucket count");
    require_throws([] { static_cast<void>(bucket_index(1, -1)); }, "negative bucket count");
    require_throws([] { static_cast<void>(bucket_index(-1, 4)); }, "negative key");
    require_throws([] { static_cast<void>(TraceableHashMap(-1)); }, "negative table bucket count");
    const std::vector<int> keys{1, 5, 9, 2};
    const std::vector<BucketEvent> expected{{1, 1, 0, false}, {5, 1, 1, true}, {9, 1, 2, true}, {2, 2, 0, false}};
    require(trace_bucket_inserts(keys, 4) == expected, "collision events");
    const std::vector<std::vector<int>> chains{{}, {1, 5, 9}, {2}, {}};
    require(build_bucket_chains(keys, 4) == chains, "bucket chains");
    require(first_collision(keys, 4) == std::optional<BucketEvent>{{5, 1, 1, true}}, "first collision");
    require(!first_collision({}, 4).has_value(), "empty first collision");
}

void test_table() {
    using namespace traceable_hash_lab;
    TraceableHashMap table;
    require(table.put(1, 10).comparisons == 0, "first insert");
    require(table.put(5, 50).comparisons == 1, "collision comparison");
    const auto update = table.put(5, 55);
    require(!update.inserted && update.comparisons == 2 && table.size() == 2, "update contract");
    require(table.get(5).value == std::optional<int>{55}, "lookup updated value");
    require(table.get(9).comparisons == 2, "missing lookup comparisons");
    require(table.items_sorted() == std::vector<std::pair<int, int>>{{1, 10}, {5, 55}}, "sorted items");

    TraceableHashMap growing;
    for (const int key : std::vector<int>{1, 5, 9, 2}) {
        static_cast<void>(growing.put(key, key * 10));
    }
    const auto growth = growing.put(13, 130);
    require(growth.bucket == 5 && growth.comparisons == 1, "post-rehash insert trace");
    require(growth.rehashed_from == std::optional<std::size_t>{4} && growth.moved == 4, "rehash trace");
    require(growing.bucket_count() == 8 && growing.size() == 5, "rehash state");
    for (const int key : std::vector<int>{1, 5, 9, 2, 13}) {
        require(growing.get(key).value == std::optional<int>{key * 10}, "rehash lookup");
    }

    TraceableHashMap erasing(2);
    require(!erasing.put(0, 0).rehashed_from.has_value(), "first load boundary");
    require(!erasing.put(2, 20).rehashed_from.has_value(), "exact load boundary");
    const auto before = erasing.items_sorted();
    const auto missing = erasing.erase(4);
    require(!missing.removed && missing.comparisons == 2 && erasing.items_sorted() == before, "missing erase stability");
    const auto removed = erasing.erase(2);
    require(removed.removed && removed.comparisons == 2, "successful erase");
}

void test_applications() {
    using namespace traceable_hash_lab;
    require(first_duplicate({}) == DuplicateTrace{std::nullopt, 0}, "empty duplicate");
    require(first_duplicate({1, 2, 3}) == DuplicateTrace{std::nullopt, 3}, "no duplicate");
    require(first_duplicate({1, 1, 2}) == DuplicateTrace{1, 2}, "early duplicate");
    require(first_duplicate({1, 2, 3, 1}) == DuplicateTrace{1, 4}, "late duplicate");
    const std::vector<int> values{7, -1, 7, 3, -1};
    const auto original = values;
    const std::vector<FrequencyRow> rows{{-1, 2}, {3, 1}, {7, 2}};
    require(count_frequencies(values) == rows, "frequency sorting");
    require(deduplicate_preserving_order(values) == std::vector<int>{7, -1, 3}, "stable deduplication");
    require(values == original, "input unchanged");
}

void test_reports() {
    using namespace traceable_hash_lab;
    const std::string hash_report = "可追踪哈希实验\nbucket_count=4\nkey | bucket | chain_before | collision\n1 | 1 | 0 | no\n5 | 1 | 1 | yes\n9 | 1 | 2 | yes\n2 | 2 | 0 | no\nbuckets：0=[] 1=[1, 5, 9] 2=[2] 3=[]";
    const std::string table_report = "分离链接哈希表\nput 1=10：inserted=yes，bucket=1，comparisons=0\nput 5=50：inserted=yes，bucket=1，comparisons=1\nput 9=90：inserted=yes，bucket=1，comparisons=2\nput 2=20：inserted=yes，bucket=2，comparisons=0\nput 13=130：inserted=yes，bucket=5，comparisons=1，rehash=4->8，moved=4\nget 9：value=90，bucket=1，comparisons=2\nsize=5，buckets=8，load_factor=0.625";
    const std::string applications_report = "集合与频次映射\ndata：7, 3, 7, 9, 3\nfirst_duplicate=7，visits=3\nunique_in_order：7, 3, 9\nfrequencies：3=2, 7=2, 9=1";
    require(build_hash_report() == hash_report, "hash report");
    require(build_table_report() == table_report, "table report");
    require(build_applications_report() == applications_report, "applications report");
}

}  // namespace

int main() {
    try {
        test_buckets();
        test_table();
        test_applications();
        test_reports();
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}
