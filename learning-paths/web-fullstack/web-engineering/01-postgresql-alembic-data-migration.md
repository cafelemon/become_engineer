<div class="be-tutor-mount" data-tutor-lesson="web-engineering-01" aria-hidden="true"></div>

# PostgreSQL、Alembic 与数据迁移

<section data-context-type="overview" data-learning-context="overview-postgres-migration" id="overview-postgres-migration">

## 从 SQLite 的可运行，到 PostgreSQL 的可演进

Web v0.9 将主存储换成 PostgreSQL 16；结构只由 Alembic 版本迁移改变，SQLite 导入可重复运行。

旧版本能把数据写进 SQLite，并不代表它已经具备多人服务需要的数据库演进能力。本课要解决的不是“换一个连接字符串”，而是让结构、数据和失败恢复都有可重复的路径。

| 你看到的现象 | 本课给出的回答 |
| --- | --- |
| 新环境没有表 | 从空库执行 `upgrade head` |
| 旧数据需要搬迁 | 运行幂等导入脚本并核对源、目标 |
| 导入中途违反外键 | 整批事务回滚，不留下半套数据 |
| 想知道数据库处于哪一版 | 查询 `alembic_version` |
</section>

<section data-context-type="concept" data-learning-context="concept-migration-contract" id="concept-migration-contract">

## 结构版本是代码的一部分

`upgrade head` 将数据库推进到已知版本；失败事务会整体回滚，`downgrade base` 只用于临时验证库，不等同生产回滚策略。

一条可靠的迁移链有三类状态：

```mermaid
flowchart LR
    A["空 PostgreSQL"] -->|"0001: 学习记录"| B["学习数据结构"]
    B -->|"0002: 用户与会话"| C["身份结构"]
    C -->|"0003: 所有权与审计"| D["授权结构"]
```

Alembic 管结构版本，SQLAlchemy Core 管 SQL 与连接生命周期，psycopg 负责 PostgreSQL 驱动。三者职责不同：连接成功不说明 revision 已完成，revision 完成也不说明旧数据已导入。

连接池会复用数据库连接。应用结束时仍要调用 `engine.dispose()`，测试则应让每个事务明确提交或回滚，避免把上一个用例的连接状态带入下一个用例。
</section>

<section data-context-type="example" data-learning-context="example-import-idempotent" id="example-import-idempotent">

## 导入用业务幂等键去重

`idempotency_key` 是唯一约束。再次导入相同 SQLite 数据，记录数和小时汇总不变；外键继续指向已导入的学习者。

导入脚本按下面顺序工作：先读取源库，随后在一个目标事务中写学习者和学习时段，冲突时按业务幂等键跳过已经存在的时段，最后从 PostgreSQL 重新读取汇总。幂等不是“忽略所有错误”，外键错误、字段类型错误仍应终止并回滚。

| 核对项 | 第一次导入 | 第二次导入 |
| --- | ---: | ---: |
| 学习者数 | 1 | 1 |
| 学习时段数 | 1 | 1 |
| 总小时 | 1.25 | 1.25 |
| `idempotency_key` | `legacy-0001` | 仍只有一条 |
</section>

<section data-context-type="reproduce" data-learning-context="reproduce-dashboard-v09" id="reproduce-dashboard-v09">

## 用真实 PostgreSQL 跑迁移

```bash
cd site-src/examples/web-engineering/learning-dashboard-v09
docker compose up -d
WEB_ENGINEERING_POSTGRES=1 ../../../../.venv/bin/python -m unittest -v test_postgres.py
```

固定检查是 4 项：升级、导入幂等、失败回滚、降级；端口是本机回环端口。

正常结束时根验证器输出：

```json
{
  "valid": true,
  "lesson_id": "web-engineering-01",
  "project": "learning-dashboard-v09",
  "checks": 4,
  "real_postgresql": true
}
```

`real_postgresql: true` 很重要：这四项测试会连接 `127.0.0.1:55439` 的 PostgreSQL 16，而不是用 SQLite 或 Mock 替代。实验结束可执行 `docker compose stop`；命名卷保留数据库，方便下次继续。
</section>

