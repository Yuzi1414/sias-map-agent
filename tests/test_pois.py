"""C9 升级 MVP 验收测试：离线 POI 知识库完整性（无需 Ollama / 纯标准库可复跑）。

运行： python tests/test_pois.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POIS_PATH = os.path.join(ROOT, "web", "static", "pois.json")

BBOX = {"min_lat": 34.39, "max_lat": 34.41, "min_lng": 113.72, "max_lng": 113.74}
CATEGORIES = ["校园建筑", "宿舍", "餐饮", "交通", "地标", "休闲"]


class TestPois(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(POIS_PATH, encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.pois = cls.data["pois"]

    def test_schema(self):
        self.assertIn("pois", self.data)
        self.assertIn("center", self.data)
        self.assertIn("bbox", self.data)
        self.assertTrue(self.pois, "POI 列表不能为空")

    def test_required_fields(self):
        for p in self.pois:
            for k in ("id", "name", "category", "lat", "lng", "desc", "aliases"):
                self.assertIn(k, p, "%s 缺字段 %s" % (p.get("name"), k))

    def test_unique_id_and_name(self):
        ids = [p["id"] for p in self.pois]
        names = [p["name"] for p in self.pois]
        self.assertEqual(len(ids), len(set(ids)), "id 必须唯一")
        self.assertEqual(len(names), len(set(names)), "name 必须唯一")

    def test_category_valid(self):
        for p in self.pois:
            self.assertIn(p["category"], CATEGORIES, "%s 类别非法" % p["name"])

    def test_coords_in_bbox(self):
        for p in self.pois:
            self.assertGreaterEqual(p["lat"], BBOX["min_lat"], "%s lat 越界" % p["name"])
            self.assertLessEqual(p["lat"], BBOX["max_lat"], "%s lat 越界" % p["name"])
            self.assertGreaterEqual(p["lng"], BBOX["min_lng"], "%s lng 越界" % p["name"])
            self.assertLessEqual(p["lng"], BBOX["max_lng"], "%s lng 越界" % p["name"])

    def test_min_coverage(self):
        cats = {p["category"] for p in self.pois}
        self.assertEqual(cats, set(CATEGORIES), "必须覆盖全部 6 个类别")
        self.assertGreaterEqual(len(self.pois), 30, "POI 数量应 ≥30")


if __name__ == "__main__":
    unittest.main(verbosity=2)
