# Tool Calling：让模型安全地使用外部能力

## 笔记定位

- 类型：项目型笔记
- 所属主线：LLM/Agent
- 学习模块：工具调用、安全与错误恢复
- 关联项目：[可评估的智能学习助手](../../projects/intelligent-learning-assistant/README.md)
- 项目里程碑：P5.5 Tool Calling

## 前置知识

- Python 函数、字典、JSON 和异常处理。
- API 请求与响应的基本概念。
- 参数校验、最小权限和单元测试。

## 本章推进

- 新增能力：让模型提出结构化工具请求，由应用验证和执行。
- 实际产出：[安全销售查询 Tool Calling 练习](../../exercises/llm-agent/safe-sales-tool-calling/README.md)。
- 验收方式：未知工具、非法月份、额外字段、恶意参数和数据库写入均被拒绝。
- 下一步状态：在智能学习助手中建立受控工具注册表，并纳入统一日志和评估。

Tool Calling，也常被称为 Function Calling，是大模型应用中的一种协作协议：模型根据用户意图提出结构化的工具调用请求，应用程序检查请求、执行真实代码，再把结果交还给模型组织回答。

最重要的边界是：

> 模型不直接执行函数。模型只能提出“想调用什么、参数是什么”，是否执行以及如何执行始终由应用程序决定。

这一区分决定了系统能否测试、审计和控制风险。

## 适合什么时候使用

模型擅长理解自然语言和识别意图，但以下能力更适合交给工具：

- 查询实时、私有或业务数据库中的信息。
- 执行计算、格式转换和确定性规则。
- 调用搜索、地图、支付、邮件等外部服务。
- 触发需要权限控制和审计的业务操作。

不要因为有了工具，就默认允许模型访问整个系统。一个好工具应暴露最小、明确的业务能力，例如 `get_monthly_sales`，而不是 `execute_sql` 或 `run_shell_command`。

## 五步流程

### 1. 应用定义工具

工具定义至少包含名称、用途和参数 Schema。下面是一个销售查询工具的简化定义：

```python
SALES_TOOL = {
    "type": "function",
    "name": "get_monthly_sales",
    "description": "查询指定月份的销售汇总，可按商品名称筛选。",
    "parameters": {
        "type": "object",
        "properties": {
            "year": {"type": "integer"},
            "month": {"type": "integer", "minimum": 1, "maximum": 12},
            "product_name": {"type": ["string", "null"]},
        },
        "required": ["year", "month", "product_name"],
        "additionalProperties": False,
    },
    "strict": True,
}
```

工具描述也是模型判断是否调用工具的重要上下文，因此应该清楚、具体，避免多个工具职责重叠。

### 2. 模型提出调用请求

用户问“2025 年 1 月键盘卖了多少”，模型可能返回：

```json
{
  "type": "function_call",
  "name": "get_monthly_sales",
  "arguments": {
    "year": 2025,
    "month": 1,
    "product_name": "Keyboard"
  }
}
```

这只是候选请求，不代表参数可信，更不代表工具已经执行。

### 3. 应用验证并执行

应用至少要检查：

- 工具名是否存在于允许列表。
- 参数是否为合法 JSON，字段和类型是否符合预期。
- 年月、长度、枚举等业务规则是否成立。
- 当前用户是否有权限执行该工具。
- 操作是否需要人工确认。

通过检查后，应用调用自己的 Python 函数、数据库查询或外部 API。工具实现不应根据模型返回的字符串临时拼接 SQL、命令行或代码。

### 4. 应用回传工具结果

在 Responses API 中，应用使用对应的 `call_id` 回传 `function_call_output`。结果应保持结构清晰，并限制字段和数据量。

```python
input_items.append({
    "type": "function_call_output",
    "call_id": call_id,
    "output": json.dumps(tool_result),
})
```

工具失败时也应返回结构化错误，例如参数错误、权限不足或服务暂时不可用，而不是把内部堆栈、凭据或数据库细节交给模型。

