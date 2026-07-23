# 可诊断系统服务 v0.3

v0.3 使用 C++20 mutex、condition_variable 和容量为 1 的有界队列。测试通过显式等待“生产者已经阻塞”的状态固定背压，不依赖 sleep 或调度运气。

```bash
../../../../.venv/bin/python -m unittest -v test_bounded_queue.py
```

关闭后拒绝新任务，已接受任务继续排空；队列关闭且排空后，消费者得到明确终止状态。
