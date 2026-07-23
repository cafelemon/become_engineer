#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

struct Interval { std::string label; int start; int end; };

void validate(const std::vector<Interval>& intervals) {
  for (const auto& item : intervals) {
    if (item.end < item.start) throw std::invalid_argument("invalid interval");
  }
}

std::vector<Interval> select(std::vector<Interval> intervals, bool by_finish) {
  validate(intervals);
  std::sort(intervals.begin(), intervals.end(), [by_finish](const auto& a, const auto& b) {
    if (by_finish) return std::tie(a.end, a.start, a.label) < std::tie(b.end, b.start, b.label);
    return std::tie(a.start, a.end, a.label) < std::tie(b.start, b.end, b.label);
  });
  std::vector<Interval> result;
  for (const auto& item : intervals) {
    if (result.empty() || item.start >= result.back().end) result.push_back(item);
  }
  return result;
}

std::vector<Interval> sample() {
  return {{"A",1,4},{"B",3,5},{"C",0,6},{"D",5,7},{"E",3,9},{"F",5,9},
          {"G",6,10},{"H",8,11},{"I",8,12},{"J",2,14},{"K",12,16}};
}

void print_labels(const std::vector<Interval>& values) {
  for (std::size_t index=0; index<values.size(); ++index) {
    if (index>0) std::cout << ',';
    std::cout << values[index].label;
  }
}

int main() {
  auto intervals=sample();
  auto ordered=intervals;
  std::sort(ordered.begin(), ordered.end(), [](const auto& a,const auto& b){
    return std::tie(a.end,a.start,a.label)<std::tie(b.end,b.start,b.label);
  });
  const auto greedy=select(intervals,true);
  const auto wrong=select(intervals,false);
  std::cout<<"intervals=A[1,4),B[3,5),C[0,6),D[5,7),E[3,9),F[5,9),G[6,10),H[8,11),I[8,12),J[2,14),K[12,16)\n";
  std::cout<<"order_by_finish=";print_labels(ordered);std::cout<<'\n';
  std::cout<<"select=";print_labels(greedy);std::cout<<" count="<<greedy.size()<<'\n';
  std::cout<<"earliest_start_select=";print_labels(wrong);std::cout<<" count="<<wrong.size()<<'\n';
  std::cout<<"exchange=finish-no-later-preserves-room\n";
  std::cout<<"invariant=selected-intervals-nonoverlap\n";
}
