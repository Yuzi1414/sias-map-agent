# C6 Web Application — AI 使用日志

> 姓名缩写：yml ｜ 挑战：C6 Web Application（ch-20260717031519-qqqx60）

## 一、分工

| 角色 | 做了什么 |
| --- | --- |
| 人类（虞梦琳 / yml） | 定方向（把 C5 的 SIAS Map Agent 升级为 Web 应用）、提供本地 Ollama 环境、最终提交确认 |
| AI（Commander） | 需求解析、前后端代码编写、本地真机调试与冒烟测试、本日志撰写 |
| 产品内 AI（本地 gemma4:e4b） | 运行时 function calling（add_marker / get_distance / finalize_map），把自然语言转成地图标记 |

## 二、真实迭代记录（含失败与修复）

### 迭代 1 — 需求纠偏
- **现象**：先入为主把 C6 当成「版本归档权限」模板，本地已有同名 .md / .docx 模板文档。
- **修复**：调用平台 `get-challenge` 权威接口，确认 C6 实为「**C6 Web Application**」，必交物 = `app链接 / demo / repo链接 / AI日志`。
- **教训**：交付前必须以平台 challenge 正文为准，不能用本地旧文件或记忆推测挑战含义。

### 迭代 2 — live 路径读超时
- **现象**：首次 live 调用 90s 读超时（`Read timed out`），demo 模式正常。
- **根因**：`gemma4:e4b`（4B）在 4GB 显存机器上跑 function calling 较慢，非流式请求要等全部生成完才返回，触发 90s 超时。
- **修复**：改为流式 `stream=True` + 读超时 300s + `max_tokens=1024`；标记数要求 8 → 5。
- **结果**：实测 54.6s 完成 5 个标记。

### 迭代 3 — 中文乱码
- **现象**：流式结果里中文变成 mojibake（"一家" → `ä¸å®¶`）。
- **根因**：`requests` 的 `iter_lines(decode_unicode=True)` 按响应头推断字符集（默认 ISO-8859-1），把 UTF-8 字节解错。
- **修复**：改手动逐行 `bytes.decode("utf-8", errors="replace")`。
- **结果**：中文正常输出（如「本地特色餐厅A」）。

### 其他工程决策
- Ollama 端点 / 模型名做成环境变量（`OLLAMA_BASE` / `MODEL`），方便切换云端 API 或更换模型。
- 已装本地模型：`gemma4:e4b`、`qwen3:4b`（此前 C2A 下载的 qwen2.5 已不在列表）。

## 三、真机验证结果

| 检查项 | 结果 |
| --- | --- |
| demo 模式（未连本地模型） | ✅ 6 个标记，<1s，中文正常 |
| live 模式（真实 function calling） | ✅ 5 个标记，54.6s，中文正常 |
| `GET /api/status` | ✅ 正确报告 `live_ai=true` + `model=gemma4:e4b` |
| 首页 `GET /` | ✅ 200，正常返回前端 |
| 空消息 | ✅ 400 拒绝 |
| Leaflet 地图 HTML | ✅ 两模式均含 `leaflet` 渲染 |

## 四、AI 集成层次（对应 C6 三层次）

属于 **🔵 进阶（多步 workflow）**：产品运行时真实调用 AI 做多步 function calling，不是「AI 只写代码、产品不调 AI」，也不是假集成按钮。

## 五、诚实声明

- live 模式在低显存机器上较慢（约 1 分钟/次），demo 模式即时兜底，保证线上也能体验核心流程。
- 部署公网后，本地 Ollama 无法被公网直达，需在「云端 LLM API / 本机隧道 / 仅前端+demo 兜底」三选一（见 README「部署」）。
