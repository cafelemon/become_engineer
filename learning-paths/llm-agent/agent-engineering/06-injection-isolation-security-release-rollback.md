<div class="be-tutor-mount" data-tutor-lesson="agent-engineering-06" aria-hidden="true"></div>
<section id="overview-agent-security-delivery" class="be-page-hero be-lesson-hero" data-learning-context="overview-agent-security-delivery" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">Agent 工程 · 第 6 / 6 课 · 智能学习助手 P5.9 v0.24</span>
# 注入、隔离、安全发布与回滚
## 攻击 fixture 必须被阻断，发布才有资格开始
```text
runtime=python:3.11+,dependencies:stdlib-only,data:synthetic,network:disabled
security=cases:5,blocked:5,unexpected-allows:0
isolation=candidate:false,prompt:false,log:false,trace:false
release=allowed:true,reasons:none,rollback:v0.23
invariants=untrusted-data,eligible-memory,tool-validation,subject-isolation,approval,rollback-target
```
v0.24 用固定攻击场景验证提示注入、记忆投毒、工具结果污染、跨主体访问和未审批发布都被拒绝；然后才检查测试、备份和回滚目标。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>Agent 工程 · 6 / 6</strong></div>
  <div><span>前置</span><strong>授权、记忆门禁、轨迹评估、脱敏 trace</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 合成攻击 fixture</strong></div>
  <div><span>完成后留下</span><strong>SecurityGate、发布门禁、回滚目标与 8 项测试</strong></div>
</div>

## 学习目标

- 把检索文本和工具结果视为不可信数据。
- 在进入候选、Prompt、日志和 trace 前完成主体隔离。
- 让记忆继续服从同意、TTL 和主体资格。
- 高风险动作必须取得与具体动作绑定的批准。
- 发布同时要求安全 fixture、测试、备份和回滚目标。

<section id="concept-four-contamination-paths" data-learning-context="concept-four-contamination-paths" data-context-type="concept" markdown="1">
## 四条污染路径在进入上下文前截断

| 路径 | 失败方式 | 阻断位置 |
| --- | --- | --- |
| 提示注入 | 文档伪装成高权限指令 | 来源分层 |
| 记忆投毒 | 未同意、过期或跨主体事实进入决策 | 记忆资格门禁 |
| 工具污染 | 工具返回指令或越界数据 | 工具结果 Schema 与信任检查 |
| 跨主体访问 | 其他主体内容进入候选 | 召回与资源授权前置 |

无权内容不能先进入候选再“提醒模型别用”，因为它已经可能泄露到重排、Prompt、日志或 trace。
</section>

<section id="concept-security-release-gate" data-learning-context="concept-security-release-gate" data-context-type="concept" markdown="1">
## 发布门禁不是一张平均分

安全 fixture 任何意外放行都阻断；测试失败、备份未验证或缺少上一稳定版本也阻断。回滚目标必须是已保存、已验证且数据契约兼容的版本，不能在事故时临时猜镜像标签。
</section>

<section id="example-five-blocked-attacks" data-learning-context="example-five-blocked-attacks" data-context-type="example" markdown="1">
## 五个攻击 case 的固定结果

```text
prompt-injection:untrusted_instruction
memory-poison:memory_ineligible
tool-pollution:tool_result_untrusted
cross-subject:subject_isolation
unapproved-publish:approval_required
```

每个拒绝都返回稳定原因，不把攻击正文写入普通日志。
</section>

<section id="reproduce-security-gate-v24" data-learning-context="reproduce-security-gate-v24" data-context-type="reproduce" markdown="1">
## 运行攻击套件与发布门禁

```bash
cd site-src/examples/agent-engineering/intelligent-learning-assistant-v24
python3 -m unittest -v test_security_release_gate.py
python3 security_release_gate.py
```

8 项测试覆盖四类污染、未审批动作、合法批准、完整攻击套件和备份/回滚阻断。
</section>

<section id="modify-add-edit-approval" data-learning-context="modify-add-edit-approval" data-context-type="modify" markdown="1">
## 增加 edit 审批并绑定摘要

1. 审批请求保存动作、参数摘要和版本。
2. 审批人修改参数后生成新摘要。
3. 旧批准不能授权新摘要。
4. 新批准只允许一次匹配执行。
5. trace 只记录摘要指纹和结果，不记录秘密参数。
</section>

<section id="troubleshoot-security-release" data-learning-context="troubleshoot-security-release" data-context-type="troubleshoot" markdown="1">
## 从信任、主体、批准和回滚排查

| 现象 | 首先检查 |
| --- | --- |
| 文档改变系统规则 | source kind 是否错误提升权限 |
| 旧偏好影响新用户 | 主体、同意或 TTL 门禁是否绕过 |
| 工具返回触发下一工具 | 结果是否被误当指令 |
| 无权内容出现在 trace | ACL 是否在召回后才执行 |
| 安全测试通过却不能发版 | 备份或回滚目标是否缺失 |
</section>

<section id="deepen-defense-in-depth" data-learning-context="deepen-defense-in-depth" data-context-type="deepen" markdown="1">
## 防御要落在每个边界

Prompt 中一句“忽略恶意指令”不是完整防护。数据层做主体隔离，检索层做 ACL，记忆层做资格过滤，工具层做 Schema 与授权，执行层做审批和幂等，交付层做回归、备份与回滚。每层都有独立失败证据。
</section>

<section id="project-learning-assistant-v24" data-learning-context="project-learning-assistant-v24" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.9 v0.24

- 上一版：v0.23 能用脱敏 trace 与指标定位故障。
- 本课新增：注入、记忆、工具、主体隔离攻击套件和发布/回滚门禁。
- 文件：`security_release_gate.py` 与 `test_security_release_gate.py`。
- 保存：安全套件指纹、阻断原因、备份状态和回滚目标。
- 下一阶段：在 RAG 应用工程中把这些边界接到真实文档、索引和管理台。
</section>

## 四类学习者入口

- 零基础兴趣：沿五个攻击 case 解释系统为什么拒绝。
- 有基础兴趣：实现 edit 审批与摘要绑定。
- 零基础求职：解释 Prompt 防注入为什么不等于完整安全。
- 有基础求职：设计跨主体、工具污染、发布与回滚门禁；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与固定安全报告通过。
- 五个攻击 fixture 全部阻断。
- 跨主体内容不进入候选、Prompt、日志或 trace。
- 高风险动作必须绑定具体批准。
- 发布需要测试、安全、备份和回滚目标同时满足。
- 固定套件不外推为生产环境绝对安全。

## 来源与版本

- 核查日期：2026-07-31。
- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [NIST AI RMF: Manage](https://airc.nist.gov/airmf-resources/playbook/manage/)

## 下一步

进入 RAG 应用工程第 1 课，把来源、版本、解析和异步索引作业接成真实闭环。
