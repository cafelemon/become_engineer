<div class="be-tutor-mount" data-tutor-lesson="llm-use-06" aria-hidden="true"></div>
<section id="overview-secure-delivery" class="be-page-hero be-lesson-hero" data-learning-context="overview-secure-delivery" data-context-type="overview" markdown="1">
<span class="be-page-eyebrow">模型使用与结构化输出 · 第 6 / 6 课 · 智能学习助手 P5.1 v0.6</span>
# Provider 配置、秘密、脱敏与可选真实验收
## 离线是默认交付，真实调用必须双重显式开启
```text
runtime=python:3.11+,dependencies:stdlib-only,network:disabled-by-default
default=mode:offline,provider:scripted,key-required:false
scripted=status:completed,request_id:req-scripted,calls:1
audit={"attempt":1,"event":"model_invocation","model":"learning-assistant-offline","provider":"scripted","request_id":"req-scripted","status":"completed"}
redaction=authorization:[REDACTED],prompt-logged:false,response-logged:false
real-call=gates:--real+ALLOW_REAL_PROVIDER=1,base-url:https,key:environment-only,ci:false
secret-boundary=process-memory:yes,config-repr:false,audit:false,evidence:false,source-control:false
delivery=offline-evidence:required,real-provider:optional,production-http-client:not-claimed
invariants=offline-default,fail-closed-config,redacted-observability,no-rag,no-tools
```
v0.6 默认运行离线证据，不要求密钥、不联网。provider 模式缺配置或密钥就拒绝启动；即使配置完整，也必须同时提供 CLI `--real` 和 `ALLOW_REAL_PROVIDER=1` 才允许网络调用。
</section>

<div class="be-lesson-overview">
  <div><span>课程位置</span><strong>LLM 应用起步 · 6 / 6</strong></div>
  <div><span>前置</span><strong>模型边界、Schema、恢复与流式闭环</strong></div>
  <div><span>环境</span><strong>Python 3.11+ · 标准库 · 离线默认</strong></div>
  <div><span>完成后留下</span><strong>交付 CLI、脱敏证据与 8 项测试</strong></div>
</div>

## 学习目标

- 把普通配置与运行时秘密分离，配置对象不保存 API key。
- provider 模式对 HTTPS、模型、timeout 和密钥执行启动门禁。
- 用 CLI 参数加环境开关形成真实调用双重确认。
- 只把密钥放入调用边界；审计、对象表示和交付证据都不包含原文。
- 用允许字段构造审计事件，并递归脱敏防御性诊断数据。
- 区分教学 HTTP 客户端、可选本机验收与生产秘密管理。

<section id="concept-config-secret-boundary" data-learning-context="concept-config-secret-boundary" data-context-type="concept" markdown="1">
## 配置可以展示，秘密只能短暂使用

`ProviderConfig` 保存 mode、provider、model、base URL 和 timeout，不保存 key。调用函数在最后边界从环境读取 key，构造 Authorization，然后只返回归一化结果。

环境变量仍会存在于进程内存，也可能被同权限诊断工具看到；它不是生产秘密管理器。这个实验只证明“不写进源码、配置对象、日志和证据”，不宣称内存中不存在秘密。
</section>

<section id="concept-fail-closed-delivery" data-learning-context="concept-fail-closed-delivery" data-context-type="concept" markdown="1">
## 错误配置不能悄悄降级成另一种行为

| 条件 | 结果 |
| --- | --- |
| 默认无配置 | offline scripted，可验收 |
| provider 无 HTTPS URL | `invalid_config` |
| provider 无 key | `missing_secret` |
| timeout 不在 1–120 秒 | `invalid_config` |
| 只有 `--real` | `real_call_not_enabled` |
| 只有环境开关 | `real_call_not_enabled` |
| 两个开关与完整配置 | 才进入 transport |

真实模式失败不会静默改用离线答案，否则用户可能误以为看到了 provider 结果。
</section>

<section id="example-redacted-audit" data-learning-context="example-redacted-audit" data-context-type="example" markdown="1">
## 审计采用允许列表，诊断对象再做递归脱敏

```python
event = {
    "event": "model_invocation",
    "provider": config.provider,
    "model": config.model,
    "request_id": result.request_id,
    "status": result.status,
    "attempt": attempt,
}
```

审计没有 Prompt、回复、Authorization 或 key。对 transport 诊断对象，`authorization`、`token`、`cookie`、`password`、`secret` 等键递归替换为 `[REDACTED]`。异常也被归一化，避免第三方异常链携带 header。
</section>

<section id="reproduce-delivery-v06" data-learning-context="reproduce-delivery-v06" data-context-type="reproduce" markdown="1">
## 先完成无密钥交付证据

