# Study Progress Reporter

这是 Become Engineer 双语言学习进度报告器的 Python 包。运行时只使用 Python 3.11+ 标准库。

```bash
python -m pip install -e ".[dev]"
study-progress report
python -m study_progress_reporter report
python -m unittest discover -s tests -v
python -m mypy --strict src tests
```

示例配置见 `config.example.toml`。配置不会自动加载，必须通过 `--config` 显式指定。

