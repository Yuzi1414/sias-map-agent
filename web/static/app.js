const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const messages = document.getElementById("messages");
const frame = document.getElementById("map-frame");
const badge = document.getElementById("mode-badge");

function addBubble(text, who) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

// ---- 离线知识库（C9 升级：数据驱动，替代原 4 组硬编码 DEMO）----
const CAT_COLORS = {
  "校园建筑": "#2563eb", "宿舍": "#16a34a", "餐饮": "#ea580c",
  "交通": "#7c3aed", "地标": "#dc2626", "休闲": "#0d9488",
};

// 意图关键词 → 类别（贴近真实问法）
const CAT_KEYWORDS = {
  "餐饮": ["吃", "饭", "食", "餐", "咖啡", "奶茶", "外卖", "食堂", "美食", "小吃", "喝的"],
  "校园建筑": ["图书", "自习", "学习", "书", "教室", "教学", "上课", "楼", "借"],
  "交通": ["公交", "地铁", "打车", "停车", "车", "门", "站", "怎么走", "多远", "距离", "离"],
  "休闲": ["篮球", "足球", "游泳", "健身", "运动", "跑", "玩"],
  "地标": ["钟楼", "广场", "草坪", "湖", "景观", "亭", "地标"],
  "宿舍": ["宿舍", "住宿", "公寓"],
};

let POIS = [];
let KB_LOADED = false;

async function loadPois() {
  try {
    const r = await fetch("pois.json", { cache: "no-store" });
    const data = await r.json();
    POIS = data.pois || [];
    KB_LOADED = POIS.length > 0;
  } catch (e) {
    KB_LOADED = false;
  }
}

// 球面距离（米），Haversine
function haversine(lat1, lng1, lat2, lng2) {
  const R = 6371000;
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
}

// 按名称/别名匹配 POI（别名越长越优先）
function matchPois(text) {
  const hits = [];
  for (const p of POIS) {
    const terms = [p.name].concat(p.aliases || []);
    let score = 0;
    for (const t of terms) {
      if (t && text.includes(t)) score = Math.max(score, t.length);
    }
    if (score > 0) hits.push({ p: p, score: score });
  }
  hits.sort((a, b) => b.score - a.score);
  return hits.map((h) => h.p);
}

function fmtDist(m) {
  return m >= 1000 ? (m / 1000).toFixed(1) + " 公里" : m + " 米";
}

// 离线知识库问答（后端不可达时的兜底）
function kbReply(message) {
  const text = message || "";
  if (!KB_LOADED) {
    return {
      reply: "离线知识库加载失败，请刷新页面或检查网络。",
      markers: [],
    };
  }

  const hits = matchPois(text);

  // 距离类：命中 ≥2 个地点且带"到/离/距/多远/距离"→ 算直线距离
  if (hits.length >= 2 && /到|离|距|多远|距离/.test(text)) {
    const a = hits[0], b = hits[1];
    const d = haversine(a.lat, a.lng, b.lat, b.lng);
    return {
      reply:
        a.name + " 到 " + b.name + " 的直线距离约 " + fmtDist(d) +
        "，步行约 " + Math.max(1, Math.round(d / 80)) + " 分钟。",
      markers: [a, b],
    };
  }

  if (hits.length) {
    const names = hits.slice(0, 5).map((p) => p.name).join("、");
    return {
      reply:
        "找到相关地点：" + names + "。" +
        "可以继续问「" + hits[0].name + " 到 XX 多远」看距离。",
      markers: hits.slice(0, 8),
    };
  }

  // 意图关键词 → 类别
  for (const cat of Object.keys(CAT_KEYWORDS)) {
    if (CAT_KEYWORDS[cat].some((k) => text.includes(k))) {
      const inCat = POIS.filter((p) => p.category === cat);
      if (inCat.length) {
        const names = inCat.slice(0, 6).map((p) => p.name).join("、");
        return {
          reply: cat + "相关地点：" + names + "。",
          markers: inCat.slice(0, 8),
        };
      }
    }
  }

  return {
    reply: "这是西亚斯学院主要地点概览，可问我「附近有什么好吃的」「图书馆到食堂多远」等。",
    markers: POIS.slice(0, 8),
  };
}

function renderMarkers(markers) {
  if (!markers || !markers.length) return;
  const items = markers.map((m) => ({
    name: m.name, desc: m.desc, cat: m.cat || m.category,
    lat: m.lat, lng: m.lng,
    color: CAT_COLORS[m.cat || m.category] || "#64748b",
  }));
  const payload = JSON.stringify(items).replace(/<\//g, "<\\/");
  const html = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"><\/script>
<style>html,body,#map{height:100%;margin:0}</style></head>
<body><div id="map"></div><script>
var map=L.map('map').setView([34.40,113.73],15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}).addTo(map);
var markers=${payload};
markers.forEach(function(m){L.marker([m.lat,m.lng]).addTo(map).bindPopup('<b>'+m.name+'</b><br/>'+m.desc+'<br/><span style="color:'+m.color+'">'+m.cat+'</span>');});
<\/script></body></html>`;
  frame.srcdoc = html;
}

function renderMap(html) {
  if (html) { frame.srcdoc = html; }
}

async function refreshStatus() {
  try {
    const r = await fetch("/api/status");
    const s = await r.json();
    badge.textContent = s.live_ai ? "AI 已连接（本地模型）" : "离线知识库模式";
    badge.className = "badge " + (s.live_ai ? "live" : "demo");
  } catch (e) {
    badge.textContent = "离线知识库模式";
    badge.className = "badge demo";
    if (KB_LOADED) renderMarkers(POIS.slice(0, 8));
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  addBubble(text, "user");
  const loading = document.createElement("div");
  loading.className = "msg bot loading";
  loading.textContent = "思考中…";
  messages.appendChild(loading);
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await r.json();
    loading.remove();
    addBubble(data.reply || data.error || "无响应", "bot");
    if (data.map_html) renderMap(data.map_html);
    else renderMarkers(data.markers);
  } catch (err) {
    // 后端不可达 → 离线知识库兜底
    loading.remove();
    const d = kbReply(text);
    addBubble(d.reply + "（离线知识库模式：坐标为示例数据）", "bot");
    renderMarkers(d.markers);
  }
});

loadPois().then(() => refreshStatus());
addBubble("你好！告诉我你想找什么，比如「附近有哪些好吃的」「图书馆到第一食堂多远」。", "bot");
