<div class="be-tutor-mount" data-tutor-lesson="cs-systems-05" aria-hidden="true"></div>

<section id="overview-transaction-result" data-learning-context="overview-transaction-result" data-context-type="overview" markdown="1">

<div class="be-page-hero" markdown="1">
<span class="be-page-eyebrow">CS 系统基础 · 第五课 · 系统运行观察器 v0.5</span>

# 事务、隔离与并发写入

## 已经扣款却来不及入账，数据库应该留下什么

```text
rollback: before=100,100 after=100,100
constraint: rejected=True total=200
lock: blocked=True retry_succeeded=True
snapshot: before=100 during=100 after=120
```

第一行在转账中途主动失败，但两边余额都回到原值；第二行让数据库拒绝负余额；第三行复现第二个写入者遇到锁并在释放后重试；最后一行展示同一读事务里的快照保持一致。

[运行事务实验](#reproduce-transaction-lab){ .md-button }
[先看事务边界](#concept-transaction-boundary){ .md-button .md-button--secondary }
</div>

<div class="be-page-summary" markdown="1">
  <div><span>课程位置</span><strong>CS 系统基础 · 5 / 6</strong></div>
  <div><span>项目版本</span><strong>系统运行观察器 v0.5</strong></div>
  <div><span>主要结果</span><strong>回滚、约束、写锁、重试、事务快照</strong></div>
</div>

## 这节适合谁

- **小白**：先把事务想成一次必须整体成立的转账，按“开始—修改—提交／回滚”看状态。
- **已有基础**：直接做跳过检查——能稳定复现回滚和写锁；能解释读事务为什么暂时看不到新提交；不会把 SQLite 行为说成所有数据库实现。都做到，可以进入下一课。
- **兴趣学习**：改变转账金额和等待期限，观察约束与重试结果。
- **求职准备**：保存一次原子性故障、一次锁等待和一张读快照时序图，练习用证据解释事务与隔离。

四类画像共用系统运行观察器 v0.5。求职路线增加 ACID、隔离和锁的原创追问，不复制数据库正文。

前置是[从端口到 HTTP 的本机网络链路](04-local-network-port-http.md)。上一课的两个参与者通过 socket 交换消息；本课的两个参与者是访问同一 SQLite 文件的独立连接。

</section>

<section id="concept-transaction-boundary" data-learning-context="concept-transaction-boundary" data-context-type="concept" markdown="1">

## 事务把多个语句变成一次提交决定

```text
BEGIN IMMEDIATE
  alice -= 30
  ── 这里失败 ──
  bob += 30
COMMIT

失败路径：ROLLBACK → alice=100, bob=100
```

事务内可以执行多条语句，但外部持久状态最终只接受一次提交或回滚决定。原子性不是“语句不会失败”，而是失败时不会留下只完成一半的业务变化。

数据库约束继续守住单行合法性：`CHECK (balance >= 0)` 让负余额即使绕过应用检查也不能提交。事务和约束保护不同层次，不能互相替代。

</section>

<section id="example-writer-lock" data-learning-context="example-writer-lock" data-context-type="example" markdown="1">

## BEGIN IMMEDIATE 让写入竞争变得可重复

连接 A 先执行 `BEGIN IMMEDIATE` 并持有写事务。线程中的连接 B 使用 50 ms busy timeout，再执行同样的开始语句；在 A 回滚前，B 得到 `database is locked`。事件保证 B 已经完成这次尝试，A 才释放锁。

随后新连接重试并成功提交。这里验证的是“锁存在时明确失败、释放后可以重新执行”，不是让测试线程随机抢锁，也不是模拟死锁。

</section>

<section id="example-wal-snapshot" data-learning-context="example-wal-snapshot" data-context-type="example" markdown="1">

## 同一读事务看到同一个快照

```text
读连接 BEGIN → 读到 100
写连接 BEGIN IMMEDIATE → 改成 120 → COMMIT
读连接仍在原事务 → 仍读到 100
读连接 COMMIT → 下一次读取 120
```

示例明确启用 SQLite WAL。WAL 允许写连接提交时，已有读事务继续读取自己的历史快照。读事务结束后，新读取才选择更新后的快照。

这是 SQLite 的具体行为，不是所有数据库隔离级别、MVCC 或锁实现的通用代码。跨数据库讨论时必须先说明产品、版本、隔离配置和实验条件。

</section>

<section id="reproduce-transaction-lab" data-learning-context="reproduce-transaction-lab" data-context-type="reproduce" markdown="1">

## 用四个临时数据库隔离四个结论

完整示例在 `site-src/examples/cs-systems/runtime-observer-v05/`，只使用 Python 3.11 的 `sqlite3` 与系统 SQLite。

```bash
cd site-src/examples/cs-systems/runtime-observer-v05
python transaction_lab.py
python -m unittest -v test_transaction_lab.py
```

你应该看到页面开头四行固定输出和 4 项测试通过。每个实验使用独立临时数据库，运行结束自动删除，不修改 Web 项目的示例数据，也不提交 `.sqlite3` 文件。

</section>

<section id="modify-transfer-rule" data-learning-context="modify-transfer-rule" data-context-type="modify" markdown="1">

## 完成真正的转账，再故意重复一次

新增 `transfer(path, amount)`：在同一事务里扣减 alice、增加 bob，并在提交前检查两者总额仍为 200。为成功转账、余额不足和中途异常各写一个测试。

然后连续调用两次 `transfer(path, 10)`。先预测余额，再判断业务是否允许重复。如果调用者只想执行一次，就需要在更高层增加操作 ID 与唯一约束；事务本身不会猜测两次调用是不是同一个意图。

</section>

<section id="troubleshoot-sqlite-concurrency" data-learning-context="troubleshoot-sqlite-concurrency" data-context-type="troubleshoot" markdown="1">

## 并发数据库问题要把连接和事务画出来

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| 失败后只扣了一边余额 | 两条 UPDATE 是否在同一事务 | 显式 BEGIN，异常时 rollback，测试最终状态 |
| `database is locked` | 哪个独立连接仍持有写事务 | 缩短事务，提交／回滚后有限重试，不无限等待 |
| 明明已提交却仍读旧值 | 读连接是否仍在原事务 | 先理解快照；需要新值时结束事务再读 |
| 透支数据进入数据库 | 是否只有应用层 if | 增加 CHECK 等数据库约束并测试绕过路径 |
| 测试偶尔抢锁顺序不同 | 是否只依赖线程调度 | 用 Event 固定先持锁、后尝试、再释放的顺序 |
| 连接越来越多 | finally 是否关闭所有连接 | 为每个连接明确所有者和退出路径 |
| 想用本课解释其他数据库 | 是否忽略产品和隔离配置 | 回到对应数据库官方文档并重新实验 |

</section>

<section id="project-runtime-observer-v05" data-learning-context="project-runtime-observer-v05" data-context-type="project" markdown="1">

## 系统运行观察器 v0.5

| v0.4 已有 | v0.5 新增 | 最后一版继续 |
| --- | --- | --- |
| 客户端和服务端并发 | SQLite 独立连接 | 请求身份 |
| HTTP 状态与超时 | 回滚、约束与写锁 | 动作授权 |
| socket 生命周期 | WAL 读事务快照 | 默认拒绝与日志脱敏 |

保存四行输出、4 项测试和一张“读连接—写连接—数据库文件”时序图。观察器现在能证明数据是否整体提交、竞争者为什么失败、重试何时安全、读取属于哪个事务快照。

</section>

<section id="deepen-sqlite-boundary" data-learning-context="deepen-sqlite-boundary" data-context-type="deepen" markdown="1">

## ACID 是检查问题的框架，不是四个开关

本课直接验证原子回滚、约束保持和隔离快照；没有通过断电恢复证明持久性，也没有覆盖所有异常、锁升级或检查点行为。不要因为 SQLite 文件测试通过，就声称具备生产数据库高可用。

后续 Web 工程化会把事务接入真实请求、幂等和认证边界；系统工程会继续讨论并发控制、性能测量与故障恢复。

</section>

<section id="career-transaction-evidence" data-learning-context="career-transaction-evidence" data-context-type="career" markdown="1">

## 求职加练：用状态变化解释事务，而不是背 ACID

原创追问：转账在扣款后抛错；并发写入者等待后失败；与此同时读连接仍看到旧余额。请分别指出原子性、写锁竞争和读快照的证据，再说明哪些结论只属于当前 SQLite WAL 配置。

回答必须引用回滚前后余额、`blocked/retry_succeeded` 和 `before/during/after` 测试。这道追问由事务、隔离级别和锁能力信号重新设计，不使用外部题面或答案结构。

</section>

## 完成检查

- [ ] 我能解释 BEGIN、COMMIT 和 ROLLBACK 的状态边界。
- [ ] 我能用失败测试证明转账没有只完成一半。
- [ ] 我同时使用应用逻辑和数据库约束保护余额不变量。
- [ ] 我能解释第二写入者为什么失败、释放后为什么能重试。
- [ ] 我能画出 WAL 读事务在提交前后的快照变化。
- [ ] 我不会把 SQLite 实验描述成所有数据库的统一实现。

## 来源与版本

- 适用：Python 3.11+、SQLite 3；示例显式使用 WAL 与独立连接。
- 本课在 Python 3.11.9、SQLite 3.45.1 与 Node.js 24.14.1 驱动的仓库验证脚本中复现；核查日期：2026-07-20。
- SQLite 官方：[事务语义与 BEGIN DEFERRED／IMMEDIATE／EXCLUSIVE](https://www.sqlite.org/lang_transaction.html)。
- SQLite 官方：[隔离、序列化写入与 WAL 快照](https://www.sqlite.org/isolation.html)。
- Python 官方：[sqlite3：事务控制与连接](https://docs.python.org/3.11/library/sqlite3.html)。
- 验证方式：4 项 unittest、固定命令输出、课程根验证脚本；数据库只存在于临时目录。

## 下一步

进入[身份、授权与最小权限](06-identity-authorization-least-privilege.md)。最后一课会给观察器的读取与诊断动作增加身份和权限边界，并验证 401、403、允许结果和日志脱敏。
