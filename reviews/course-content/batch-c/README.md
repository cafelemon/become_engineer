# 课程内容架构样板 · 批次 C

<div class="be-sample-hero be-sample-hero--index" markdown="1">

<span class="be-sample-kicker">Web 与智能方向 · 独立评审环境</span>

## 数据从哪里来，程序凭什么相信它

这一批有四条数据流：浏览器向本地 API 要学习报告，模型从合成数据里学习规律，LLM 把一句话整理成固定字段，Agent 在规则允许后查询一门课程。每一页都先让结果跑起来，再拆开看中间发生了什么。

<div class="be-sample-actions" markdown="1">
[从浏览器请求开始](web-local-api.md){ .md-button .md-button--primary }
[直接看 Agent](agent-read-only-tool.md){ .md-button }
</div>

</div>

## 两条作品线

<div class="be-sample-card-grid" markdown="1">

<article class="be-sample-card" markdown="1">
### 可评估的智能学习助手

Web 先把学习报告送到浏览器；LLM 再把自然语言整理成可靠字段；Agent 最后只查询经过允许的课程信息。
</article>

<article class="be-sample-card" markdown="1">
### 结构化数据机器学习系统

AI 样板用合成学习记录练习数据划分、基线、训练、验证和错例检查。它只讲实验方法，不拿合成结果解释真实学习者。
</article>

</div>

## 四个样板

| 样板 | 读完以后能做什么 | 连续作品 | 状态 |
| --- | --- | --- | --- |
| [Web：浏览器怎样拿到学习数据](web-local-api.md) | 启动 FastAPI，让浏览器处理成功和失败响应 | 学习进度报告器 Web 入口 | 已验收 |
| [AI：第一次训练与验证](ai-reproducible-experiment.md) | 重跑一份固定实验，并读懂基线、指标和错例 | 结构化数据机器学习系统 | 已验收 |
| [LLM：把一句话变成可靠数据](llm-structured-output.md) | 校验模型返回的 JSON，而不是直接相信它 | 智能学习助手 P5.1 | 已验收 |
| [Agent：安全查询一门课程](agent-read-only-tool.md) | 看懂一次受限的只读工具调用 | 智能学习助手 P5.5 | 已验收 |

## 本地运行

安装离线样板依赖：

```bash
.venv/bin/pip install -r reviews/course-content/batch-c/requirements.txt
```

启动评审站点：

```bash
.venv/bin/mkdocs serve -f mkdocs.samples-c.yml -a 127.0.0.1:8768
```

Web 页面还需要另开一个终端启动本地 API：

```bash
.venv/bin/uvicorn app:app --app-dir reviews/course-content/batch-c/examples/web-api --port 8780
```

真实 DeepSeek 调用是可选项。请先在本机设置新的 `DEEPSEEK_API_KEY`，不要把密钥写进仓库或发到对话中。自动测试不访问外部 API。

!!! info "评审说明"
    批次 C 已通过用户评审，但仍不进入正式课程导航和搜索，也不增加正式课程数量。下一步和批次 A、B 做跨方向统一评审。
