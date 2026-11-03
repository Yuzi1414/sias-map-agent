# SIAS Map Agent — Web Application

用自然语言驱动郑州西亚斯学院周边交互式地图的 Web 应用（C6 交付物）。

## 这是什么

用户输入一句中文（如「学校附近有哪些好吃的」），后端调用本地大模型做
function calling，把 `add_marker` / `get_distance` / `finalize_map` 的工具调用
解析成地点列表，再由前端把 Leaflet 地图渲染出来。

- **真 AI 集成**：产品运行时会调用 Ollama 上的 `gemma4:e4b`，不是「AI 写代码但产品不调 AI」。
- **演示模式兜底**：未检测到本地 Ollama 时自动降级为规则匹配 + 示例数据，保证线上也能体验核心流程（输入 → 处理 → 输出地图）。
- **响应式**：手机浏览器可用，桌面端左右分栏（聊天 + 地图）。

## 本地运行

```bash
pip install -r requirements.txt
python app.py
# 打开 http://localhost:8000
```

需要本地 Ollama 已启动并拉取模型（否则走演示模式）：

```bash
ollama run gemma4:e4b
```

环境变量：`OLLAMA_BASE`（默认 `http://localhost:11434`）、`MODEL`（默认 `gemma4:e4b`）。

## 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 前端页面 |
| GET | `/api/status` | `{live_ai, model}`，是否连上本地模型 |
| POST | `/api/chat` | `{"message": "..."}` → `{mode, reply, markers, map_html}` |

## 部署

- 前端是纯静态（`static/`），可单独托管到 Vercel / Netlify / GitHub Pages。
- 后端是 Flask + 本地 Ollama。要「真 AI + 公网可访问」有两条路：
  1. 后端部署到带 GPU 的服务器（装 Ollama）；
  2. 本机跑后端 + Cloudflare Tunnel / ngrok 把本机端口暴露到公网（免费、真 AI、但需本机开机）。

## 目录

```
web/
  app.py           Flask 后端（agent loop + demo 兜底）
  map_render.py    Leaflet HTML 渲染
  static/          前端（index.html / app.js / style.css）
  requirements.txt
```
