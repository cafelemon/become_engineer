<div class="be-tutor-mount" data-tutor-lesson="agent-tool-calling-02" aria-hidden="true"></div>
<section id="overview-read-only-execution" class="be-page-hero be-lesson-hero" data-learning-context="overview-read-only-execution" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Tool Calling 与有界工作流 · 第 2 / 6 课 · 智能学习助手 P5.5 v0.14</span>
# 业务校验、主体授权与只读工具执行
## 只有合法且有权的候选才能触达 handler
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled
tool=name:get_learning_status,risk:read-only,permission:learning_status:read
success=call-id:call_read1,status:ok,completed:4,recent:3
denied=call-id:call_read2,status:error,error:forbidden,handler-called:false
handler=calls:1,sqlite-uri:mode=ro,sql:parameterized,result-limit:3
validation=exact-fields:true,learner-pattern:true,strict-bool:true,permission:true,ownership:true
rejection=unknown-tool:true,invalid-arguments:true,missing-permission:true,cross-learner:true,write-attempt:true
envelope=call-id:true,tool-name:true,status:true,data-or-error:true,internal-exception:false
logs=arguments:none,query:none,result:none,call-id:allowed,tool-name:allowed,status:allowed,error-code:allowed
invariants=validate-before-handler,authorize-before-handler,own-resource,read-only-db,parameterized-sql,bounded-result,no-network
```
v0.14 接收第 1 课已通过结构校验的候选，再检查业务值、`learning_status:read` 权限和资源所有权。只有全部通过才打开真实临时 SQLite 的只读连接；拒绝路径用 handler 调用计数证明没有触达数据层。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 2 / 6</strong></div>
  <div><span>前置</span><strong>ToolRegistry、身份授权、SQLite 参数化查询</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 临时 SQLite</strong></div>
  <div><span>完成后留下</span><strong>只读 handler、权限门禁、结果 envelope 与 8 项测试</strong></div>
</div>

## 学习目标

- 把 Schema 形状校验与业务值校验分开。
- 让主体权限和资源所有权先于数据访问。
- 用 SQLite URI `mode=ro` 证明数据库层拒绝写入。
- 只用参数化、固定结构 SQL，不接受模型生成 SQL。
- 限制结果字段和最近记录数量。
- 把内部失败归一为结构化 envelope，不暴露路径或异常细节。

<section id="concept-validation-order" data-learning-context="concept-validation-order" data-context-type="concept" markdown="1">
## 执行顺序本身是安全属性

```text
已验证候选
  → 已知工具
  → 精确业务字段与值
  → 主体 permission
  → learner_id 所有权
  → 只读 handler
  → 有界结果 envelope
