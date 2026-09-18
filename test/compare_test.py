import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import tempfile
import unittest

from bqyx_parser.tools.compare import compare_data, compare_json


class TestCompareData(unittest.TestCase):
    def test_equal_returns_empty(self):
        self.assertEqual(compare_data({"a": 1}, {"a": 1}, print_diff=False), [])

    def test_dict_added_removed_changed(self):
        diffs = compare_data(
            {"keep": 1, "gone": 2, "val": "old"},
            {"keep": 1, "new": 3, "val": "new"},
            print_diff=False,
        )
        self.assertIn("[新增] new = 3", diffs)
        self.assertIn("[删除] gone = 2", diffs)
        self.assertIn("[值变化] val: 'old' -> 'new'", diffs)

    def test_nested_path(self):
        diffs = compare_data(
            {"endless10": {"medelProArr": "specialPartsDropPro"}},
            {"endless10": {"medelProArr": ["specialPartsDropPro"]}},
            print_diff=False,
        )
        self.assertTrue(any("endless10.medelProArr" in line and "类型变化" in line for line in diffs))

    def test_list_ignores_order(self):
        self.assertEqual(compare_data(["def", "abc"], ["abc", "def"], print_diff=False), [])

    def test_list_set_diff(self):
        diffs = compare_data([1, 2], [1, 3, 4], print_diff=False)
        self.assertIn("[删除元素] <root> = 2", diffs)
        self.assertIn("[新增元素] <root> = 3", diffs)
        self.assertIn("[新增元素] <root> = 4", diffs)

    def test_list_of_dicts_by_name_ignores_order(self):
        old = [{"name": "abc", "n": 1}, {"name": "def", "n": 2}]
        new = [{"name": "def", "n": 2}, {"name": "abc", "n": 1}]
        self.assertEqual(compare_data(old, new, print_diff=False), [])

    def test_list_of_dicts_by_name_diff(self):
        diffs = compare_data(
            [{"name": "a", "n": 1}, {"name": "b", "n": 2}],
            [{"name": "b", "n": 3}, {"name": "c", "n": 4}],
            print_diff=False,
        )
        self.assertIn("[删除] a = {'name': 'a', 'n': 1}", diffs)
        self.assertIn("[新增] c = {'name': 'c', 'n': 4}", diffs)
        self.assertIn("[值变化] b.n: 2 -> 3", diffs)

    def test_list_of_dicts_by_lv_diff(self):
        diffs = compare_data(
            [{"lv": 1, "n": 1}, {"lv": 2, "n": 2}],
            [{"lv": 2, "n": 3}, {"lv": 3, "n": 4}],
            print_diff=False,
        )
        self.assertIn("[删除] 1 = {'lv': 1, 'n': 1}", diffs)
        self.assertIn("[新增] 3 = {'lv': 3, 'n': 4}", diffs)
        self.assertIn("[值变化] 2.n: 2 -> 3", diffs)

    def test_list_of_dicts_by_cn_name_diff(self):
        diffs = compare_data(
            [{"cnName": "排名", "proUrl": "rank"}, {"cnName": "积分", "proUrl": "old"}],
            [{"cnName": "积分", "proUrl": "score"}, {"cnName": "用户名", "proUrl": "extraObj.player"}],
            print_diff=False,
        )
        self.assertIn("[删除] 排名 = {'cnName': '排名', 'proUrl': 'rank'}", diffs)
        self.assertIn("[新增] 用户名 = {'cnName': '用户名', 'proUrl': 'extraObj.player'}", diffs)
        self.assertIn("[值变化] 积分.proUrl: 'old' -> 'score'", diffs)

    def test_compare_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_path = Path(tmp) / "old.json"
            new_path = Path(tmp) / "new.json"
            old_path.write_text(json.dumps({"a": 1}), encoding="utf-8")
            new_path.write_text(json.dumps({"a": 2}), encoding="utf-8")
            diffs = compare_json(old_path, new_path, print_diff=False)
            self.assertEqual(diffs, ["[值变化] a: 1 -> 2"])


if __name__ == "__main__":
    unittest.main()
