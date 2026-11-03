# -*- coding: utf-8 -*-
"""test_tools.py —— 工具集单元测试。"""
from __future__ import annotations
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tools import _haversine, execute_tool  # noqa: E402


class TestHaversine(unittest.TestCase):
    def test_same_point_is_zero(self):
        self.assertAlmostEqual(_haversine(34.4, 113.73, 34.4, 113.73), 0.0, places=6)

    def test_known_latitude_degree(self):
        # 1° 纬度 ≈ 111.19 km（同一经度）
        d = _haversine(34.0, 113.73, 35.0, 113.73)
        self.assertAlmostEqual(d, 111.19, delta=0.5)

    def test_symmetric(self):
        d1 = _haversine(34.4, 113.7, 34.5, 113.8)
        d2 = _haversine(34.5, 113.8, 34.4, 113.7)
        self.assertAlmostEqual(d1, d2, places=9)


class TestExecuteTool(unittest.TestCase):
    def test_add_marker_appends_state(self):
        state = {}
        out = execute_tool(
            "add_marker",
            {"name": "Main Gate", "name_zh": "主校门", "latitude": 34.40,
             "longitude": 113.73, "description": "校园主入口", "category": "交通"},
            state,
        )
        self.assertEqual(len(state["markers"]), 1)
        self.assertEqual(state["markers"][0]["name_zh"], "主校门")
        self.assertIn("主校门", out)

    def test_add_marker_default_category(self):
        state = {}
        execute_tool(
            "add_marker",
            {"name": "A", "name_zh": "甲", "latitude": 34.4,
             "longitude": 113.7, "description": "x"},
            state,
        )
        self.assertEqual(state["markers"][0]["category"], "地标")

    def test_get_distance_returns_km(self):
        state = {}
        out = execute_tool(
            "get_distance", {"lat1": 34.0, "lng1": 113.73, "lat2": 34.0, "lng2": 114.73}, state
        )
        self.assertIn("km", out)

    def test_finalize_sets_state(self):
        state = {"markers": []}
        execute_tool("add_marker", {"name": "A", "name_zh": "甲", "latitude": 34.4,
                                    "longitude": 113.7, "description": "x"}, state)
        out = execute_tool("finalize_map", {"title": "T", "summary": "s"}, state)
        self.assertTrue(state["finalized"])
        self.assertEqual(state["title"], "T")
        self.assertIn("1", out)

    def test_unknown_tool_raises(self):
        with self.assertRaises(ValueError):
            execute_tool("nope", {}, {})


if __name__ == "__main__":
    unittest.main()
