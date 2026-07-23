# 算法演练运行器 v0.1

这个本机项目用真实 Python 子进程复现固定输入输出判题，不访问外网，也不包含外部题库题面。

```bash
../../../../.venv/bin/python -m unittest -v test_judge_runner.py
../../../../.venv/bin/python judge_runner.py
```

成功时三组原创用例全部通过。运行器区分 `wrong-answer`、`runtime-error` 与 `timeout`，固定输出不记录机器相关耗时。
