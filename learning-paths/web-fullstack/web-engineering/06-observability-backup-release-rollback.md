<div class="be-tutor-mount" data-tutor-lesson="web-engineering-06" aria-hidden="true"></div>

# 指标、备份、发布与回滚演练

<section data-context-type="overview" data-learning-context="overview-release-evidence" id="overview-release-evidence" markdown="1">

## 发布必须能证明可恢复

Web v0.14 不把“镜像已经启动”当作交付完成。一次发布至少要回答：候选版本是否 ready，错误率是否异常，备份能否恢复，新旧应用是否都兼容当前数据库，出现故障后是否有明确停止条件。

```mermaid
flowchart LR
    A["构建 v0.14"] --> B["启动候选"]
    B --> C{"readiness 通过?"}
    C -->|"否"| X["停止发布"]
    C -->|"是"| D["检查日志与指标"]
    D --> E{"恢复演练通过?"}
    E -->|"否"| X
    E -->|"是"| F{"数据库兼容 v0.13?"}
    F -->|"否"| X
    F -->|"是"| G["允许切换并保留回滚路径"]
```

本课最终交付测试报告、健康与指标样本、备份恢复核对、发布记录和故障复盘。它们来自可运行命令，不是手填的“全部成功”清单。
</section>

<section data-context-type="concept" data-learning-context="concept-expand-contract" id="concept-expand-contract" markdown="1">

## 数据库不能总是跟镜像一起回滚

应用镜像可以切回 v0.13，但数据库 schema 可能已经改变。expand/contract 把数据库变化拆成兼容阶段：

1. **Expand**：先增加旧代码可以忽略的新列或新表。
2. **Migrate**：回填数据，让新旧读路径都成立。
3. **Switch**：新代码开始写新结构，同时保留旧版本需要的内容。
4. **Contract**：确认旧版本不再运行后，才删除旧结构。

如果 v0.14 已经删除 v0.13 必需的列，切回旧镜像只会制造第二次故障。`release_guard.py` 因此同时检查候选 readiness、恢复结果和数据库回滚兼容性；任一条件不满足都返回拒绝原因。

| 条件 | 门禁结果 |
| --- | --- |
| candidate not ready | `candidate-not-ready` |
| 恢复未验证 | `restore-not-verified` |
| schema 不兼容旧应用 | `unsafe-database-rollback` |
| 三项都满足 | 允许推进 |
</section>

<section data-context-type="example" data-learning-context="example-low-cardinality" id="example-low-cardinality" markdown="1">

## 日志负责定位，指标负责判断范围

JSON 日志每条请求带 request ID、method、status 与 duration；指标只用 method、状态等低基数标签。request ID 可以进入日志，但不能作为 Prometheus 标签，否则每次请求都会创建新的时间序列。

| 信息 | JSON 日志 | Prometheus 指标 |
| --- | --- | --- |
| request ID | 适合 | 禁止作标签 |
| URL 原始路径 | 谨慎，先去敏 | 不使用含资源 ID 的原始路径 |
| 路由模板 | 可以 | 适合 |
| method/status | 可以 | 适合 |
| Cookie/Authorization | 不记录 | 不记录 |
| duration | 单请求毫秒数 | 直方图或聚合 |

示例日志形状：

```json
{"event":"http_request","request_id":"req-safe","method":"POST","status":403,"duration_ms":4}
```

内部 `/metrics` 可由可选 Compose profile 启动的 Prometheus 抓取，但不应直接暴露在公网。监控端点也需要网络边界和访问控制。
</section>

<section data-context-type="reproduce" data-learning-context="reproduce-dashboard-v14" id="reproduce-dashboard-v14" markdown="1">

## 运行可观测与恢复实验

先运行不依赖容器的八项测试：

```bash
cd site-src/examples/web-engineering/learning-dashboard-v14
../../../../.venv/bin/python -m unittest -v test_observability.py
```

测试覆盖 JSON 字段、request ID 唯一性、低基数计数器、日志脱敏，以及发布门禁的四种决定。然后在 v0.9 PostgreSQL 已启动并迁移到 head 的前提下执行恢复脚本：

```bash
./backup_restore.sh
```

先创建独立的空白 `dashboard_verify` 数据库，再给脚本提供源、目标 URL。脚本用 `pg_dump -Fc` 生成自定义格式备份，以 `pg_restore` 恢复，并核对核心表与约束；如果两个 URL 完全相同会直接拒绝。恢复目标绝不能是正在使用的 `dashboard` 数据库。

```bash
export DATABASE_URL='postgresql://dashboard:dashboard@127.0.0.1:55439/dashboard'
export VERIFY_DATABASE_URL='postgresql://dashboard:dashboard@127.0.0.1:55439/dashboard_verify'
./backup_restore.sh /tmp/learning-dashboard-v14.dump
```

一次可接受的摘要形状：

```text
backup_format=custom
restore_database=dashboard_verify
schema_present=true
constraints_present=true
restore_verified=true
```

