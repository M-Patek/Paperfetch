# 快速开始

## 安装

只安装核心功能：

```bash
pip install -e .
```

安装开发和 demo 依赖：

```bash
pip install -e ".[dev,demo]"
```

## 常用命令

提取 JSON：

```bash
paperfetch extract 2301.12345 --format json
```

提取 Markdown dossier：

```bash
paperfetch extract https://www.alphaxiv.org/abs/2301.12345 --format md
```

批量处理：

```bash
paperfetch batch examples/papers.txt --format ndjson
```

启动本地 demo：

```bash
paperfetch serve --host 127.0.0.1 --port 8000
```
