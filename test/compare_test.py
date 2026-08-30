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

    def test_list_length_and_values(self):
        diffs = compare_data([1, 2], [1, 3, 4], print_diff=False)
        self.assertIn("[长度变化] <root>: 长度 2 -> 3", diffs)
        self.assertIn("[值变化] [1]: 2 -> 3", diffs)
        self.assertIn("[新增元素] [2] = 4", diffs)

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