```bash
cd site-src/examples/llm-use/intelligent-learning-assistant-v06
python3 -m unittest -v test_delivery_cli.py
python3 delivery_cli.py
```

8 项测试覆盖离线默认、配置门禁、HTTPS/timeout、双重确认、调用边界、递归脱敏、异常归一化和固定证据。自动测试只用 `ScriptedTransport`，不访问 provider。
</section>

<section id="modify-provider-config" data-learning-context="modify-provider-config" data-context-type="modify" markdown="1">
## 新增 provider 时不修改业务契约

1. 复制 `.env.example` 的占位字段到当前 shell，不把真实值写回文件。
2. 新建 adapter，把 provider 响应映射成 completed/refused/incomplete。
3. 保留第 2 课请求快照、第 3 课严格解析、第 4 课预算和第 5 课终止状态。
4. 加入 synthetic key 测试，扫描 stdout、stderr、审计和异常链。
5. 真实验收只在个人明确执行时运行，结束后撤销或轮换测试 key。

不要为了“通用”把不同 provider 的原始 JSON 泄漏到业务层。
</section>

<section id="troubleshoot-delivery-security" data-learning-context="troubleshoot-delivery-security" data-context-type="troubleshoot" markdown="1">
## 先判断是启动门禁、调用还是证据泄漏

| 现象 | 定位 |
| --- | --- |
| 默认运行要求 key | `MODEL_MODE` 默认值是否仍为 offline |
| provider 模式仍未调用 | 是否同时有 `--real` 与环境开关 |
| 配置报 HTTPS 错误 | base URL 是否明确以 `https://` 开头 |
| 日志出现 Prompt | 审计是否从允许字段构造 |
| 错误 traceback 出现 key | 是否保留了第三方异常链 |
| key 被提交 | 立即撤销/轮换，再清理历史；仅删当前文件不够 |
| 测试产生费用 | CI 是否误启真实开关或使用真实 transport |
</section>

<section id="deepen-production-secret" data-learning-context="deepen-production-secret" data-context-type="deepen" markdown="1">
## 生产方案还需要更多边界

生产系统应使用受控秘密注入或秘密管理器、最小权限 key、轮换、费用与速率限制、出口网络策略、TLS 校验、成熟 HTTP 客户端、可观测性和应急撤销。本课的 `urllib` 客户端只证明接口边界，不宣称连接池、生产重试或企业级证书策略。

Prompt 与回复也可能含个人或机密数据。默认不日志化只是起点；真实产品还需要数据分类、保留期限、用户告知和 provider 数据处理评审。
</section>

<section id="project-learning-assistant-v06" data-learning-context="project-learning-assistant-v06" data-context-type="project" markdown="1">
## 可评估的智能学习助手 P5.1 v0.6

- v0.1：可替换模型边界与归一化状态。
- v0.2：Prompt 角色、版本、参数与输入预算。
- v0.3：严格 JSON、Schema、语义校验和补问。
- v0.4：错误分类、timeout、deadline、退避与尝试预算。
- v0.5：有序 delta、唯一终止、部分结果和取消。
- v0.6：离线默认、provider 配置、秘密边界、脱敏审计与交付 CLI。

保存 48 项测试结果、60 张卡/120 条问法检索结果、严格构建、链接和多模式浏览器证据后，才把六课模块标记开放。
</section>

## 四类学习者入口

- 零基础兴趣：运行默认 CLI，逐项确认它没有密钥也能给出证据。
- 有基础兴趣：实现第二个 scripted adapter，保持同一归一化契约。
- 零基础求职：讲清“配置可展示、秘密不落日志、真实调用需确认”。
- 有基础求职：解释 fail closed、允许列表审计和异常链泄漏；本模块无招聘信号，不声称高频。

## 完成检查

- 8 项 unittest 与离线证据通过，默认不联网也不要求 key。
- provider 模式缺 HTTPS URL、合法 timeout 或 key 会拒绝启动。
- 真实调用必须同时有 CLI 与环境开关，CI 不设置二者。
- key 不进入 ProviderConfig、审计、stdout、stderr、异常消息或证据包。
- `.env.example` 只有占位值；真实 key 不写源码或版本库。
- 能明确说明环境变量、教学 transport 和可选真实调用不等于生产安全方案。

## 来源与版本

- 核查日期：2026-07-26。
- 适用环境：Python 3.11+ 标准库；自动验收离线。
- [OpenAI Production best practices](https://platform.openai.com/docs/guides/production-best-practices)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Python urllib.request](https://docs.python.org/3.11/library/urllib.request.html)

## 下一步

完成六课组级验收后进入“检索、RAG 与评估”；没有检索基线和固定评估集前，不提前建设 Agent。
