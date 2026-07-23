<div class="be-tutor-mount" data-tutor-lesson="algorithm-deepening-10" aria-hidden="true"></div>
<section id="overview-string-matching" class="be-page-hero be-lesson-hero" data-learning-context="overview-string-matching" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">算法深化 · 第 10 / 10 课 · 可追踪约束模式实验 v1.0</span>
# Trie、KMP 与字符串匹配
## 前缀树共享词典路径，失败函数共享匹配进度
```text
words=to,tea,ten,inn
trie_nodes=9
contains_te=false prefix_te=tea,ten
pattern=ababd prefix=0,0,1,2,0
text=ababcabcabababd matches=10
overlap_aaaaa_aaa=0,1,2
invariants=shared-prefix-path,fallback-keeps-valid-border
```
Trie 回答前缀集合问题；KMP 在线性扫描中复用模式串已知边界。两者都避免重复工作，但状态含义不同。
</section>
<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>算法深化 · 10 / 10</strong></div>
  <div><span>前置</span><strong>树、字符串边界与状态回退</strong></div>
  <div><span>实现</span><strong>Python 3.11 + C++20 Trie/KMP</strong></div>
  <div><span>完成后留下</span><strong>确定性补全、prefix function、重叠匹配与边界测试</strong></div>
</div>
## 学习目标
- 用终止标记区分完整词和仅存在的前缀。
- 解释 Trie 节点为何由共享路径而非词数决定。
- 推导 KMP prefix function 的最长真前后缀语义。
- 失配时回退模式位置而不回退文本位置。
- 完整保留重叠匹配并冻结空模式契约。
<section id="concept-trie-prefix" data-learning-context="concept-trie-prefix" data-context-type="concept" markdown="1">
## Trie 的节点状态是“到这里的字符路径”
插入 `to,tea,ten,inn` 后，根、共享的 `t→e` 路径与分支共形成 9 个节点。`te` 路径存在但没有终止标记，所以 `contains_te=false`；从该节点按字符有序 DFS 得到 `tea,ten`。
重复插入只重设同一终止标记，不新增节点。补全顺序必须显式固定，不能依赖哈希容器遍历。
</section>
<section id="example-kmp-prefix" data-learning-context="example-kmp-prefix" data-context-type="example" markdown="1">
## prefix[i] 保存截至 i 的最长真前后缀长度
模式 `ababd` 的表为 `0,0,1,2,0`。计算新字符时，若与当前候选边界不匹配，就令 `matched=prefix[matched-1]`，退到下一个仍可能成立的边界；文本字符不需要重新扫描。
```text
pattern: a b a b d
prefix : 0 0 1 2 0
```
</section>
<section id="concept-kmp-search" data-learning-context="concept-kmp-search" data-context-type="concept" markdown="1">
## 完整匹配后也要回退到有效边界
文本 `ababcabcabababd` 中模式首次出现在下标 10。找到一次后，将 matched 回退到最后一个 prefix 值，而不是归零，因此 `aaaaa` 中 `aaa` 的重叠匹配 `0,1,2` 全部保留。
KMP 预处理 `O(m)`、扫描 `O(n)`；每次回退缩短 matched，总推进与回退受线性界约束。
</section>
<section id="reproduce-string-v10" data-learning-context="reproduce-string-v10" data-context-type="reproduce" markdown="1">
## 运行共享前缀和失败回退实验
```bash
cd site-src/examples/algorithm-deepening/pattern-lab-v10
../../../../.venv/bin/python -m unittest -v test_string_matching_trace.py
```
6 项测试覆盖完整词/前缀、确定性补全、重复插入、固定 KMP 表、重叠/无匹配、空输入和 Python/C++20 报告一致。
</section>
<section id="modify-string-matching" data-learning-context="modify-string-matching" data-context-type="modify" markdown="1">
## 改变删除、限制和字符边界
1. 为 Trie 增加删除，只有无子节点且非其他词终点的节点才能回收。
2. 给补全增加 limit，并显式报告是否截断。
3. 将 KMP 改为只返回首个匹配，比较输出契约。
4. 输入非 ASCII 文本；明确 Python 按 Unicode 码点、当前 C++ 示例按 UTF-8 字节，不宣称下标单位相同。
</section>
<section id="troubleshoot-string-matching" data-learning-context="troubleshoot-string-matching" data-context-type="troubleshoot" markdown="1">
## 字符串结构按终点、边界和下标单位排错
| 现象 | 原因 | 恢复 |
| --- | --- | --- |
| `te` 被当作完整词 | 只检查路径存在 | 检查 terminal |
| 补全顺序漂移 | 依赖哈希遍历 | 按字符排序 |
| 重复插入增加节点 | 未复用已有边 | 只在边缺失时创建 |
| KMP 失配漏解 | matched 直接归零 | 沿 prefix 链回退 |
| 重叠匹配丢失 | 命中后归零 | 命中后回退到 prefix[m-1] |
| 中英文下标不一致 | 混用码点与 UTF-8 字节 | 明确索引单位或统一解码 |
</section>
<section id="project-pattern-lab-v10" data-learning-context="project-pattern-lab-v10" data-context-type="project" markdown="1">
## 可追踪约束模式实验 v1.0
- 十个版本已覆盖候选消除、窗口、区间、单调结构、回溯、贪心、DP、图与字符串。
- v1.0 固定 Trie 共享节点、词/前缀边界、KMP 表、匹配下标和重叠结果。
- Python/C++20 报告逐字一致；组级验收后算法深化才从建设中切换为已开放。
</section>
## 四类学习者入口
- 零基础兴趣：画出四个词的 Trie 并圈出终止节点。
- 有基础兴趣：实现安全删除和有界补全。
- 零基础求职：手算 `ababd` 的 prefix 表和一次失配回退。
- 有基础求职：解释重叠匹配、线性复杂度与 Unicode 下标边界。
<section id="career-string-matching" data-learning-context="career-string-matching" data-context-type="career" markdown="1">
## 求职加练：共享信息必须有准确语义
原创追问：搜索服务把前缀存在当成完整词，同时 KMP 命中后清零导致漏掉重叠结果。请分别指出 Trie 的终止状态和 KMP 的有效边界，补齐删除、空模式、确定性输出与 Unicode 下标测试。
</section>
## 完成检查
- 6 项测试通过，Python/C++20 报告一致。
- Trie 共 9 节点，`te` 不是词但补全为 `tea,ten`。
- `ababd` 的 prefix 表为 `0,0,1,2,0`，匹配下标为 10。
- `aaaaa` 中 `aaa` 保留下标 `0,1,2`。
- ASCII 固定报告一致；非 ASCII 索引单位边界明确。
## 来源与版本
- Python 3.11、C++20；核查日期 2026-07-23。
- [CP-Algorithms: Trie](https://cp-algorithms.com/string/aho_corasick.html#construction-of-the-trie)
- [CP-Algorithms: Prefix function and KMP](https://cp-algorithms.com/string/prefix-function.html)
## 下一步
执行算法深化十课组级验收；通过后按课程地图进入下一个已满足前置的规划模块。