<section data-context-type="modify" data-learning-context="modify-migration-column" id="modify-migration-column">

## 主动修改：新增一个可空列

写一份新 revision，先 `upgrade head`，验证旧数据仍可读；再补回填步骤。不要手工 `ALTER TABLE` 后假装迁移已经记录。

建议把改动拆成三步：

1. 新增允许为空的 `timezone_name`。
2. 用一条受约束的更新语句为旧行回填 `Asia/Shanghai`。
3. 只有在所有读写版本都兼容后，才考虑改成非空。

修改后分别从空库和已有 v0.9 数据库升级。前者证明全新安装可用，后者证明真实升级路径没有漏掉旧数据。
</section>

<section data-context-type="troubleshoot" data-learning-context="troubleshoot-migration" id="troubleshoot-migration">

## 找不到 revision 时先检查什么

先看连接 URL、`alembic_version` 和 revision 链。导入失败时不要删生产数据，先在临时数据库复现并观察事务是否回滚。

| 现象 | 先检查 | 恢复办法 |
| --- | --- | --- |
| `connection refused` | 容器健康、端口、连接 URL | 等 PostgreSQL ready，再重试 |
| `Can't locate revision` | 版本文件是否完整、`down_revision` | 恢复缺失 revision，不手改版本号 |
| `relation already exists` | 是否手工建表、版本表是否漂移 | 在验证库重放并修正迁移链 |
| 第二次导入记录翻倍 | 唯一键与冲突处理 | 修复幂等键后从干净目标库验证 |
| 外键失败后仍有新行 | 事务是否包住整批写入 | 扩大事务边界并补回滚测试 |

不要把 `alembic stamp head` 当作修复迁移的通用手段。它只改版本标记，不执行结构变化；除非你已经逐项证明实际 schema 与 revision 完全一致，否则会制造更隐蔽的漂移。
</section>

<section data-context-type="project" data-learning-context="project-dashboard-v09" id="project-dashboard-v09">

## 学习进度报告器 Web v0.9

v0.9 保留 v0.8 的学习记录语义，并提供 PostgreSQL 连接池、SQLAlchemy Core、Alembic 与可验证导入。

- 上一版：SQLite 保存学习者、学习时段、摘要与幂等语义。
- 这一版：主存储进入 PostgreSQL，结构由 `0001` 到 `0003` 的 revision 链管理。
- 关键文件：`database.py`、`migrate_sqlite.py`、`alembic/versions/`、`test_postgres.py`。
- 应保存的记录：两次导入的计数与小时数、失败事务后的查询、当前 revision。
- 下一版：把用户、密码哈希和服务端会话接到已经迁移出的表。
</section>

## 四类学习者入口

- 零基础兴趣：先画“旧库 → 导入 → 新库”的数据流，再运行四项测试。
- 有基础兴趣：直接检查 revision 链、连接池与幂等键是否能解释。
- 零基础求职：保存迁移前后记录数、汇总和失败回滚输出。
- 有基础求职：补一份“为何不能靠手工改表”的迁移评审记录。

<section data-context-type="career" data-learning-context="career-migration-review" id="career-migration-review">

## 求职加练：迁移在第 73% 失败怎么办

原创追问：导入已运行 20 分钟时违反外键，你如何证明目标库没有半套数据，并设计可安全重试的恢复流程？回答必须包含事务边界、幂等键、源目标核对和停止条件。
</section>

## 完成检查

- 能说明迁移、导入和业务回滚的边界。
- 能证明第二次导入没有重复记录。
- 能从空库升级到 `0003_ownership_audit`，并列出四张核心表。
- 能解释为什么生产回滚不能简单照搬 `downgrade base`。

## 来源与版本

适用 Python 3.11、PostgreSQL 16、SQLAlchemy 2.0.51、Alembic 1.18.5；核查日期 2026-07-22。参考 [SQLAlchemy PostgreSQL 方言](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html) 与 [Alembic 教程](https://alembic.sqlalchemy.org/en/latest/tutorial.html)。

## 下一步

继续进入 [密码哈希、Cookie 会话与 CSRF](02-password-hashing-cookie-sessions-csrf.md)。
