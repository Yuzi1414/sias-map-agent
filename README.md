# SIAS Map Agent 🗺️

> **输入一句自然语言指令，就能得到一张郑州西亚斯学院（SIAS）周边的交互式地图。**

一个**纯本地、零云端依赖**的函数调用（Function Calling）Agent：由本地运行的 **Gemma 4**（Ollama）驱动，理解你的自然语言指令，自主调用工具在地图上打点、测距，最终渲染出一张可缩放、可点击的 **Leaflet** 交互式地图。所有地点数据由模型实时生成，工具层不硬编码任何地点。

## ✨ 特性

- **本地模型驱动**：Gemma 4（4B，Q4_K_M 量化）通过 Ollama 在本地推理，数据不出本机
- **函数调用（Function Calling）**：模型自主决策调用 `add_marker` / `get_distance` / `finalize_map` 三个工具
- **纯 Python 3 标准库**：除 Ollama 与浏览器外，无任何第三方 pip 依赖
- **交互式地图**：Leaflet.js 渲染，可缩放、点击标记查看详情
- **可复现**：坐标、描述全部由模型生成，同一指令可反复复现流程

## 📋 环境要求

- Windows 11（示例环境），实际跨平台（Windows / macOS / Linux）
- Python 3.10+
- [Ollama](https://ollama.com) 并拉取模型：`ollama pull gemma4:e4b`

## 📦 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Yuzi1414/sias-map-agent.git
cd sias-map-agent

# 2. 拉取本地模型（首次）
ollama pull gemma4:e4b

# 3. 确认 Ollama 服务已启动
ollama serve
```

> 本项目不依赖任何第三方 pip 包，**无需 `pip install`**。

## 🖥️ 使用示例

```bash
python src/agent.py "给我生成一张郑州西亚斯学院周边的地图，标出校门、宿舍和食堂"
```

运行后生成两个文件：

- `examples/sias_map.html` —— 交互式地图（浏览器打开即可查看）
- `examples/runlog.txt` —— 本次运行完整日志（模型决策、工具调用、token 统计）

### 一句话跑通

```bash
python src/agent.py "标出郑州西亚斯学院的南门、北门和图书馆，并告诉我南门到图书馆的距离"
```

## 🗂️ 项目结构

```
sias-map-agent/
├── src/
│   ├── __init__.py       # 包标记
│   ├── config.py         # 配置与常量（模型、端点、中心坐标、设备信息）
│   ├── agent.py          # Agent 主循环（Gemma 4 函数调用）
│   ├── tools.py          # 工具集：add_marker / get_distance / finalize_map
│   └── render_map.py     # Leaflet 交互式地图渲染
├── examples/
│   ├── sias_map.html     # 示例交互式地图（真实运行产物）
│   └── runlog.txt        # 示例运行日志
├── tests/
│   ├── test_tools.py     # 工具单元测试
│   └── test_render_map.py # 渲染测试
├── .github/workflows/ci.yml  # CI：push/PR 时自动跑测试
├── AI_LOG.md             # AI 使用日志
├── ATTRIBUTION.md        # 拿来说明（借鉴来源）
├── CONTRIBUTING.md       # 贡献指南
└── LICENSE               # MIT
```

## 🧠 工作原理

1. **指令**：用户输入一句自然语言指令
2. **决策**：Gemma 4 判断需要调用哪个工具（`add_marker` / `get_distance` / `finalize_map`）
3. **执行**：Agent 执行工具并把结果回传给模型
4. **迭代**：模型继续决策，直到调用 `finalize_map`
5. **渲染**：`render_map.py` 把 marker 列表渲染成 Leaflet 交互式地图

## 📐 工具说明

| 工具 | 作用 | 关键参数 |
|------|------|----------|
| `add_marker` | 添加地点标记 | `name` / `name_zh` / `latitude` / `longitude` / `description` / `category` |
| `get_distance` | 计算两点球面距离（km，haversine） | 两组经纬度 |
| `finalize_map` | 结束流程并触发渲染 | `title` / `summary` |

`category` 枚举：校园建筑 / 宿舍 / 餐饮 / 交通 / 地标 / 休闲。

## 🤝 贡献

欢迎 star、fork、提 Issue 或 PR！详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 📄 License

[MIT](./LICENSE) · 本项目由本地模型 Gemma 4 辅助开发，详见 [AI_LOG.md](./AI_LOG.md) 与 [ATTRIBUTION.md](./ATTRIBUTION.md)。
