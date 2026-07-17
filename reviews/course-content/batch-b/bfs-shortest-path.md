# BFS：无权图中的最少步数

<div class="be-sample-tutor-mount" data-tutor-context-lesson="sample-bfs-shortest-path" aria-hidden="true"></div>

<section id="overview-bfs-path" class="be-sample-hero" data-learning-context="overview-bfs-path" data-context-type="overview" markdown="1">

<span class="be-sample-kicker">算法样板 · 可追踪图遍历实验</span>

## 从 A 到 E，至少经过几条边

```text
A ─ B ─ D ─ E
└─ C ─┘

一条最短路径：A → B → D → E
距离：3
```

先不用代码。拿纸画出这张图，从 A 开始一层一层向外找。BFS 做的就是把这个过程记得足够清楚，让程序最后还能把路径还原出来。

<div class="be-sample-actions" markdown="1">
[跟着队列走一遍](#concept-bfs-queue){ .md-button .md-button--primary }
[直接运行代码](#reproduce-bfs-code){ .md-button }
</div>

</section>

<section id="concept-bfs-queue" class="be-sample-learning-unit" data-learning-context="concept-bfs-queue" data-context-type="concept" markdown="1">

## 队列让搜索按层推进

队列遵守“先进入，先出来”。A 的邻居 B、C 会先于更远的 D、E 被处理，所以第一次发现某个点时，就已经走过了最少的边数。

<div class="be-trace-demo" data-trace-demo="bfs" aria-label="BFS 队列、距离和父节点单步演示"></div>

??? info "没有 JavaScript 时的完整轨迹"
    | 时刻 | 取出 | 队列 | 新发现 | 父节点 |
    | --- | --- | --- | --- | --- |
    | 0 | — | A | A | A←无 |
    | 1 | A | B,C | B,C | B←A，C←A |
    | 2 | B | C,D | D | D←B |
    | 3 | C | D | 无 | D 不改变 |
    | 4 | D | E | E | E←D |
    | 5 | E | 空 | 无 | 结束 |

关键点在“发现邻居时就标记”。如果等到出队才标记，B 和 C 都可能把 D 放进队列。

</section>

<section id="example-bfs-parent" class="be-sample-learning-unit" data-learning-context="example-bfs-parent" data-context-type="example" markdown="1">

## 距离回答多远，父节点负责找回来

第一次从 `current` 发现 `neighbor` 时记录：

```python
parent[neighbor] = current
queue.append(neighbor)
```

搜索结束后，从 E 沿父节点倒着走：

```text
E ← D ← B ← A
```

反转以后就是 `A → B → D → E`。如果目标从未进入 `parent`，它不可达，应该返回空路径，而不是硬凑一条路线。

</section>

<section id="reproduce-bfs-code" class="be-sample-learning-unit" data-learning-context="reproduce-bfs-code" data-context-type="reproduce" markdown="1">

## 跑一下最小实现

```python
from collections import deque

def shortest_path(graph, start, target):
    queue = deque([start])
    parent = {start: None}
    while queue:
        current = queue.popleft()
        if current == target:
            break
        for neighbor in graph[current]:
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)

    if target not in parent:
        return []

    path = []
    cursor = target
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    return list(reversed(path))
```

本地运行完整样例：

```bash
python3 reviews/course-content/batch-b/examples/bfs/bfs_demo.py
```

预期输出：

```text
path A->E: A -> B -> D -> E
path A->F: []
```

</section>

<section id="modify-bfs-graph" class="be-sample-learning-unit" data-learning-context="modify-bfs-graph" data-context-type="modify" markdown="1">

## 改一条边，先别急着运行

在图中增加 `C-E`。先在纸上判断 A 到 E 的距离和路径会怎样变化，再修改邻接表：

```python
"C": ["A", "D", "E"],
"E": ["C", "D"],
```

如果邻接点顺序固定，程序会稳定返回 `A → C → E`，距离变成 2。这里要同时修改无向图的两边，不能只给 C 添加 E。

</section>

<section id="troubleshoot-bfs-mark" class="be-sample-learning-unit" data-learning-context="troubleshoot-bfs-mark" data-context-type="troubleshoot" markdown="1">

## 为什么要在入队时记住它

把“记录父节点”推迟到出队，会让 D 被 B 和 C 重复加入。小图可能还能结束，但队列更大，父节点也可能被后来的路径改写。

另一个常见误用是把 BFS 直接搬到带权图。BFS 保证的是最少边数；如果一条边耗时 1 分钟，另一条边耗时 30 分钟，边数少不一定总耗时少。

| 现象 | 先检查 |
| --- | --- |
| 同一点多次入队 | 是否在入队前就写入 `parent` |
| 不可达点得到距离 0 | 是否把“未发现”和起点混在一起 |
| 每次路径不同 | 邻接点遍历顺序是否固定 |
| 带权图答案不对 | 问题是否已经超出 BFS 的适用条件 |

</section>

<section id="project-traceable-bfs" class="be-sample-project-panel" data-learning-context="project-traceable-bfs" data-context-type="project" markdown="1">

## 接回可追踪图遍历实验

正式实验同时提供 Python 与 C++ 实现，并继续记录访问顺序、距离、父节点、边检查数和最大队列。这个样板先把最容易卡住的队列过程讲清楚，再回到完整实验比较两种语言。

[查看现有双语言实验](../../../exercises/cs-core/traceable-graph-traversal-lab/README.md){ .md-button }

</section>

??? info "再深入一点：复杂度从哪里来"
    使用邻接表时，每个可达顶点最多入队一次，每条相关邻接项被扫描一次，因此完整遍历是 `Theta(V + E)`。路径恢复只沿父链走，长度最多为 `V`。

## 完成检查

- [ ] 能用纸和队列追踪 A 到 E 的搜索过程。
- [ ] 能解释为什么要在入队时标记。
- [ ] 能用父节点恢复路径，并处理不可达目标。
- [ ] 能改一条边，先预测再运行。
- [ ] 能说清 BFS 最短路径对边权的要求。

下一页：[对象生命周期与 RAII](cpp-raii.md)。
