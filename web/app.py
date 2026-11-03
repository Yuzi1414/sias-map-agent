"""
SIAS Map Agent — Web Application
自然语言驱动郑州西亚斯学院周边交互式地图（网页版）

本地运行:
    pip install -r requirements.txt
    python app.py          # 打开 http://localhost:8000

环境变量:
    OLLAMA_BASE   本地 Ollama 地址（默认 http://localhost:11434）
    MODEL         模型名（默认 gemma4:e4b）
"""
import json
import math
import os

from flask import Flask, jsonify, request, send_from_directory

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    requests = None
    HAS_REQUESTS = False

from map_render import render_map_html, SIAS_CENTER

R_EARTH_KM = 6371.0
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_ENDPOINT = os.environ.get("OLLAMA_ENDPOINT", OLLAMA_BASE.rstrip("/") + "/v1/chat/completions")
MODEL = os.environ.get("MODEL", "gemma4:e4b")
MAX_STEPS = 40
CATEGORIES = ["校园建筑", "宿舍", "餐饮", "交通", "地标", "休闲"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__)

SYSTEM_PROMPT = (
    "你是西亚斯地图助手。用户用自然语言询问郑州西亚斯学院周边地点。"
    "你必须通过工具调用 add_marker 在地图上标注至少 5 个相关地点，"
    "需要时调用 get_distance 计算距离，最后调用 finalize_map 给出中文总结。"
    "地点类别只能从以下选择：" + "、".join(CATEGORIES) + "。"
    "经纬度须在郑州西亚斯学院附近（约 34.39~34.41, 113.72~113.74），"
    "基于常识给出一致、合理的坐标。"
)

TOOLS = [
    {"type": "function", "function": {
        "name": "add_marker",
        "description": "在地图上添加一个地点标记",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string", "description": "英文标识"},
            "name_zh": {"type": "string", "description": "中文名称"},
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "description": {"type": "string"},
            "category": {"type": "string", "enum": CATEGORIES},
        }, "required": ["name", "name_zh", "latitude", "longitude", "description", "category"]}},
    },
    {"type": "function", "function": {
        "name": "get_distance",
        "description": "计算两个经纬度点间距离（公里）",
        "parameters": {"type": "object", "properties": {
            "lat1": {"type": "number"}, "lon1": {"type": "number"},
            "lat2": {"type": "number"}, "lon2": {"type": "number"},
        }, "required": ["lat1", "lon1", "lat2", "lon2"]}},
    },
    {"type": "function", "function": {
        "name": "finalize_map",
        "description": "结束标注并返回中文总结",
        "parameters": {"type": "object", "properties": {
            "summary": {"type": "string"},
        }, "required": ["summary"]}},
    },
]


def _m(name_zh, lat, lng, desc, cat):
    return {"name": name_zh, "name_zh": name_zh, "latitude": lat,
            "longitude": lng, "description": desc, "category": cat}


# 演示模式兜底数据（未连接本地模型时用于体验核心流程）
DEMO = {
    "overview": [
        _m("西亚斯学院", 34.4000, 113.7300, "郑州西亚斯学院主校区", "校园建筑"),
        _m("图书馆", 34.4012, 113.7310, "主图书馆/自习", "校园建筑"),
        _m("第一食堂", 34.3988, 113.7285, "学生食堂", "餐饮"),
        _m("第二食堂", 34.3995, 113.7320, "学生食堂", "餐饮"),
        _m("学生宿舍A区", 34.3978, 113.7280, "宿舍区", "宿舍"),
        _m("东门", 34.3992, 113.7335, "校门/出入口", "交通"),
        _m("南门", 34.3970, 113.7295, "校门/出入口", "交通"),
        _m("校园咖啡", 34.4005, 113.7338, "东门外咖啡馆", "休闲"),
    ],
    "dining": [
        _m("第一食堂", 34.3988, 113.7285, "学生食堂", "餐饮"),
        _m("第二食堂", 34.3995, 113.7320, "学生食堂", "餐饮"),
        _m("校园咖啡", 34.4005, 113.7338, "东门外咖啡馆", "休闲"),
        _m("奶茶店", 34.4002, 113.7336, "东门外饮品", "餐饮"),
        _m("小吃街", 34.3998, 113.7340, "东门夜市小吃", "餐饮"),
        _m("清真食堂", 34.3990, 113.7305, "校内清真窗口", "餐饮"),
    ],
    "study": [
        _m("图书馆", 34.4012, 113.7310, "主图书馆/自习", "校园建筑"),
        _m("教学楼A", 34.4008, 113.7290, "教学/自习", "校园建筑"),
        _m("自习室", 34.4010, 113.7300, "24小时自习室", "校园建筑"),
        _m("校园咖啡", 34.4005, 113.7338, "东门外咖啡馆（可自习）", "休闲"),
        _m("学生活动中心", 34.4000, 113.7315, "活动/研讨", "校园建筑"),
    ],
    "transit": [
        _m("东门", 34.3992, 113.7335, "校门/出入口", "交通"),
        _m("南门", 34.3970, 113.7295, "校门/出入口", "交通"),
        _m("东门公交站", 34.3990, 113.7342, "公交站点", "交通"),
        _m("南门公交站", 34.3968, 113.7298, "公交站点", "交通"),
        _m("停车场", 34.3994, 113.7328, "校内停车场", "交通"),
    ],
}


