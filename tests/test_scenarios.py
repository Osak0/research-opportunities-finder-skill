# -*- coding: utf-8 -*-
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "eval/scenarios.md"


class ScenarioTest(unittest.TestCase):
    def setUp(self):
        self.text = SCENARIOS.read_text(encoding="utf-8")
        self.sections = {
            match.group(1): match.group(2)
            for match in re.finditer(r"^## (S\d+) · .*?\n(.*?)(?=^## S\d+ · |\Z)", self.text, re.S | re.M)
        }

    def test_scenarios_cover_s1_to_s20(self):
        required = [f"S{i}" for i in range(1, 21)]
        self.assertEqual(required, sorted(self.sections, key=lambda s: int(s[1:])))
        for sid in required:
            self.assertIn(f"## {sid}", self.text)

    def test_each_scenario_has_input_mode_behaviour_and_forbidden(self):
        for sid, body in self.sections.items():
            for label in ["学生输入", "预期模式", "预期行为", "不得出现"]:
                self.assertIn(label, body, f"{sid} missing {label}")

    def test_scenarios_cover_required_risk_phrases(self):
        for phrase in [
            "模式不明",
            "追加条件",
            "限定候选",
            "零个明确匹配",
            "过期公告",
            "页面打不开",
            "只换格式",
            "跨校",
            "企业岗位",
            "合作项目",
            "归属不明",
            "查全有限目录",
        ]:
            self.assertIn(phrase, self.text)

    def test_scenarios_require_evidence_and_coverage_language(self):
        for phrase in ["原句", "核查日期", "时效", "覆盖", "待核实线索"]:
            self.assertIn(phrase, self.text)

    def test_scenarios_do_not_promise_unsupported_scope(self):
        for phrase in ["不承诺跨校", "不遍历全目录", "不伪造", "不把旧公告当当前名额"]:
            self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
