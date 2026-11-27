# -*- coding: utf-8 -*-
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_REFERENCES = [
    "references/xjtu-search-playbook.md",
    "references/evidence-rules.md",
    "references/result-format.md",
]

REQUIRED_RULES = [
    "信息展示",
    "匹配模式",
    "先确定交互模式",
    "明确满足",
    "明确冲突",
    "未说明",
    "明确有效期",
    "长期接收",
    "曾发布-当前名额待确认",
    "已截止",
    "待核实线索",
    "零个明确匹配",
    "CSV",
    ".docx",
    "同一份结果",
    "20 位候选",
    "校内",
    "企业自行招募",
    "合作项目",
    "来源",
    "核查日期",
    "scripts/export_results.py",
]

REQUIRED_REFERENCE_CONTENT = {
    "references/xjtu-search-playbook.md": [
        "gr.xjtu.edu.cn",
        "units_teacherlist.jsp",
        "collegeId=1025",
        "1151",
        "1176",
        "我的新闻",
        "招生信息",
        "getsitelistcontent.jsp",
        "cs.xjtu.edu.cn",
    ],
    "references/evidence-rules.md": [
        "E1",
        "E2",
        "E3",
        "原句",
        "直达页面",
        "发布日期",
        "核查日期",
        "明确满足",
        "明确冲突",
        "未说明",
        "长期接收",
        "曾发布-当前名额待确认",
        "已截止",
        "未找到本科生招募信息",
        "归属",
        "转载",
        "冲突",
    ],
    "references/result-format.md": [
        "信息展示模式",
        "匹配模式",
        "待确认",
        "覆盖",
        "name",
        "college",
        "direction",
        "undergrad_statement",
        "conditions",
        "recency",
        "unknowns",
        "sources",
        "group",
        "meets",
        "conflicts",
        "unknown",
        "posted_quota_tbd",
        "none_found",
        "utf-8-sig",
    ],
}


class SkillContractTest(unittest.TestCase):
    def test_skill_frontmatter_and_references_exist(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
        self.assertIn("name: xjtu-research-opportunities", text)
        self.assertIn("description:", text)
        for rel in REQUIRED_REFERENCES:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_skill_states_the_mvp_scope(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in [
            "西安交通大学本科生",
            "本校科研实习",
            "跨校",
            "企业自行招募",
            "合作方",
            "实际工作地点",
            "无法核实",
        ]:
            self.assertIn(phrase, text)

    def test_skill_contains_operating_rules(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        missing = [phrase for phrase in REQUIRED_RULES if phrase not in text]
        self.assertEqual([], missing, f"SKILL.md missing: {missing}")

    def test_skill_describes_modes_and_delivery(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in [
            "先确定交互模式",
            "先让用户选择",
            "跳过",
            "中性排列",
            "匹配分数",
            "逐项比较",
            "同一份结果",
            "零个明确匹配",
            "已确认资格",
        ]:
            self.assertIn(phrase, text)

    def test_skill_forbids_unverified_claims(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in [
            "不得",
            "伪造",
            "搜索摘要",
            "过期公告",
            "当前名额",
            "待核实线索",
        ]:
            self.assertIn(phrase, text)

    def test_references_cover_required_content(self):
        for rel, phrases in REQUIRED_REFERENCE_CONTENT.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            missing = [phrase for phrase in phrases if phrase not in text]
            self.assertEqual([], missing, f"{rel} missing: {missing}")

    def test_readme_mentions_install_call_and_tests(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in [
            "xjtu-research-opportunities",
            "SKILL.md",
            "python -m unittest discover -s tests -v",
            "scripts/export_results.py",
            "已知限制",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
