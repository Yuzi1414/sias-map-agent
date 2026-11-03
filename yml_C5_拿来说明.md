# C5 拿来说明（Attribution）

> 本文件与仓库内 `ATTRIBUTION.md` 同源，为 C5 平台交付物版本。

本项目遵循「拿来主义」原则——凡是借鉴、参考、复用的公开成果，均在此说明来源与许可。

## 模型

| 项目 | 用途 | 许可 | 来源 |
|------|------|------|------|
| **Gemma 4（E4B）** | 本地推理，驱动函数调用 Agent | Apache 2.0 | Google DeepMind，经 [Ollama](https://ollama.com) 拉取运行 |

## 前端与地图

| 项目 | 用途 | 许可 | 来源 |
|------|------|------|------|
| **Leaflet.js 1.9.4** | 交互式地图渲染 | BSD-2-Clause | https://leafletjs.com |
| **OpenStreetMap 瓦片** | 底图 | ODbL | © OpenStreetMap contributors |

## 运行时

| 项目 | 用途 | 许可 | 来源 |
|------|------|------|------|
| **Ollama 0.35.1** | 本地大模型运行环境 | MIT | https://ollama.com |

## 借鉴思路

- **函数调用（Function Calling）Agent 架构**：参考 OpenAI 的 `tools` JSON Schema 规范（`type: function` + `parameters`），并适配 Ollama 的 OpenAI 兼容 `/chat/completions` 端点。
- **地点数据「模型生成而非硬编码」** 的设计：借鉴让模型实时决策、工具层只负责执行与记录的通用 Agent 实践。

> 若发现有来源遗漏或版权问题，欢迎提 Issue，我会尽快补充或移除。
