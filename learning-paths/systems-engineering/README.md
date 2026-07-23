# 系统编程、并发、网络与性能

本组在 C++ 核心与 CS 系统基础之后，用一个“可诊断系统服务”连续建设六课。

当前进度：6 / 6，已开放。

1. [文件描述符、部分 I/O 与所有权](01-file-descriptors-partial-io-ownership.md)
2. [信号、进程监督与优雅停止](02-signals-process-supervision-graceful-shutdown.md)
3. [条件变量、有界队列与关闭协议](03-condition-variables-bounded-queue-shutdown.md)
4. [非阻塞网络、事件循环与背压](04-nonblocking-network-event-loop-backpressure.md)
5. [延迟分布、采样分析与性能预算](05-latency-distribution-sampling-performance-budget.md)
6. [故障注入、资源泄漏与恢复验收](06-fault-injection-resource-leaks-recovery-acceptance.md)

示例目标是 macOS/Linux 的 POSIX 教学环境；每课会明确哪些行为属于 POSIX、哪些属于标准 C++。