```

若先查询再检查权限，即使最后返回 403，也可能产生存在性侧信道、额外负载或审计噪声。测试用 `handler_calls == 0` 证明缺权限、跨主体和坏参数都停在数据层之前。
</section>

<section id="concept-least-privilege-reader" data-learning-context="concept-least-privilege-reader" data-context-type="concept" markdown="1">
## 两层只读比注释里的“只查询”更可信

工具层只注册 `get_learning_status`，数据库层又用 `file:...?...mode=ro` 打开连接。SQL 结构固定，`learner_id` 只作为 `?` 参数，最近记录固定 `LIMIT 3`。真实测试尝试 `INSERT` 并得到 SQLite 写入失败。

这仍是本机教学边界，不替代生产数据库账号、行级授权、连接池和超时。
</section>

<section id="example-owner-read" data-learning-context="example-owner-read" data-context-type="example" markdown="1">
## 同时满足 permission 和 ownership

主体 `learner-001` 必须拥有 `learning_status:read`，且调用参数也必须是 `learner-001`。只有权限没有所有权仍返回 `forbidden`；模型不能通过修改参数读取 `learner-002`。

成功结果只含 learner ID、完成数和最多三条课程 ID，不返回原始时间行、数据库路径或 SQL。
</section>

<section id="reproduce-read-only-v14" data-learning-context="reproduce-read-only-v14" data-context-type="reproduce" markdown="1">
## 运行真实只读数据库与拒绝路径

```bash
cd site-src/examples/agent-tool-calling/intelligent-learning-assistant-v14
python3 -m unittest -v test_read_only_tool.py
python3 read_only_tool.py
```

8 项测试覆盖所有者成功、缺权限、跨主体、坏业务值、未知工具、真实写失败、envelope 脱敏和固定报告。
</section>

<section id="modify-result-bound" data-learning-context="modify-result-bound" data-context-type="modify" markdown="1">
## 把最近结果从 3 改为 2

1. 修改 SQL 的固定 `LIMIT`，不要把 limit 暴露为任意模型参数。
2. 更新固定报告和测试期望。
3. 验证完成总数仍是 4，最近列表变成 2。
4. 尝试给候选增加 `limit=1000`，确认精确字段门禁拒绝。
5. 说明何时才值得把分页做成受控业务参数。
</section>

<section id="troubleshoot-read-only-tool" data-learning-context="troubleshoot-read-only-tool" data-context-type="troubleshoot" markdown="1">
## 用 handler 计数判断拒绝发生在哪一层

| 结果 | 含义 |
| --- | --- |
| `unknown_tool` | 不在注册表 |
| `invalid_arguments` | 业务字段、ID 格式或严格 bool 不合法 |
| `forbidden` | 缺 permission 或跨资源所有者 |
| `tool_unavailable` | 受控 handler 内部数据库/文件失败 |
| `ok` | 通过门禁并成功生成有界数据 |

对模型只回传稳定错误码；内部异常路径、SQL、参数和值留在受限诊断域，本课默认也不写入日志。
</section>

<section id="deepen-authorization-boundary" data-learning-context="deepen-authorization-boundary" data-context-type="deepen" markdown="1">
## 参数化 SQL 不能替代授权

参数化查询阻止值改变 SQL 结构，但合法的 `learner-002` 仍可能越权。只读连接阻止写，却不限制能读哪些行。Schema、参数化、只读账号和资源授权解决不同问题，必须组合。

如果来源文本诱导模型请求别人的 ID，它仍然只是候选；应用按当前主体重新授权，不相信模型声称的身份。
</section>

<section id="project-learning-assistant-v14" data-learning-context="project-learning-assistant-v14" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.5 v0.14

- 上一版：v0.13 解析候选但不执行。
- 本课新增：业务值、permission、ownership、只读 SQLite、参数化查询和结果 envelope。
- 文件：`read_only_tool.py` 与 `test_read_only_tool.py`。
- 保存：成功/越权证据、写失败、handler 计数和 8 项测试。
- 下一版：处理同一模型响应中的多个 call ID、稳定顺序与部分失败。
</section>

## 四类学习者入口

- 零基础兴趣：按顺序给六道门贴标签。
- 有基础兴趣：修改结果上限并证明未知 limit 被拒绝。
- 零基础求职：解释“参数化 SQL 不等于授权”。
- 有基础求职：解释两层只读、所有权侧信道和错误脱敏；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定报告通过。
- 缺权限、跨主体和坏参数不触达 handler。
- SQLite URI 真实只读，写入测试失败。
- SQL 结构固定且参数化，结果最多三条。
- envelope 在 data/error 间二选一，不暴露内部异常。
- 日志不保存参数、查询或结果。

## 来源与版本

- 核查日期：2026-07-26。
- [Python sqlite3 URI 只读模式](https://docs.python.org/3.11/library/sqlite3.html#how-to-work-with-sqlite-uris)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP LLM Excessive Agency](https://genai.owasp.org/llmrisk/llm06-excessive-agency/)

## 下一步

进入第 3 课，用 `call_id` 把多个候选与多个结果一一关联，并隔离部分失败。
