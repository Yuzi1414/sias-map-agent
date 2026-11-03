# AI 使用日志（AI_LOG）

本项目（SIAS Map Agent）是 C4 阶段「本地大模型 Agent 技能」的**开源化再封装**：把原本散落在本地工作区的技能与 demo，打包成一个别人能 `git clone` 后 5 分钟跑起来的公开仓库。全程 AI 辅助，本文件记录各阶段的 AI 用法、迭代过程与失败经验。

## 一、项目初始化

| 阶段 | AI 怎么用 | 具体做法 |
|------|----------|----------|
| 仓库骨架 | AI 生成标准结构 | 用 Claude 生成 `src/`（`config.py` / `agent.py` / `tools.py` / `render_map.py`）、`examples/`、`tests/`、`.github/workflows/` 目录结构 |
| README 模板 | AI 生成初稿 | 按 C5 的 README 模板（一句话说明、安装、示例、结构）生成初稿，再手动校正 |
| .gitignore | AI 生成 | 生成 Python 项目标准忽略规则 |

## 二、代码编写

| 阶段 | AI 怎么用 | 具体做法 |
|------|----------|----------|
| 核心代码 | 多轮迭代 | `agent.py`（函数调用主循环）、`tools.py`（haversine 测距 + marker 工具）、`render_map.py`（Leaflet 模板）由 AI 生成，我逐行复核并修正 |
| 测试 | AI 生成 + 手动补 | AI 生成 `test_tools.py` / `test_render_map.py`，我补充边界断言（同点距离=0、已知纬度差≈111 km） |
| CI | AI 生成 | AI 生成 GitHub Actions 工作流，push/PR 时自动跑 `unittest discover` |

## 三、文档撰写

| 阶段 | AI 怎么用 |
|------|----------|
| README | AI 基于代码生成初稿，我手动校准命令路径与示例 |
| ATTRIBUTION / CONTRIBUTING | AI 生成，我核对各依赖的真实许可（Gemma 4 Apache 2.0 / Leaflet BSD-2 / OSM ODbL / Ollama MIT） |

## 四、代码审查与 Debug

- **AI review**：让 AI 审查 `render_map.py` 的脚本注入风险 → 采用 `json.dumps(..., ensure_ascii=False).replace("</", "<\\/")` 转义 `</`，防止标记描述里的 `</script>` 破坏页面。
- **AI review**：让 AI 检查 `tools.py` 的 `execute_tool` 分支，确认未知工具名会抛 `ValueError` 而非静默失败。

## 五、迭代过程与失败经验（承自 C4）

1. **双语描述偏英文**：C4 阶段模型生成的 `description` 字段中英文比例失衡、英文偏多，中文可读性不足。C5 在 `tools.py` 的 schema 里把 `description` 明确标注为「1-2 句中英文描述」，并保留 `name_zh` 中文名字段，缓解但未完全根治。
2. **地名张冠李戴**：模型曾把「郑州西亚斯学院主校门」生成成「西雅斯大学主校门」（音译回译错误）。这说明本地小模型对中文地名的事实性仍不可靠——工具层只做执行、不硬编码地点，本意是让模型灵活生成，但也放大了幻觉风险。C5 在 README 里以真实示例指令显式引导「郑州西亚斯学院」。
3. **依赖最小化**：为满足「clone 后 5 分钟跑起来」，刻意保持**纯 Python 标准库 + 零 pip 依赖**，把唯一的外部运行依赖收敛到 Ollama 与浏览器。

## 六、手动步骤的反向举证

以下内容为**手动指定**，非 AI 生成：

- `config.py` 中的 `OLLAMA_ENDPOINT`、`MODEL=gemma4:e4b`、`QUANTIZATION=Q4_K_M`、`DEVICE`（真实机器信息）、`SIAS_CENTER=(34.40, 113.73)` —— 这些反映真实运行环境与真实地标，AI 生成会编造，故手动填入。
- 项目名 `sias-map-agent`、仓库归属 `Yuzi1414`、署名 `yml` —— 命名规范由用户决定。
- 各依赖的许可信息（ATTRIBUTION）—— 逐一核对官方仓库，非 AI 编造。
