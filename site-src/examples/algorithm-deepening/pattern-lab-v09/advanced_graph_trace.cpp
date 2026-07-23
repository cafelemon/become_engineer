#include <algorithm>
#include <deque>
#include <iostream>
#include <map>
#include <optional>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Edge = std::pair<char,char>;
using Graph = std::map<char,std::vector<char>>;

Graph graph(const std::vector<char>& nodes, const std::vector<Edge>& edges) {
  std::set<char> known(nodes.begin(), nodes.end());
  if (known.size()!=nodes.size()) throw std::invalid_argument("invalid graph");
  Graph result; for(char node:nodes) result[node]={};
  for(auto [left,right]:edges) {
    if(!known.contains(left)||!known.contains(right)) throw std::invalid_argument("invalid graph");
    result[left].push_back(right);
  }
  for(auto& [_,neighbors]:result) std::sort(neighbors.begin(),neighbors.end());
  return result;
}

std::optional<std::vector<char>> topo(const std::vector<char>& nodes,const std::vector<Edge>& edges) {
  auto adjacency=graph(nodes,edges); std::map<char,int> indegree; for(char node:nodes) indegree[node]=0;
  for(auto [_,right]:edges) ++indegree[right];
  std::priority_queue<char,std::vector<char>,std::greater<char>> ready;
  for(char node:nodes) if(indegree[node]==0) ready.push(node);
  std::vector<char> order;
  while(!ready.empty()) { char node=ready.top();ready.pop();order.push_back(node);
    for(char next:adjacency[node]) if(--indegree[next]==0) ready.push(next);
  }
  if(order.size()!=nodes.size()) return std::nullopt; return order;
}

std::vector<std::vector<char>> scc(const std::vector<char>& nodes,const std::vector<Edge>& edges) {
  auto adjacency=graph(nodes,edges); std::vector<Edge> reversed_edges;
  for(auto [left,right]:edges) reversed_edges.push_back({right,left});
  auto reverse=graph(nodes,reversed_edges); std::set<char> seen; std::vector<char> finish;
  const auto visit=[&](const auto& self,char node)->void { seen.insert(node);
    for(char next:adjacency[node]) if(!seen.contains(next)) self(self,next); finish.push_back(node); };
  auto sorted=nodes;std::sort(sorted.begin(),sorted.end());for(char node:sorted)if(!seen.contains(node))visit(visit,node);
  seen.clear();std::vector<std::vector<char>> components;
  const auto collect=[&](const auto& self,char node,std::vector<char>& current)->void {seen.insert(node);current.push_back(node);
    for(char next:reverse[node])if(!seen.contains(next))self(self,next,current);};
  for(auto iterator=finish.rbegin();iterator!=finish.rend();++iterator)if(!seen.contains(*iterator)){std::vector<char> current;collect(collect,*iterator,current);std::sort(current.begin(),current.end());components.push_back(current);}
  std::sort(components.begin(),components.end(),[](const auto& a,const auto& b){return a.front()<b.front();});return components;
}

std::set<std::pair<int,int>> condensation(const std::vector<std::vector<char>>& components,const std::vector<Edge>& edges) {
  std::map<char,int> owner;for(std::size_t index=0;index<components.size();++index)for(char node:components[index])owner[node]=static_cast<int>(index);
  std::set<std::pair<int,int>> result;for(auto [left,right]:edges)if(owner[left]!=owner[right])result.insert({owner[left],owner[right]});return result;
}

std::map<char,int> multi_source(const std::vector<char>& nodes,const std::vector<Edge>& edges,const std::vector<char>& sources) {
  auto adjacency=graph(nodes,edges);if(sources.empty())throw std::invalid_argument("invalid sources");
  std::map<char,int> distance;for(char node:nodes)distance[node]=-1;std::set<char> unique(sources.begin(),sources.end());std::deque<char> queue;
  for(char source:unique){if(!distance.contains(source))throw std::invalid_argument("invalid sources");distance[source]=0;queue.push_back(source);}
  while(!queue.empty()){char node=queue.front();queue.pop_front();for(char next:adjacency[node])if(distance[next]<0){distance[next]=distance[node]+1;queue.push_back(next);}}
  return distance;
}

template<class T>void print_chars(const T& values){bool first=true;for(char value:values){if(!first)std::cout<<',';first=false;std::cout<<value;}}

int main(){
  const std::vector<char> nodes{'A','B','C','D','E','F'};
  const std::vector<Edge> dag{{'A','C'},{'B','C'},{'C','D'},{'C','E'},{'D','F'},{'E','F'}};
  const std::vector<Edge> cyclic{{'A','B'},{'B','C'},{'C','A'},{'C','D'},{'D','E'},{'E','D'},{'E','F'}};
  const auto order=topo(nodes,dag);const auto components=scc(nodes,cyclic);const auto condensed=condensation(components,cyclic);const auto distances=multi_source(nodes,dag,{'A','B'});
  std::cout<<"dag_edges=A>C,B>C,C>D,C>E,D>F,E>F\n";
  std::cout<<"topological=";print_chars(*order);std::cout<<"\ncycle_topological="<<(topo(nodes,cyclic)?"unexpected":"cycle")<<"\n";
  std::cout<<"scc_edges=A>B,B>C,C>A,C>D,D>E,E>D,E>F\nscc=";
  for(std::size_t index=0;index<components.size();++index){if(index)std::cout<<'|';print_chars(components[index]);}
  std::cout<<"\ncondensation=";bool first=true;for(auto [left,right]:condensed){if(!first)std::cout<<',';first=false;std::cout<<left<<'>'<<right;}
  std::cout<<"\nsources=A,B distances=";first=true;for(char node:nodes){if(!first)std::cout<<',';first=false;std::cout<<node<<':'<<distances.at(node);}
  std::cout<<"\ninvariants=zero-indegree-only,scc-condensation-acyclic,first-discovery-shortest\n";
}

