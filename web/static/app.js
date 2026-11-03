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

// ---- 客户端演示模式数据（后端不可达时的兜底，与 app.py 的 DEMO 对齐）----
const CAT_COLORS = {
  "校园建筑": "#2563eb", "宿舍": "#16a34a", "餐饮": "#ea580c",
  "交通": "#7c3aed", "地标": "#dc2626", "休闲": "#0d9488",
};
function M(name, lat, lng, desc, cat) {
  return { name: name, lat: lat, lng: lng, desc: desc, cat: cat };
}
const DEMO = {
  overview: [
    M("西亚斯学院", 34.4000, 113.7300, "郑州西亚斯学院主校区", "校园建筑"),
    M("图书馆", 34.4012, 113.7310, "主图书馆/自习", "校园建筑"),
    M("第一食堂", 34.3988, 113.7285, "学生食堂", "餐饮"),
    M("第二食堂", 34.3995, 113.7320, "学生食堂", "餐饮"),
    M("学生宿舍A区", 34.3978, 113.7280, "宿舍区", "宿舍"),
    M("东门", 34.3992, 113.7335, "校门/出入口", "交通"),
    M("南门", 34.3970, 113.7295, "校门/出入口", "交通"),
    M("校园咖啡", 34.4005, 113.7338, "东门外咖啡馆", "休闲"),
  ],
  dining: [
    M("第一食堂", 34.3988, 113.7285, "学生食堂", "餐饮"),
    M("第二食堂", 34.3995, 113.7320, "学生食堂", "餐饮"),
    M("校园咖啡", 34.4005, 113.7338, "东门外咖啡馆", "休闲"),
    M("奶茶店", 34.4002, 113.7336, "东门外饮品", "餐饮"),
    M("小吃街", 34.3998, 113.7340, "东门夜市小吃", "餐饮"),
    M("清真食堂", 34.3990, 113.7305, "校内清真窗口", "餐饮"),
  ],
  study: [
    M("图书馆", 34.4012, 113.7310, "主图书馆/自习", "校园建筑"),
    M("教学楼A", 34.4008, 113.7290, "教学/自习", "校园建筑"),
    M("自习室", 34.4010, 113.7300, "24小时自习室", "校园建筑"),
    M("校园咖啡", 34.4005, 113.7338, "东门外咖啡馆（可自习）", "休闲"),
    M("学生活动中心", 34.4000, 113.7315, "活动/研讨", "校园建筑"),
  ],
  transit: [
    M("东门", 34.3992, 113.7335, "校门/出入口", "交通"),
    M("南门", 34.3970, 113.7295, "校门/出入口", "交通"),
    M("东门公交站", 34.3990, 113.7342, "公交站点", "交通"),
    M("南门公交站", 34.3968, 113.7298, "公交站点", "交通"),
    M("停车场", 34.3994, 113.7328, "校内停车场", "交通"),
  ],
};

function demoReply(message) {
  const text = message || "";
  if (/吃|饭|食|餐|咖啡|奶茶|外卖/.test(text)) {
    return { reply: "学校餐饮集中在第一/第二食堂与东门外商业街，另有一家咖啡馆和清真窗口。", markers: DEMO.dining };
  }
  if (/图书|自习|学习|书/.test(text)) {
    return { reply: "自习推荐图书馆与24小时自习室，东门外咖啡馆也可带电脑自习。", markers: DEMO.study };
  }
  if (/公交|地铁|打车|停车|交通|车|门/.test(text)) {
    return { reply: "东门、南门是主要出入口，两处门外均有公交站，校内设停车场。", markers: DEMO.transit };
  }
  return { reply: "这是西亚斯学院及周边的核心地点概览，可继续问我更具体的需求。", markers: DEMO.overview };
}

function renderMarkers(markers) {
  if (!markers || !markers.length) return;
  const items = markers.map((m) => ({
    name: m.name, desc: m.desc, cat: m.cat,
    lat: m.lat, lng: m.lng,
    color: CAT_COLORS[m.cat] || "#64748b",
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
    badge.textContent = s.live_ai ? "AI 已连接（本地模型）" : "演示模式（未连接本地模型）";
    badge.className = "badge " + (s.live_ai ? "live" : "demo");
  } catch (e) {
    badge.textContent = "演示模式";
    badge.className = "badge demo";
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
    // 后端不可达 → 客户端演示模式兜底
    loading.remove();
    const d = demoReply(text);
    addBubble(d.reply + "（演示模式：未连接后端，坐标为示例数据）", "bot");
    renderMarkers(d.markers);
  }
});

refreshStatus();
addBubble("你好！告诉我你想找什么，比如「学校附近有哪些好吃的」或「图书馆怎么走」。", "bot");
