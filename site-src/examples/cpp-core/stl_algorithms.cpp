#include <algorithm>
#include <iostream>
#include <iterator>
#include <numeric>
#include <set>
#include <string>
#include <vector>

int main() {
    const std::vector<int> original{2, 5, 3, 4};

    const auto first_large{
        std::find_if(original.begin(), original.end(), [](int value) {
            return value >= 4;
        })
    };
    const auto even_count{
        std::count_if(original.begin(), original.end(), [](int value) {
            return value % 2 == 0;
        })
    };
    const int total{std::accumulate(original.begin(), original.end(), 0)};

    std::vector<int> doubled{};
    doubled.reserve(original.size());
    std::transform(
        original.begin(), original.end(), std::back_inserter(doubled),
        [](int value) { return value * 2; }
    );

    std::vector<int> sorted{original};
    std::sort(sorted.begin(), sorted.end(), std::greater<>{});
    const std::set<std::string> tags{"基础", "工程", "基础"};

    std::cout << "first>=4=" << (first_large != original.end() ? *first_large : -1) << '\n';
    std::cout << "even=" << even_count << '\n';
    std::cout << "total=" << total << '\n';
    std::cout << "doubled=";
    for (int value : doubled) {
        std::cout << value << ' ';
    }
    std::cout << "\nsorted=";
    for (int value : sorted) {
        std::cout << value << ' ';
    }
    std::cout << "\noriginal_first=" << original.front() << '\n';
    std::cout << "unique_tags=" << tags.size() << '\n';
    return 0;
}
