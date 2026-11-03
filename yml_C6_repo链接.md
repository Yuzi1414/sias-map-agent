# C6 · 仓库链接

- GitHub 仓库：<https://github.com/Yuzi1414/sias-map-agent>
- 默认分支：`main`
- 线上部署分支：`gh-pages`（静态前端）
- 仓库可见性：Public

## 仓库结构（关键目录）

| 路径 | 说明 |
|------|------|
| `web/static/` | 前端（`index.html` + `style.css` + `app.js`） |
| `web/app.py` | Flask 后端（`/api/status`、`/api/chat`、根级静态路由） |
| `web/map_render.py` | Leaflet 地图渲染 + 分类配色 |
| `web/requirements.txt` | `flask>=2.2` + `requests>=2.28` |
| `src/` | 地图数据/核心逻辑 |
| `yml_C6_AI日志.md` | C6 AI 迭代日志 |
| `AI_LOG.md` / `README.md` | 项目说明与 AI 使用记录 |
| `ATTRIBUTION.md` / `LICENSE` | 数据来源归属与开源协议 |

## 技术要点

- 前端自包含、零后端依赖即可演示（客户端 demo 兜底）。
- 实时 AI 模式：本地 Ollama（`gemma4:e4b`，`http://localhost:11434`）+ Flask，`/api/chat` 返回 `{mode, reply, markers, map_html}`。
- 线上静态托管用 gh-pages 分支（无需 GitHub Actions workflow 权限）。