备份文件存在不等于恢复成功；只有在隔离目标上实际恢复和查询，才能证明这份备份可用。
</section>

<section data-context-type="modify" data-learning-context="modify-release-failure" id="modify-release-failure" markdown="1">

## 主动修改：注入发布失败

让 v0.14 的 readiness 返回 503，按下面顺序记录演练：

1. 构建并标记 v0.13、v0.14 两个镜像，不复用含糊的 `latest`。
2. 启动 v0.14 候选，但不切换正式流量。
3. readiness 失败，发布门禁输出 `candidate-not-ready`。
4. 停止候选，确认 v0.13 仍能连接当前 schema。
5. 复核 v0.13 的 live、ready 与一条业务读取。
6. 写下故障原因、检测信号、影响范围和修复后新增的测试。

第二次实验把 readiness 恢复正常，却把数据库兼容性设为 false。门禁应阻止“看起来健康”的不安全回滚，说明健康检查与数据兼容检查解决的是不同问题。
</section>

<section data-context-type="troubleshoot" data-learning-context="troubleshoot-rollback" id="troubleshoot-rollback" markdown="1">

## 回滚前先问数据库兼容吗

| 现象 | 判断 | 动作 |
| --- | --- | --- |
| v0.14 ready 失败，schema 未改变 | 应用候选故障 | 停止候选，保留 v0.13 |
| v0.14 ready 成功，错误率上升 | 业务回归 | 用 request ID 定位，再检查回滚兼容 |
| 备份生成但恢复失败 | 恢复链不可信 | 阻止发布，修复工具/权限/版本 |
| v0.13 无法读取新 schema | 不可安全应用回滚 | 停止切换，执行前向修复方案 |
| 指标时间序列暴增 | 标签高基数 | 移除 request ID、用户 ID、原始路径标签 |

回滚不是默认正确答案。若数据库已经进入不可逆状态，最安全的决定可能是停止切流、保持当前可运行版本并做前向修复。复盘必须记录为何阻止回滚，而不是把它写成“回滚失败”。

日志里查不到 request ID 时，先确认网关是否接收并透传已有值，应用是否为缺失值生成新 ID，以及响应头是否回传同一个 ID。任何层都不应把 Authorization 值拼进结构化日志。
</section>

<section data-context-type="project" data-learning-context="project-dashboard-v14" id="project-dashboard-v14" markdown="1">

## 学习进度报告器 Web v0.14

- 上一版：应用和 PostgreSQL 已有可重复的容器启动、配置门禁与健康检查。
- 这一版：加入 JSON 日志、request ID、低基数指标、备份恢复和应用/数据库双重发布门禁。
- 关键文件：`observability.py`、`release_guard.py`、`backup_restore.sh`、`prometheus.yml`、`compose.yaml`。
- 应保存的记录：测试报告、健康与指标样本、恢复核对、发布决定与故障复盘。
- 下一阶段：Web 工程化前置完成后，可进入仍待建设的 RAG／Agent 路线；本课不会提前开放下游课程。

v0.14 仍是本机教学拓扑，不包含公网部署、TLS、云账号、真实用户数据或长期秘密。Prometheus profile 是可选观察工具，不是课程运行的强制外部服务。
</section>

## 四类学习者入口

- 零基础兴趣：先关联一次 request ID、日志和指标变化。
- 有基础兴趣：直接检查高基数风险与 expand/contract 门禁。
- 零基础求职：保存备份恢复核对和一次故障注入记录。
- 有基础求职：补充不可安全回滚时的停止发布决策。

<section data-context-type="career" data-learning-context="career-release-rollback" id="career-release-rollback" markdown="1">

## 求职加练：新镜像 healthy 但错误率上升

原创追问：如何用低基数指标判断影响范围，用 request ID 定位一条失败请求，判断应用回滚是否与数据库兼容，并留下发布与复盘记录？回答必须包含一个“明确阻止回滚”的条件。
</section>

## 完成检查

- 能区分日志字段和指标标签，并解释高基数风险。
- `/metrics` 不使用 request ID、用户 ID 或资源 ID 作标签。
- 备份已恢复到独立验证数据库，并核对 schema 与约束。
- 候选不 ready、恢复未验证、schema 不兼容都会阻止发布。
- 能完整演练 v0.14 故障后保留或回到 v0.13，并说明数据库限制。
- 交付记录不含 Cookie、Authorization、CSRF 或真实秘密。

## 来源与版本

适用 PostgreSQL 16、Prometheus Python client 0.24、Docker Engine 29 与 Compose 5；核查日期 2026-07-23。参考 [PostgreSQL 备份与恢复](https://www.postgresql.org/docs/current/backup.html)、[pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html) 与 [Prometheus Python client](https://prometheus.github.io/client_python/exporting/http/fastapi-gunicorn/)。

## 下一步

Web 工程化六课完成后，再进入等待开放的 RAG／Agent 路线；先保留本批测试、迁移、恢复和回滚记录。
