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
    renderMap(data.map_html);
  } catch (err) {
    loading.remove();
    addBubble("请求失败：" + err, "bot");
  }
});

refreshStatus();
addBubble("你好！告诉我你想找什么，比如「学校附近有哪些好吃的」或「图书馆怎么走」。", "bot");
