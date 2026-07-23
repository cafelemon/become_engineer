# 可诊断系统服务 v0.1

这个 POSIX 教学程序使用真实 `pipe/read/write/close/fcntl`，并用移动专属的 `UniqueFd` 管理描述符所有权。为了固定部分 I/O 路径，每次写最多请求 3 字节、每次读最多请求 4 字节。

```bash
../../../../.venv/bin/python -m unittest -v test_fd_pipeline.py
```

它适用于 macOS 与 Linux，不把 POSIX 接口描述成标准 C++ 或 Windows 通用接口。
