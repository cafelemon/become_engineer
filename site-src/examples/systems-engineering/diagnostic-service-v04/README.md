# 可诊断系统服务 v0.4

这一版本用真实 POSIX `socketpair` 演示非阻塞发送、`EAGAIN` 背压、
`poll` 写就绪、对端排空与恢复发送。实验不连接外网，也不使用 Mock。

```bash
../../../../.venv/bin/python -m unittest -v test_nonblocking_socket.py
```

固定输出只记录状态迁移，不记录内核缓冲区大小、循环次数或耗时。程序用有界写入
循环避免错误实现无限运行，用 RAII 在正常或异常路径关闭两个描述符。
