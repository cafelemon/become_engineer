<div class="be-tutor-mount" data-tutor-lesson="cs-systems-06" aria-hidden="true"></div>

<section id="overview-authorization-result" data-learning-context="overview-authorization-result" data-context-type="overview" markdown="1">

<div class="be-page-hero" markdown="1">
<span class="be-page-eyebrow">CS 系统基础 · 第六课 · 系统运行观察器 v0.6</span>

# 身份、授权与最小权限

## 已经登录，为什么仍不能执行诊断

```text
anonymous: status=401 challenge=Bearer
viewer: action=status:read status=200
denied: principal=viewer action=diagnostic:run status=403
operator: action=diagnostic:run status=200
audit: entries=4 raw_token_logged=False
```

匿名请求没有可验证身份，得到 401；viewer 已经通过认证，却没有运行诊断的权限，因此得到 403；operator 才能执行诊断。审计记录保留主体、动作和结果，但不保留原始令牌。

[运行权限实验](#reproduce-authorization-lab){ .md-button }
[先分清认证与授权](#concept-authn-authz){ .md-button .md-button--secondary }
</div>

<div class="be-page-summary" markdown="1">
  <div><span>课程位置</span><strong>CS 系统基础 · 6 / 6</strong></div>
  <div><span>项目版本</span><strong>系统运行观察器 v0.6</strong></div>
  <div><span>主要结果</span><strong>身份、动作权限、401/403、默认拒绝、日志脱敏</strong></div>
</div>

## 这节适合谁

- **小白**：先记住两个问题——“你是谁”和“你能做什么”不是同一个判断。
- **已有基础**：直接做跳过检查——能区分 401 与 403；能用动作权限实现最小授权；新动作默认拒绝；令牌不进代码和日志。都做到，可以完成本组课程。
- **兴趣学习**：增加一个只读动作，观察 viewer 与 operator 的权限集合怎样变化。
- **求职准备**：保存 401、403、200 和脱敏日志测试，练习解释认证、授权和最小权限的证据链。

四类画像共用系统运行观察器 v0.6。求职路线增加认证、授权和会话令牌的原创追问，不复制安全正文。

前置是[事务、隔离与并发写入](05-transactions-isolation-concurrent-writes.md)。上一课保护共享数据的一致性；本课决定哪个主体可以读取状态或触发诊断。

</section>

<section id="concept-authn-authz" data-learning-context="concept-authn-authz" data-context-type="concept" markdown="1">

## 认证回答是谁，授权回答能做什么

| 请求 | 认证结果 | 授权结果 | HTTP 状态 |
| --- | --- | --- | --- |
| 没有令牌或令牌无效 | 无身份 | 不继续判断动作 | 401 + `WWW-Authenticate` |
| viewer 读取状态 | viewer | 有 `status:read` | 200 |
| viewer 运行诊断 | viewer | 缺 `diagnostic:run` | 403 |
| operator 运行诊断 | operator | 有 `diagnostic:run` | 200 |

最小权限不是给每个人一个大角色再靠自觉少用，而是只授予完成当前工作所需的动作。本课直接保存权限集合：viewer 只有读取，operator 才增加诊断。

没有登记的 method/path 不会自动继承权限。路由表之外默认拒绝，新增功能必须显式选择动作和测试。

</section>

<section id="example-opaque-token" data-learning-context="example-opaque-token" data-context-type="example" markdown="1">

## 令牌只在签发时出现原文

```python
token = secrets.token_urlsafe(32)
digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
```

示例运行时生成高熵不透明令牌，调用者持有原文，服务端内存只保存摘要到 Principal 的映射。认证时先摘要候选令牌，再用 `hmac.compare_digest` 与已登记摘要比较。

摘要不能让泄漏的低强度密码变安全；这里能使用它，是因为令牌由安全随机数生成器产生且只存在本次进程。本课不实现账号密码、刷新、吊销、过期或跨服务会话。

</section>

<section id="example-policy-audit" data-learning-context="example-policy-audit" data-context-type="example" markdown="1">

## 权限检查和审计共用同一个动作名

路由表把 `GET /status` 映射到 `status:read`，把 `POST /diagnostics` 映射到 `diagnostic:run`。授权器检查 Principal 的 scopes，审计也记录同一个动作名：

```text
principal=viewer action=status:read result=200
principal=viewer action=diagnostic:run result=403
```

日志足以回答谁请求了什么、结果如何，但不包含 Authorization 头、原始令牌或请求正文。脱敏不是事后替换几个演示值，而是从日志字段设计上排除秘密。

</section>

<section id="reproduce-authorization-lab" data-learning-context="reproduce-authorization-lab" data-context-type="reproduce" markdown="1">

## 跑过匿名、越权和允许路径

完整示例在 `site-src/examples/cs-systems/runtime-observer-v06/`，只使用 Python 3.11 标准库。

```bash
cd site-src/examples/cs-systems/runtime-observer-v06
python authorization_lab.py
python -m unittest -v test_authorization_lab.py
```

你应该看到页面开头五行固定输出和 5 项测试通过。令牌每次运行都会变化，但不打印、不写文件、不进入固定输出；测试只验证状态、摘要存储和审计脱敏。

</section>

<section id="modify-readonly-action" data-learning-context="modify-readonly-action" data-context-type="modify" markdown="1">

## 增加日志摘要读取，不扩大诊断权限

新增 `GET /summary`，动作名为 `summary:read`。让 viewer 和 operator 都能读取摘要，但 viewer 仍不能运行诊断。先添加默认拒绝测试，再显式授予新 scope。

然后故意把新路由映射到 `diagnostic:run`，观察 viewer 得到 403。修复时修改权限模型，不要为了让测试变绿而把诊断权限送给 viewer。

</section>

<section id="troubleshoot-auth-boundary" data-learning-context="troubleshoot-auth-boundary" data-context-type="troubleshoot" markdown="1">

## 权限错误先分身份、策略和秘密处理

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| 所有请求都是 401 | Authorization 格式和令牌来源 | 使用 `Bearer <token>`，不要把摘要当原令牌发送 |
| 已认证却得到 403 | 当前主体是否有目标 action | 修正权限分配，不绕过授权器 |
| 新接口谁都能访问 | 未登记路由是否默认允许 | 路由之外默认拒绝，新增动作必须有测试 |
| viewer 能执行诊断 | 是否给了过宽 scope 或共享 operator 凭据 | 分开主体和令牌，只授予所需动作 |
| 日志出现长令牌 | 是否记录完整请求头 | 只记录 principal、action、result，轮换已暴露令牌 |
| 令牌写在源码里 | 是否用常量方便演示 | 运行时生成；生产使用受管密钥与身份系统 |
| 401 没有挑战头 | 是否遗漏 `WWW-Authenticate` | 按 HTTP 认证语义返回适用 challenge |

</section>

<section id="project-runtime-observer-v06" data-learning-context="project-runtime-observer-v06" data-context-type="project" markdown="1">

## 系统运行观察器 v0.6

| 六课形成的边界 | 可以证明 | 仍不声称 |
| --- | --- | --- |
| 进程与线程 | 退出、超时、竞态和互斥 | 生产监控与多核性能 |
| 内存与资源 | 引用、文件关闭和异常清理 | 跨语言完整内存模型 |
| 本机网络 | TCP、HTTP、404、超时和关闭 | 公网、DNS、TLS 与容量 |
| SQLite | 回滚、约束、写锁和读快照 | 分布式事务与高可用 |
| 身份与权限 | 401、403、动作授权和脱敏审计 | 生产 OAuth/OIDC 与账号体系 |

保存五行输出、5 项测试、权限矩阵和一份不含令牌的审计记录。系统运行观察器 v0.6 到此形成可运行、可解释、可排错的六课阶段作品。

</section>

<section id="deepen-security-boundary" data-learning-context="deepen-security-boundary" data-context-type="deepen" markdown="1">

## 这不是生产登录系统

本课不自制 JWT，不实现密码哈希、注册登录、令牌刷新与吊销，也没有 TLS。Bearer 令牌一旦泄漏，持有者就能使用它；明文 HTTP 只用于不经过网络的本机教学边界，不能承载生产凭据。

Web 工程化应选用成熟身份提供方和框架，使用 TLS、短期令牌或安全会话、密钥管理、撤销策略、资源级授权、CSRF 防护与安全审计。操作系统级用户、文件权限和容器身份也需要单独课程验证。

</section>

<section id="career-auth-evidence" data-learning-context="career-auth-evidence" data-context-type="career" markdown="1">

## 求职加练：不要把认证成功说成拥有全部权限

原创追问：viewer 能读取状态，但调用诊断得到 403；匿名请求得到 401；operator 调用成功，日志又不能暴露令牌。请画出凭据、Principal、scope、action、响应和审计的完整链路。

回答必须解释 401/403 差异、默认拒绝、最小权限和日志脱敏，并引用 5 项测试。这个追问由认证、授权和会话令牌能力信号重新设计，不复述外部题面。

</section>

## 完成检查

- [ ] 我能用自己的话区分认证和授权。
- [ ] 我能解释缺少身份的 401 与权限不足的 403。
- [ ] 我只给 viewer 读取权限，诊断权限留给 operator。
- [ ] 我确认未登记动作默认拒绝。
- [ ] 我没有在源码、存储或日志中保留原始令牌。
- [ ] 我能说明本课与生产 OAuth/OIDC、TLS 和账号系统的边界。

## 来源与版本

- 适用：Python 3.11+；示例是单进程、本机、短期不透明令牌的教学实现。
- 本课在 Python 3.11.9 与 Node.js 24.14.1 驱动的仓库验证脚本中复现；核查日期：2026-07-20。
- IETF：[RFC 9110：401、403 与 WWW-Authenticate](https://www.rfc-editor.org/rfc/rfc9110.html)。
- OWASP：[Authorization Cheat Sheet：最小权限与默认拒绝](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)。
- Python 官方：[secrets：安全随机令牌](https://docs.python.org/3.11/library/secrets.html)。
- Python 官方：[hmac.compare_digest](https://docs.python.org/3.11/library/hmac.html#hmac.compare_digest)。
- 验证方式：5 项 unittest、固定命令输出、课程根验证脚本；不访问网络、不使用真实凭据。

## 下一步

回到[CS 系统基础课程表](README.md)复查六课作品。完成组级验收后，可以按方向进入 Web 工程化或系统编程、并发、网络与性能；设备方向仍需先补 C 语言起步。