### 5. 模型生成回答或继续调用

模型读取工具结果后，可以：

- 生成最终自然语言回答。
- 根据结果再调用另一个工具。
- 在信息不足时请求用户补充。

应用应为循环设置最大轮数和最大工具调用数，防止错误配置或不稳定输出造成无限调用。

## Schema 校验不是安全边界

严格 JSON Schema 能减少字段缺失、类型错误和额外参数，但它不能解决全部问题：

- `month=99` 可能满足宽松的整数类型，却不符合业务规则。
- 合法字符串仍可能包含 SQL 注入、路径穿越或命令注入载荷。
- 合法工具调用仍可能超出当前用户权限。
- 外部文档、网页和数据库内容可能包含提示注入文本。

因此需要两层检查：

1. Schema 控制数据形状。
2. 应用代码控制业务规则、权限和副作用。

## 数据库工具的安全设计

入门示例经常让模型生成 SQL，再直接交给数据库执行。它看起来灵活，却把数据库权限暴露给了概率性输出。

更稳妥的做法是：

- 将工具设计为明确的业务能力。
- 数据库账号和连接使用最小权限，查询场景优先只读。
- SQL 结构由开发者预先编写，值使用参数化查询。
- 对表、列、时间范围、结果条数和执行时间设置限制。
- 写入、删除、付款和发送等高风险动作要求显式确认。

本仓库的 [安全销售查询练习](../../exercises/llm-agent/safe-sales-tool-calling/README.md) 使用只读 SQLite 连接和固定参数化查询演示这些原则。

## 多工具与异常处理

一个真实的工具循环需要处理正常路径以外的情况：

- **未知工具**：拒绝执行并返回允许的工具范围。
- **参数解析失败**：返回可理解的参数错误，不猜测缺失字段。
- **工具内部失败**：记录内部日志，对模型只返回必要信息。
- **空结果**：返回成功但数据为空，不把“没有数据”误判为系统错误。
- **并行或连续调用**：分别绑定每个 `call_id`，避免结果错配。
- **循环失控**：设置轮数、调用数、超时和成本上限。

## 与旧版示例的差异

历史教程常使用 Chat Completions 的 `tool_calls` 消息和具体旧模型名称。核心思想仍然相同，但当前公开示例以 Responses API 为主：

- 模型输出中读取 `function_call`。
- 应用执行工具。
- 使用 `function_call_output` 和原 `call_id` 回传结果。
- 保留模型输出项，供下一轮请求继续使用。

学习时应优先掌握协议和安全边界，不要把某个模型名称、SDK 对象结构或历史兼容写法当成长期不变的知识。

## 自测问题

1. 为什么模型返回工具参数后不能直接执行？
2. JSON Schema 和业务校验分别解决什么问题？
3. 为什么 `get_monthly_sales` 比 `execute_sql` 更适合作为公开工具？
4. 工具返回错误时，哪些信息不应交给模型？
5. 连续工具调用为什么需要最大轮数？

## 关联基础课

- [工程基础](../../learning-paths/engineering-foundation/README.md)：测试、日志、密钥和最小权限。
- [编程语言](../../learning-paths/programming-languages/README.md)：Python 函数、类型、JSON 和异常处理。
- [Web 全栈](../../learning-paths/web-fullstack/README.md)：API、数据库和权限边界。
- [CS 核心](../../learning-paths/cs-core/README.md)：数据库查询、系统边界和并发调用。

## 来源与延伸阅读

- [OpenAI Function Calling 指南](https://developers.openai.com/api/docs/guides/function-calling)
- [OpenAI Tools 指南](https://developers.openai.com/api/docs/guides/tools)
- [Python sqlite3 文档](https://docs.python.org/3/library/sqlite3.html)
- [OWASP LLM Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

本文基于多份历史学习素材重新组织，并以当前官方文档和本地可运行测试进行核查。未复用原素材中的广告、截图、凭据或大段代码。
