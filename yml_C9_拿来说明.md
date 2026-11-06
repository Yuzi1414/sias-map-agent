# C9 拿来说明（Attribution）

> 本仓库 SIAS Map Agent 在 C9 阶段使用的外部资源与来源说明。

## 直接沿用（自有资产）
- C6 版 SIAS Map Agent 代码（本仓库 `src/`、`web/`），为本人 C6 挑战产出，C9 在此基础上迭代。

## 模型与运行时
- **Ollama**（本地 LLM 运行时）：https://ollama.com
- **Gemma 模型**（默认 `gemma4:e4b`）：Google Gemma 系列，本地推理用。

## 数据与命名
- 校内 POI 标准命名（图书馆、第一食堂、西亚斯钟楼等）：参考郑州西亚斯学院公开校园信息与通用叫法。
- POI 结构化字段设计（name/category/lat/lng/aliases）：参考通用地图 POI 通用做法，非直接复制任何一家数据。
- 坐标为本校校园内近似/示例点位，仅用于离线演示与距离估算，非实测测绘数据（已在 `pois.json` note 与气泡文案中注明）。

## 思路参考
- OpenStreetMap / Overture Maps 的开放数据与标注理念（未直接使用其数据）。
- 挑战 C9 正文「九、联动」关于 C6→C9 同一项目延续的说明。

## 声明
除上述自产与开源运行时外，未复制任何第三方地图数据或代码；`pois.json` 全部条目由本人撰写。
