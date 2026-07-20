<div class="be-tutor-mount" data-tutor-lesson="cs-systems-04" aria-hidden="true"></div>

<section id="overview-network-result" data-learning-context="overview-network-result" data-context-type="overview" markdown="1">

<div class="be-page-hero" markdown="1">
<span class="be-page-eyebrow">CS 系统基础 · 第四课 · 系统运行观察器 v0.4</span>

# 从端口到 HTTP 的本机网络链路

## TCP 连上了，为什么请求仍可能失败

```text
tcp: connected=True loopback=True
http: status=200 body={"status":"ok"}
http error: status=404
timeout: timed_out=True cleaned_up=True
```

第一行只证明客户端连到了本机监听端口；第二、三行才进入 HTTP 消息和应用结果；最后一行说明已经连接也可能等不到响应，而且超时后双方仍要关闭资源。

[运行本机网络实验](#reproduce-local-network){ .md-button }
[看清调用链](#concept-port-to-http){ .md-button .md-button--secondary }
</div>

<div class="be-page-summary" markdown="1">
  <div><span>课程位置</span><strong>CS 系统基础 · 4 / 6</strong></div>
  <div><span>项目版本</span><strong>系统运行观察器 v0.4</strong></div>
  <div><span>主要结果</span><strong>回环地址、临时端口、TCP、HTTP、超时</strong></div>
</div>

## 这节适合谁

- **小白**：把端口想成进程在主机上登记的接收入口，先按时序图区分连接和消息。
- **已有基础**：直接做跳过检查——能解释 bind/listen/accept 与 connect；能手读一条 HTTP 状态行；能区分连接拒绝、404 和响应超时。都做到，可以进入下一课。
- **兴趣学习**：增加一个本机路径和 JSON 响应，观察状态行与消息体怎样变化。
- **求职准备**：保存一次 TCP 成功但 HTTP 失败的故障分层，练习按链路定位而不是笼统说网络挂了。

四类画像共用系统运行观察器 v0.4。求职路线增加 HTTP 生命周期和分层诊断追问，不复制网络正文。

前置是[内存、文件与资源生命周期](03-memory-file-resource-lifecycle.md)。你已经知道资源需要明确关闭；本课把同样责任应用到监听 socket、已连接 socket 和服务线程。

</section>

<section id="concept-port-to-http" data-learning-context="concept-port-to-http" data-context-type="concept" markdown="1">

## 一次本机请求跨过三层结果

```text
服务端进程                         客户端进程
socket → bind(127.0.0.1:0)
       → listen
       → accept  <────────────── create_connection
已连接 socket <─────────────── TCP 字节流
       ← GET /health HTTP/1.1
       → HTTP/1.1 200 OK + JSON
close          ───────────────→ close
```

- IP 地址选择哪台主机；`127.0.0.1` 只回到当前主机。
- 端口把到达这台主机的连接交给某个监听 socket。端口 `0` 只用于绑定时请系统分配可用端口，客户端使用分配后的真实数字。
- TCP 提供有序字节流，不认识 JSON、路径或 404。
- HTTP 规定怎样把请求行、头、正文和状态码组织在字节流中。

所以“能连接”和“业务成功”不能合并成一个布尔值。

</section>

<section id="example-http-message" data-learning-context="example-http-message" data-context-type="example" markdown="1">

## 先读原始消息，再谈框架

客户端实际发送的开头是：

```http
GET /health HTTP/1.1
Host: 127.0.0.1:<动态端口>
Connection: close
```

服务端返回：

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 15
Connection: close

{"status":"ok"}
```

`Content-Length` 是字节长度，不是字符数量；这个示例只解析自己生成的最小消息，不能当作生产 HTTP 服务器。真正服务应使用经过验证的 HTTP 实现处理分块、持久连接、非法输入和安全限制。

</section>

<section id="example-deterministic-timeout" data-learning-context="example-deterministic-timeout" data-context-type="example" markdown="1">

## 超时由调用者期限决定

`/wait` 路径不是随机睡一会儿。服务端收到请求后设置事件，然后等待测试释放响应；客户端把读取期限设为 `0.02` 秒，因此一定先进入 `socket.timeout`。测试随后释放服务端，让线程和 socket 正常退出。

超时表示调用者在期限内没有拿到下一批数据，不等于服务端一定没处理，也不等于 TCP 从未连接。真实系统重试前还要考虑请求是否可能已经产生副作用。

</section>

<section id="reproduce-local-network" data-learning-context="reproduce-local-network" data-context-type="reproduce" markdown="1">

## 在一台机器上跑完整链路

完整示例在 `site-src/examples/cs-systems/runtime-observer-v04/`，只使用 Python 3.11 标准库。

```bash
cd site-src/examples/cs-systems/runtime-observer-v04
python local_network_lab.py
python -m unittest -v test_local_network_lab.py
```

服务端只绑定 `127.0.0.1:0`，不会访问外网，也不会占用固定端口。你应该看到页面开头的四行结果和 4 项测试通过。测试断言端口大于 0，但不把每次变化的端口写进快照。

</section>

<section id="modify-local-route" data-learning-context="modify-local-route" data-context-type="modify" markdown="1">

## 增加 `/version`，别把未知路径当成功

让服务端在 `/version` 返回 `200` 和 `{"version":"0.4"}`，其他未知路径继续返回 `404`。先写测试，再改路由判断和固定输出。

然后把客户端读取期限从 `0.02` 改成 `0.2` 秒，但仍不要释放事件。运行前预测结果：期限变长只意味着等得更久，不会自动把未发送的响应变成成功。

</section>

<section id="troubleshoot-local-network" data-learning-context="troubleshoot-local-network" data-context-type="troubleshoot" markdown="1">

## 从最靠近本机的边界开始查

| 看到什么 | 先查哪里 | 怎样回来 |
| --- | --- | --- |
| `ConnectionRefusedError` | 地址和端口是否真的在 listen | 先启动服务端，读取系统分配的真实端口 |
| bind 报地址已占用 | 是否写死端口或旧进程仍监听 | 使用端口 0 做测试，生产端口则查清占用者 |
| TCP 已连接但得到 404 | 请求路径和 HTTP 状态行 | 修正路径，不要把 404 当网络断开 |
| 一直等响应 | 客户端是否设置读取期限 | 设置 timeout，记录请求可能已到服务端 |
| 只收到部分响应 | 是否假设一次 recv 就是完整消息 | 循环读取并按协议长度或连接结束组装 |
| 测试结束后进程不退出 | 服务线程或 socket 是否仍存活 | 释放事件、关闭双方 socket 并 join 线程 |
| localhost 在不同机器行为不一致 | 名称解析是否选择 IPv4/IPv6 | 本课明确使用 `127.0.0.1`，DNS 留到深化 |

</section>

<section id="project-runtime-observer-v04" data-learning-context="project-runtime-observer-v04" data-context-type="project" markdown="1">

## 系统运行观察器 v0.4

| v0.3 已有 | v0.4 新增 | 下一版继续 |
| --- | --- | --- |
| 文件和临时资源关闭 | 回环地址与动态端口 | SQLite 独立连接 |
| 正常／异常退出清理 | TCP 连接与 HTTP 消息 | 事务回滚与写锁 |
| 所有权和生命周期 | 404、超时和 socket 回收 | 一致性读取 |

保存四行输出、4 项测试和一张调用时序图。观察器现在能回答“连接是否建立、协议返回什么、期限内是否完成、资源是否回收”四个不同问题。

</section>

<section id="deepen-network-boundary" data-learning-context="deepen-network-boundary" data-context-type="deepen" markdown="1">

## 本机回环不能证明互联网和生产性能

回环实验没有经过交换机、路由器、DNS、TLS、代理或公网防火墙，也不能代表真实延迟、吞吐和丢包。它证明的是客户端与服务端 API、TCP 字节流、HTTP 消息和资源清理的最小关系。

系统工程会继续进入并发连接、非阻塞 I/O、连接池和性能测量；Web 工程化会继续进入 TLS、反向代理、认证、部署和可观测性。

</section>

<section id="career-network-triage" data-learning-context="career-network-triage" data-context-type="career" markdown="1">

## 求职加练：别用“网络问题”结束排查

原创故障场景：客户端已经连到本机端口，却得到 404；改对路径后又在等待响应时超时。请按监听、连接、HTTP 请求、应用状态、响应期限和资源清理六层说明证据。

至少引用本课的 200、404、timeout 和 cleaned_up 测试结果。这个追问来自 HTTP 生命周期与系统可靠性能力信号，只使用能力方向，不声称是任何企业原题。

</section>

## 完成检查

- [ ] 我能解释地址、端口、TCP 和 HTTP 分别解决什么问题。
- [ ] 我能画出 bind/listen/accept 与 connect 的顺序。
- [ ] 我能从原始消息读出请求路径、状态码和正文长度。
- [ ] 我能区分连接拒绝、404 和响应超时。
- [ ] 我增加了 `/version` 并保留未知路径 404 测试。
- [ ] 我确认超时后服务线程和 socket 都被回收。

## 来源与版本

- 适用：Python 3.11+，IPv4 本机回环；不访问 DNS、外网或 TLS。
- 本课在 Python 3.11.9 与 Node.js 24.14.1 驱动的仓库验证脚本中复现；核查日期：2026-07-20。
- Python 官方：[socket：底层网络接口](https://docs.python.org/3.11/library/socket.html)。
- IETF：[RFC 9293：TCP](https://www.rfc-editor.org/rfc/rfc9293.html)。
- IETF：[RFC 9110：HTTP 语义与状态码](https://www.rfc-editor.org/rfc/rfc9110.html)。
- 验证方式：4 项 unittest、固定命令输出、课程根验证脚本；仅使用 `127.0.0.1` 与动态端口。

## 下一步

进入[事务、隔离与并发写入](05-transactions-isolation-concurrent-writes.md)。下一课会把两个并发参与者从 socket 两端换成 SQLite 独立连接，观察回滚、写锁和事务快照。
