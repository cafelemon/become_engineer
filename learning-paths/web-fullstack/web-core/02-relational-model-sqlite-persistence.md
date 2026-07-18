<div class="be-tutor-mount" data-tutor-lesson="web-core-02" aria-hidden="true"></div>

<section id="overview-restart-keeps-data" class="be-page-hero be-lesson-hero" data-learning-context="overview-restart-keeps-data" data-context-type="overview" markdown="1">

<span class="be-page-eyebrow">Web 核心 · 第二课 · 学习进度报告器 Web v0.6</span>

# 关系模型、SQLite 与持久化边界

## 服务停了再开，刚才的 1 小时还在

```text
第一次读取      7.5 小时
保存一次        +1.0 小时 → HTTP 201
停止 Uvicorn
重新启动服务
再次读取        8.5 小时
```

v0.5 把数据放在 Python 字典里，进程一停，临时改动就消失。v0.6 把学习者和学习时段写进一个 SQLite 文件。服务可以重启，页面仍能重新算出 8.5 小时。

<div class="be-page-actions" markdown="1">
[先看数据放在哪里](#concept-memory-and-disk){ .md-button .md-button--primary }
[运行 v0.6](#reproduce-dashboard-v06){ .md-button }
</div>

</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Web 核心 · 2 / 4</strong></div>
  <div><span>开始条件</span><strong>完成 Web v0.5，能运行 FastAPI 与 TypeScript</strong></div>
  <div><span>完成后留下</span><strong>两个关系表、持久化写入、回滚测试与重启记录</strong></div>
</div>

## 开始前

- **第一次学数据库**：按顺序完成关系图、短 SQL 和本地复现。这里不要求先学完整数据库原理，也不使用 ORM。
- **已有基础**：先做跳过检查——能设计主键和外键、始终使用占位符、证明失败事务没有留下半条数据，并解释 SQLite 适合这个项目的原因。都能做到，可以直接进入下一课 REST 资源设计。
- **兴趣画像**：完成正文、项目修改和重启检查即可。
- **求职画像**：再保留一次回滚测试输出，并完成末尾的项目追问。四类画像使用同一份 v0.6 代码。
- **环境**：Python 3.11+、标准库 `sqlite3`、FastAPI、Node.js 24 LTS、TypeScript 7.0.2。SQLite 不需要另起一个数据库服务。

<section id="concept-memory-and-disk" data-learning-context="concept-memory-and-disk" data-context-type="concept" markdown="1">

## 内存字典和数据库文件差在哪

v0.5 的数据跟着 Python 进程生活：

```text
浏览器 → FastAPI 进程 → SUMMARIES 字典
                         └─ 进程结束，临时修改消失
```

v0.6 多了一层磁盘存储：

```text
浏览器 → FastAPI → LearningDatabase → data/learning.sqlite3
                    每次短暂连接       进程重启后仍保留
```

“持久化”不是数据永远不会丢，而是数据的寿命不再绑定当前进程。磁盘损坏、误删、错误迁移仍可能造成损失；备份与恢复会在后续工程化课程处理。

SQLite 是嵌入式数据库。Python 进程直接通过标准库读写数据库文件，不需要先启动独立数据库服务器。这使它很适合本地学习、桌面工具、测试和小型服务，也方便我们先把数据边界看清楚。

</section>

<section id="concept-two-related-tables" data-learning-context="concept-two-related-tables" data-context-type="concept" markdown="1">

## 为什么分成两张表

一位学习者会有很多次学习记录。把每次投入都塞进 `learners` 的新列，很快会出现 `hours_1`、`hours_2`、`hours_3`，也不知道下一次要放在哪里。

v0.6 使用一对多关系：

```text
learners                              study_sessions
┌─────────┬──────┬──────────────┐     ┌────┬────────────┬───────┬────────────┐
│ id (PK) │ name │ completed... │ 1 ─<│ id │ learner_id│ hours │ note       │
├─────────┼──────┼──────────────┤     ├────┼────────────┼───────┼────────────┤
│ xiaoma  │ 小码 │ 8            │     │ 1  │ xiaoma    │ 7.5   │ 契约检查   │
└─────────┴──────┴──────────────┘     └────┴────────────┴───────┴────────────┘
```

- **表**描述一类对象；这里有学习者和学习时段两类。
- **行**是一条具体记录。
- **列**是一项固定含义的数据。
- **主键**（PK）在表内唯一标识一行。`learners.id` 使用稳定的学习者 ID。
- **外键**（FK）要求 `study_sessions.learner_id` 指向一位真实存在的学习者。

页面上的累计小时不是某一列，而是查询时计算：

```sql
SELECT COALESCE(SUM(study_sessions.hours), 0.0) AS completed_hours
FROM learners
LEFT JOIN study_sessions
  ON study_sessions.learner_id = learners.id
WHERE learners.id = ?;
```

这里用 `LEFT JOIN`，所以一位还没有学习时段的新学习者也能出现在结果里，小时数由 `COALESCE` 变成 `0.0`。

SQLite 的外键约束需要在每次连接时明确开启。示例在 `connect()` 中执行 `PRAGMA foreign_keys = ON`，不依赖环境默认值。

</section>

<section id="example-placeholders" data-learning-context="example-placeholders" data-context-type="example" markdown="1">

## SQL 和数据不要自己拼在一起

先看读取一位学习者的条件：

```python
row = connection.execute(
    "SELECT name FROM learners WHERE id = ?",
    (learner_id,),
).fetchone()
```

问号是占位符，第二个参数才是真正的数据。数据库驱动负责把值安全地绑定进去。

不要这样写：

```python
# 不要照着做
sql = f"SELECT name FROM learners WHERE id = '{learner_id}'"
```

字符串拼接会让输入有机会改变 SQL 的结构。占位符把“查询要做什么”和“这次传入什么值”分开。测试会把 `'); DROP TABLE learners; --` 当作普通备注保存，再确认 `learners` 表仍然存在。

</section>

<section id="reproduce-dashboard-v06" data-learning-context="reproduce-dashboard-v06" data-context-type="reproduce" markdown="1">

## 保存一次，再重启服务

把完整 v0.6 复制到自己的练习目录：

=== "Windows PowerShell"

    ```powershell
    New-Item -ItemType Directory -Force .\practice\web-core\learning-dashboard | Out-Null
    Copy-Item .\site-src\examples\web-core\learning-dashboard-v06\* `
      .\practice\web-core\learning-dashboard\ -Recurse -Force
    ```

=== "macOS / Linux"

    ```bash
    mkdir -p practice/web-core/learning-dashboard
    cp -R site-src/examples/web-core/learning-dashboard-v06/. \
      practice/web-core/learning-dashboard/
    ```

如果复制目录里带有 `node_modules` 或 `data/learning.sqlite3`，先删掉它们。按锁文件安装并编译前端：

```bash
cd practice/web-core/learning-dashboard
npm ci
npm test
```

回到仓库根目录，安装测试依赖并运行 12 项后端测试：

=== "Windows PowerShell"

    ```powershell
    .\.venv\Scripts\python.exe -m pip install `
      -r .\practice\web-core\learning-dashboard\requirements-test.txt
    .\.venv\Scripts\python.exe -m unittest discover `
      -s .\practice\web-core\learning-dashboard -p test_app.py -v
    ```

=== "macOS / Linux"

    ```bash
    .venv/bin/python -m pip install \
      -r practice/web-core/learning-dashboard/requirements-test.txt
    .venv/bin/python -m unittest discover \
      -s practice/web-core/learning-dashboard -p test_app.py -v
    ```

启动服务：

```bash
.venv/bin/python -m uvicorn app:app \
  --app-dir practice/web-core/learning-dashboard \
  --host 127.0.0.1 --port 8780
```

Windows 把开头换成 `\.venv\Scripts\python.exe`。打开 `http://127.0.0.1:8780/`，点击“保存 1 小时”。累计投入应该从 `7.5` 变成 `8.5`。

现在在终端按 ++ctrl+c++ 停止服务，再运行同一条 Uvicorn 命令。刷新页面，`8.5` 仍然存在。也可以不用 JavaScript，直接检查接口：

```bash
curl http://127.0.0.1:8780/api/learning-summary/xiaoma
```

数据库文件位于练习目录的 `data/learning.sqlite3`。它是运行结果，不需要提交到 Git；真正应该提交的是 `schema.sql`、代码和测试。

</section>

<section id="example-transaction-boundary" data-learning-context="example-transaction-boundary" data-context-type="example" markdown="1">

## 两个动作要么都成功，要么都不留下

写入不是单独一行 `INSERT`。应用还要确认学习者存在、写入学习时段，并把整个变化提交。示例把这段范围放进 `transaction()`：

```python
@contextmanager
def transaction(self):
    connection = self.connect()
    try:
        with connection:
            yield connection
    finally:
        connection.close()
```

`with connection` 正常退出时提交，内部抛出异常时回滚。它不会自动关闭连接，所以外层 `finally` 仍然要 `close()`。

测试会先插入一条合法记录，紧接着执行一条指向不存在表的 SQL。第二条失败后重新连接，记录数量与开始前相同。这比只看“接口返回了 503”更可靠：它证明数据库没有留下半次操作。

</section>

<section id="modify-own-session" data-learning-context="modify-own-session" data-context-type="modify" markdown="1">

## 把固定的 1 小时改成自己的记录

先不要改数据库结构。把页面按钮改成你今天真正投入的时间，例如 `0.75` 小时，并换一条备注：

```typescript
const result = await saveStudySession(
  activeLearnerId,
  0.75,
  "整理 SQLite 关系图并补回滚测试"
);
```

运行前先写下预测：当前是 `8.5`，保存后应该变成多少？然后依次检查：

1. `npm test` 是否仍通过。
2. 点击按钮后是否收到 `201 Created`。
3. 页面累计小时是否与预测一致。
4. 重启服务后数值是否保留。
5. 把小时数临时改成 `-1`，确认 API 返回 `422`，数据库记录数没有增加。

如果想再多走一步，在种子数据中加入第三位学习者和一条学习时段。两条记录必须使用同一个 `learner_id`，否则外键会拒绝写入。

</section>

<section id="troubleshoot-sqlite" data-learning-context="troubleshoot-sqlite" data-context-type="troubleshoot" markdown="1">

## 没得到同样结果时

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| 页面还是 7.5，重启后没变化 | Network 里的 POST 状态 | 确认是 `201`，再看 `data/learning.sqlite3` 是否生成 |
| `unable to open database file` | 数据库路径与目录权限 | 回到项目目录运行，确认 `data/` 可创建且目标路径不是目录 |
| `FOREIGN KEY constraint failed` | `learner_id` | 先查询 `learners`，不要关闭外键检查来绕过问题 |
| `CHECK constraint failed` | `hours` 或 `note` | 保持小时数在 0 到 24 之间，备注不能为空且不超过 200 字符 |
| 改了 `schema.sql`，旧数据库没变化 | `PRAGMA user_version` 与现有文件 | 学习阶段可备份后删除本地数据库重建；正式系统要写迁移，不要直接改生产文件 |
| 测试互相影响 | 测试数据库路径 | 每个测试使用临时目录，不要指向练习中的真实数据库 |
| 页面保存成功但数字没刷新 | 保存后的 GET 请求 | 看 Network 是否再次请求当前学习者，确认前端没有只改 DOM 假装保存 |

这里先别打开数据库文件手工改值。先从 HTTP 状态、应用日志和自动测试判断错误在哪一层。

</section>

<section id="project-dashboard-v06" data-learning-context="project-dashboard-v06" data-context-type="project" markdown="1">

## 学习进度报告器 Web v0.6

| v0.5 已经有 | v0.6 新增 | 下一节继续 |
| --- | --- | --- |
| FastAPI、OpenAPI、TypeScript 守卫 | `learners` 与 `study_sessions` 两张表 | 正式设计 REST 资源 |
| 内存字典中的两条记录 | SQLite 文件与聚合查询 | CRUD 与分页 |
| HTTP 失败与契约漂移测试 | 约束、参数绑定、提交与回滚 | 更新操作的幂等边界 |

保存这些材料：关系图、重启前后两次 GET、一次成功 POST、12 项后端测试、前端状态测试，以及一条回滚用例。下一版会继续使用同一个数据库，但不会在这一课提前堆出所有资源接口。

</section>

<section id="deepen-sqlite-and-migrations" data-learning-context="deepen-sqlite-and-migrations" data-context-type="deepen" markdown="1">

## SQLite 能用到什么时候

这个项目现在只有本机学习者、少量写入和一个进程，SQLite 让搭建成本很低。它不是“初级数据库”的代名词，也不是所有 Web 服务的最终选择。

当系统进入多实例部署、持续并发写入、细粒度权限、在线运维或复杂数据治理时，要重新评估 PostgreSQL 等独立数据库。迁移的关键不是把文件名换掉，而是先保住应用层的数据接口、事务语义和测试。

`schema.sql` 使用 `PRAGMA user_version = 1` 标记第一版结构，这只是迁移入口，不是完整迁移系统。后续数据库深化课程会再处理索引、查询计划、隔离、备份和迁移工具。

</section>

<section id="career-explain-persistence" data-learning-context="career-explain-persistence" data-context-type="career" markdown="1">

## 求职加练：不要只说“项目用了 SQLite”

用这次改动回答三个问题：

1. 为什么把学习者和学习时段拆成两张表？如果只用一张表会出现什么重复？
2. 你怎样防止输入改变 SQL？API 校验与数据库约束为什么都要保留？
3. 写入中途失败时，你怎样证明没有留下半条数据？

我更建议把项目讲成一条改进链：内存数据在重启后丢失 → 建立关系模型 → 参数化读写 → 事务失败自动回滚 → 临时数据库测试证明行为。它比“会写 SELECT、INSERT”更能说明你理解数据为什么可靠。

</section>

## 完成检查

- [ ] 我能解释内存对象与数据库文件的寿命差别。
- [ ] 我能在关系图中指出主键、外键和一对多关系。
- [ ] 我只用占位符传入 SQL 数据，没有拼接用户输入。
- [ ] 我保存了自己的学习时段，重启服务后仍能读到。
- [ ] 我让一次事务中途失败，并用测试证明它已经回滚。
- [ ] 我知道 SQLite 适合当前项目，但没有把它说成所有 Web 系统的最终数据库。

## 来源与版本

- 适用：Python 3.11+、SQLite 3、FastAPI 0.139.2、Node.js 24 LTS、TypeScript 7.0.2。
- 本课在 Python 3.11.9、SQLite 3.45.1、Node.js 24.14.1 上完成复现；核查日期：2026-07-18。
- Python 官方：[sqlite3 教程、占位符与事务控制](https://docs.python.org/3.11/library/sqlite3.html)。
- SQLite 官方：[外键支持](https://www.sqlite.org/foreignkeys.html)、[事务](https://www.sqlite.org/lang_transaction.html)、[CREATE TABLE 与约束](https://www.sqlite.org/lang_createtable.html)。
- 代码验证：`npm test`、12 项 unittest、临时数据库重开测试、约束测试、回滚测试与严格站点构建。

## 下一步

下一课[《REST 资源、CRUD、分页与幂等》](03-rest-resources-crud-pagination-idempotency.md)会把现在的“读取汇总＋追加学习时段”整理成可维护的资源接口。SQLite 继续保留，但重点转向 URL、方法、状态码、分页和重复请求的行为。
