# 常见问题

## 为什么不直接只抓 alphaXiv？

因为 `alphaXiv` 很适合做增强，但 `arXiv` 仍然是更稳定的规范元数据来源。

## 这个项目会解析整篇 PDF 吗？

不会。当前目标是统一元数据提取和 Markdown dossier 生成，不是 PDF 全量结构化解析。

## 为什么输出里要有 `provider_trace`？

因为 agent 和自动化流程通常需要知道字段来自哪里、哪个 provider 失败了、哪些步骤被跳过了。