def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH_KM * math.asin(math.sqrt(a))


def execute_tool(name, args, markers):
    if name == "add_marker":
        if not all(k in args for k in ("name", "latitude", "longitude")):
            return {"ok": False, "error": "add_marker 缺少必填参数"}
        cat = args.get("category", "地标")
        if cat not in CATEGORIES:
            cat = "地标"
        markers.append({
            "name": args["name"],
            "name_zh": args.get("name_zh") or args["name"],
            "latitude": float(args["latitude"]),
            "longitude": float(args["longitude"]),
            "description": args.get("description", ""),
            "category": cat,
        })
        return {"ok": True, "count": len(markers)}
    if name == "get_distance":
        try:
            d = haversine(float(args["lat1"]), float(args["lon1"]),
                          float(args["lat2"]), float(args["lon2"]))
            return {"distance_km": round(d, 3)}
        except Exception:
            return {"ok": False, "error": "get_distance 参数错误"}
    if name == "finalize_map":
        return {"ok": True, "summary": args.get("summary", "")}
    return {"ok": False, "error": "未知工具 " + name}


def ollama_available():
    if not HAS_REQUESTS:
        return False
    try:
        r = requests.get(OLLAMA_BASE.rstrip("/") + "/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def demo_reply(message):
    text = message or ""
    if any(k in text for k in ("吃", "饭", "食", "餐", "咖啡", "奶茶", "外卖")):
        ms, reply = DEMO["dining"], "学校餐饮集中在第一/第二食堂与东门外商业街，另有一家咖啡馆和清真窗口。"
    elif any(k in text for k in ("图书", "自习", "学习", "书")):
        ms, reply = DEMO["study"], "自习推荐图书馆与24小时自习室，东门外咖啡馆也可带电脑自习。"
    elif any(k in text for k in ("公交", "地铁", "打车", "停车", "交通", "车", "门")):
        ms, reply = DEMO["transit"], "东门、南门是主要出入口，两处门外均有公交站，校内设停车场。"
    else:
        ms, reply = DEMO["overview"], "这是西亚斯学院及周边的核心地点概览，可继续问我更具体的需求。"
    return {
        "mode": "demo",
        "reply": reply + "（演示模式：未连接本地模型，坐标为示例数据）",
        "markers": ms,
        "map_html": render_map_html(ms),
    }


def _chat_stream(messages):
    """调用 Ollama（流式），返回 (content, 有序 tool_calls 列表)。"""
    payload = {"model": MODEL, "messages": messages, "tools": TOOLS,
               "stream": True, "temperature": 0.2, "max_tokens": 1024}
    content = ""
    calls = {}
    with requests.post(OLLAMA_ENDPOINT, json=payload, stream=True,
                       timeout=(10, 300)) as resp:
        resp.raise_for_status()
        for raw in resp.iter_lines():
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace")
            line = line[6:] if line.startswith("data: ") else line
            if line.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(line)
            except Exception:
                continue
            for choice in chunk.get("choices") or []:
                delta = choice.get("delta") or {}
                if delta.get("content"):
                    content += delta["content"]
                for tc in delta.get("tool_calls") or []:
                    idx = tc.get("index", 0)
                    e = calls.setdefault(idx, {"id": "", "name": "", "args": ""})
                    if tc.get("id"):
                        e["id"] = tc["id"]
                    fn = tc.get("function") or {}
                    if fn.get("name"):
                        e["name"] += fn["name"]
                    if fn.get("arguments"):
                        e["args"] += fn["arguments"]
    return content, [calls[i] for i in sorted(calls)]


def run_agent(message):
    if not ollama_available():
        return demo_reply(message)
    markers, summary = [], ""
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}]
    try:
        for _ in range(MAX_STEPS):
            content, calls = _chat_stream(messages)
            if not calls:
                if content:
                    summary = content
                break
            messages.append({"role": "assistant", "content": content or None,
                             "tool_calls": [
                                 {"id": c["id"], "type": "function",
                                  "function": {"name": c["name"], "arguments": c["args"]}}
                                 for c in calls]})
            for c in calls:
                try:
                    args = json.loads(c["args"] or "{}")
                except Exception:
                    args = {}
                result = execute_tool(c["name"], args, markers)
                messages.append({"role": "tool", "tool_call_id": c["id"],
                                 "content": json.dumps(result, ensure_ascii=False)})
                if c["name"] == "finalize_map":
                    summary = args.get("summary") or result.get("summary", "")
                    break
            if summary:
                break
    except Exception as e:
        d = demo_reply(message)
        d["reply"] = "（本地模型暂时响应超时，已切换演示模式）" + d["reply"]
        return d
    if not summary:
        summary = "已为你在地图上标注 %d 个地点。" % len(markers)
    return {"mode": "live", "reply": summary, "markers": markers,
            "map_html": render_map_html(markers) if markers else ""}


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(STATIC_DIR, "style.css")


@app.route("/app.js")
def js():
    return send_from_directory(STATIC_DIR, "app.js")


@app.route("/api/status")
def status():
    return jsonify({"live_ai": ollama_available(), "model": MODEL})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "empty message"}), 400
    return jsonify(run_agent(message))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
