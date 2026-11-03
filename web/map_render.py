"""Leaflet 地图 HTML 渲染（供 Flask 后端复用）。"""
import json as _json

SIAS_CENTER = (34.40, 113.73)

_CATEGORY_COLORS = {
    "校园建筑": "#2563eb",
    "宿舍": "#16a34a",
    "餐饮": "#ea580c",
    "交通": "#7c3aed",
    "地标": "#dc2626",
    "休闲": "#0d9488",
}

_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>html,body,#map{height:100%;margin:0}</style></head>
<body><div id="map"></div>
<script>
var map=L.map('map').setView([__LAT__,__LNG__],__ZOOM__);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}).addTo(map);
var markers=__PAYLOAD__;
markers.forEach(function(m){L.marker([m.lat,m.lng]).addTo(map).bindPopup('<b>'+m.name+'</b><br/>'+m.desc+'<br/><span style="color:'+m.color+'">'+m.cat+'</span>');});
</script></body></html>"""


def render_map_html(markers, center=SIAS_CENTER, zoom=15):
    """把 marker 列表渲染成一段独立可运行的 Leaflet HTML 字符串。"""
    lat, lng = center
    items = []
    for m in markers:
        cat = m.get("category", "地标")
        items.append({
            "name": m.get("name_zh") or m.get("name", ""),
            "desc": m.get("description", ""),
            "cat": cat,
            "lat": float(m["latitude"]),
            "lng": float(m["longitude"]),
            "color": _CATEGORY_COLORS.get(cat, "#64748b"),
        })
    payload = _json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    return (_TEMPLATE
            .replace("__LAT__", str(lat))
            .replace("__LNG__", str(lng))
            .replace("__ZOOM__", str(zoom))
            .replace("__PAYLOAD__", payload))
