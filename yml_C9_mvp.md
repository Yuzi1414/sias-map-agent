# C9 MVP —— SIAS Map Agent 数据化与离线问答（第 1 周）

> 实物位置：本仓库 `web/static/pois.json`、`web/static/app.js`、`web/app.py`、`tests/test_pois.py`
> 在线地址：https://yuzi1414.github.io/sias-map-agent/

## 这周做出来的实物是什么
把 C6 的 SIAS Map Agent 从"连不上本地后端就显示『连接中…』的静态壳"，改造成**打开网页就能离线问路**的版本：

1. **校园知识库 `web/static/pois.json`**
   - 34 个校内点位，6 大类别：校园建筑(7)、宿舍(4)、餐饮(6)、交通(7)、地标(4)、休闲(6)。
   - 每个点含 `id / name / category / lat / lng / desc / aliases`，`aliases` 支持口语别名（如"一食堂""钟楼""打球"）。

2. **离线问答 `web/static/app.js`**
   - `loadPois()` 加载知识库；`matchPois()` 用别名匹配理解问法；`haversine()` 算直线距离；`kbReply()` 兜底回复。
   - 距离类问法（含"到/离/距/多远/距离"且命中 ≥2 点）→ 输出直线距离 + 估算步行时间。
   - 后端不可达时气泡标注「（离线知识库模式：坐标为示例数据）」，不误导用户。

3. **意图分类 `CAT_KEYWORDS`**：替代 C6 版硬编码 DEMO 的关键词正则。

4. **服务端路由**：`web/app.py` 新增 `/pois.json`，本地 Flask 运行知识库可正常加载。

5. **测试 `tests/test_pois.py`**：6 项用例全部通过（纯标准库 unittest，`python tests/test_pois.py` 复跑）。

## 怎么验证它是"真的"
```
python tests/test_pois.py   # → Ran 6 tests ... OK
python web/app.py           # → 浏览器打开 http://localhost:8000 可离线问答
```

## 与 C6 的关系（为什么这不是"改个名重交"）
C6 交的是"能跑的后端 + 静态壳"，**没有数据、离线不可用、没有测试**。本周新增的是：一份可维护的数据资产、一个离线可用的问答入口、一套能防回归的测试——这三样是 C6 版完全没有、且后续 8 周迭代的地基。

## 下一周计划
部署到 GitHub Pages 并可公开访问 → 找 3 名同学试用 → 收集反馈进入 V1。
