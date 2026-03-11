# 架构说明

`paperfetch` 的核心流程是“归一化输入 -> 拉取 provider -> 合并结果 -> 输出统一 schema”。

## 主流程

1. `normalize_input(...)` 识别输入类型并标准化成内部表示
2. `ArxivProvider` 负责拉取规范元数据
3. `AlphaXivHtmlProvider` 负责解析 alphaXiv 页面中的 HTML 和 JSON-LD
4. `AlphaXivMentionsProvider` 在拿到 group ID 时补充 mentions
5. 合并逻辑统一处理字段优先级、warnings 和 provider_trace

## 优先级

- `arXiv` 优先：ID、日期、分类、PDF 链接
- `alphaXiv` 只做增强：讨论链接、互动指标、mentions、图片

## 错误处理

- provider 失败不会默认中断整个提取
- 失败和跳过都会记录到 `provider_trace`
- 下游系统应同时检查 `warnings` 和实际字段值
