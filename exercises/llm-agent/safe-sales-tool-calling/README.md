# 安全销售查询 Tool Calling 练习

这是一个聚焦练习，不是独立长期项目。它服务于 [可评估的智能学习助手](../../../projects/intelligent-learning-assistant/README.md) 的 P5.5 里程碑：模型或离线模拟器提出结构化调用，应用验证参数，通过只读 SQLite 查询销售数据，再返回结构化结果。

它刻意不提供“执行任意 SQL”的工具。

## 关联课程或项目

- 对应笔记：[Tool Calling：让模型安全地使用外部能力](../../../notes/llm-agent/tool-calling.md)
- 对应项目：[可评估的智能学习助手](../../../projects/intelligent-learning-assistant/README.md)
- 对应里程碑：P5.5 Tool Calling

## 练习目标

- 理解模型提出调用、应用执行工具的职责边界。
- 使用工具白名单和参数校验处理不可信输入。
- 使用只读数据库连接和参数化 SQL。
- 在没有 API Key 的情况下测试完整工具调用流程。
- 可选接入 OpenAI Responses API。

## 练习结构

```text
safe-sales-tool-calling/
├── app.py
├── safe_sales.py
├── openai_adapter.py
├── data/
│   └── seed.sql
├── tests/
│   └── test_safe_sales.py
├── .env.example
└── requirements-openai.txt
```

运行时生成的 `data/sales.db` 被仓库 `.gitignore` 中的 `*.db` 规则排除。

## 离线运行

仅需要 Python 3.10 或更高版本：

```bash
cd exercises/llm-agent/safe-sales-tool-calling
python app.py --year 2025 --month 1
python app.py --year 2025 --month 1 --product Keyboard
```

第一次运行会根据 `data/seed.sql` 创建演示数据库。查询阶段始终通过 SQLite URI 的只读模式打开数据库。

输出包含模拟的 `function_call`、`function_call_output` 和最终工具结果，因此不调用模型也能观察完整协议。

## 运行测试

```bash
python -m unittest discover -s tests -v
```

测试覆盖正常查询、商品筛选、空结果、非法月份、未知工具、额外参数、恶意字符串、只读数据库和完整离线调用流程。

## 可选接入 OpenAI

安装练习目录内的可选依赖：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-openai.txt
```

设置环境变量：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="a-model-that-supports-function-calling"
```

然后运行：

```bash
python app.py --use-openai --prompt "2025 年 1 月 Keyboard 的销售情况"
```

代码使用 Responses API。练习不保存密钥，也不假设某个模型名称长期有效，因此必须通过 `OPENAI_MODEL` 显式选择模型。

## 安全设计

- 只注册 `get_monthly_sales` 一个业务工具。
- 拒绝未知工具、未知字段、错误类型和越界年月。
- 商品名称只作为 SQL 参数，不参与 SQL 结构拼接。
- 查询连接使用 `mode=ro`。
- 查询只访问固定的 `sales` 表，并限制最多返回 50 行。
- 金额使用整数分存储，避免浮点累计误差。
- OpenAI 工具循环最多执行 4 轮。
- API 缺失或可选 SDK 未安装时给出明确错误，不影响离线模式。

## 与知识笔记的关系

先阅读 [Tool Calling：让模型安全地使用外部能力](../../../notes/llm-agent/tool-calling.md)，再运行本练习。笔记解释协议和设计原则，练习负责验证这些原则能否落实。

## 验收标准

- 无 API Key 时离线示例和测试全部通过。
- 注入风格的商品名不会改变 SQL 结构或删除数据。
- 只读连接无法执行写操作。
- 工具输出能与原始 `call_id` 正确关联。
- 公开目录中不出现原素材、访问凭证或硬编码数据库口令。
