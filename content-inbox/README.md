# Content Inbox

这里是素材收纳系统，用来把零散资料先归类、排队和标注处理动作。

`content-inbox/` 不是正式学习资料区，也不保存原始资料本体。它只记录公开仓库可以展示的素材索引、处理状态、归属主线和下一步动作。

## 使用原则

- 不写入账号、密码、访问 token、私人路径。
- 不上传下载的课程、PDF、视频或受版权保护原件。
- 有广告、重复、过时或错误风险的资料先进入 inbox，不直接进入正式目录。
- 每个素材必须映射到六条主线之一。
- 通过筛选后，再沉淀到 `resources/`、`reviews/`、`notes/`、`projects/` 或 `publications/`。
- 原始抓取内容、清洗中间产物和临时导出文件放入 `source-materials/` 的 ignored 子目录。

## 六条主线队列

- [工程基础](engineering-foundation.md)
- [编程语言](programming-languages.md)
- [Web 全栈](web-fullstack.md)
- [CS 核心](cs-core.md)
- [AI 基础](ai-foundation.md)
- [LLM/Agent](llm-agent.md)

## 素材状态

- `raw`：刚收录，未检查。
- `triaged`：已归类，知道大致用途。
- `dedupe-needed`：需要去重。
- `fact-check-needed`：需要纠错或更新核对。
- `ad-cleanup-needed`：需要去广告或营销内容。
- `project-pick-needed`：需要筛选可实践项目。
- `ready-for-review`：可进入资源评测。
- `ready-for-publication`：可整理为公开笔记、项目或文章。
- `rejected`：不适合公开沉淀。

## 处理流水线

```text
素材登记
  -> 主线归类
  -> 阶段判断
  -> 去重
  -> 去广告
  -> 事实核对
  -> 项目精选
  -> 进入正式目录
```

## 项目推动原则

理论和实践并行，但不强迫所有内容都做成独立项目。

- LLM、Agent、Web、AI、编程语言优先项目驱动。
- CS 核心优先用小实验、案例和题目验证。
- 工程基础更多作为其他项目中的实践规范，不强制单独做项目。
