# 可诊断系统服务 v0.2

v0.2 使用真实 SIGTERM、self-pipe、fork、kill 与 waitpid。信号处理器只保存信号号并向非阻塞 pipe 写一个字节；普通控制流负责停止、清理和回收子进程。

```bash
../../../../.venv/bin/python -m unittest -v test_signal_supervisor.py
```

`--child-exit 7` 用于验证子进程失败不会被监督器隐藏。目标环境是 macOS/Linux POSIX。
