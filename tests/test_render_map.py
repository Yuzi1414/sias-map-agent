# -*- coding: utf-8 -*-
"""test_render_map.py —— 地图渲染测试。"""
from __future__ import annotations
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from render_map import render_map  # noqa: E402


class TestRenderMap(unittest.TestCase):
    def test_render_writes_html(self):
        markers = [{"name": "Main Gate", "name_zh": "主校门", "lat": 34.40,
                    "lng": 113.73, "description": "校园主入口", "category": "交通"}]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "m.html")
            out = render_map(markers, "标题", p)
            self.assertEqual(out, p)
            with open(p, encoding="utf-8") as f:
                html = f.read()
            self.assertIn("leaflet", html.lower())
            self.assertIn("主校门", html)

    def test_script_tag_escaped(self):
        markers = [{"name": "x", "name_zh": "y", "lat": 34.4, "lng": 113.7,
                    "description": "a</script><script>alert(1)</script>", "category": "地标"}]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "m.html")
            render_map(markers, "标题", p)
            with open(p, encoding="utf-8") as f:
                html = f.read()
            self.assertNotIn("</script><script>", html)

    def test_empty_markers_fallback_center(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "m.html")
            render_map([], "标题", p)
            with open(p, encoding="utf-8") as f:
                html = f.read()
            self.assertIn("34.4", html)
            self.assertIn("113.73", html)


if __name__ == "__main__":
    unittest.main()
