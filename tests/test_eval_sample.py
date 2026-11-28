# -*- coding: utf-8 -*-
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED_AT = "2026-11-27"
ALLOWED = {
    "direction": {"stated", "not_stated"},
    "undergrad": {"accepted", "not_stated", "conflict"},
    "grade": {"stated", "not_stated", "conflict"},
    "school": {"stated", "not_stated", "conflict"},
    "time": {"stated", "not_stated", "conflict"},
    "recency": {
        "deadline_open",
        "long_term",
        "posted_quota_tbd",
        "deadline_expired",
        "none_found",
    },
}
FIELDS = ["direction", "undergrad", "grade", "school", "time", "recency"]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class EvalSampleTest(unittest.TestCase):
    def setUp(self):
        self.data = load("eval/faculty-sample.json")
        self.teachers = self.data["teachers"]

    def test_sample_has_20_unique_teachers(self):
        self.assertEqual(20, len(self.teachers))
        self.assertEqual(20, len({t["name"] for t in self.teachers}))
        self.assertEqual(20, len({t["homepage"] for t in self.teachers}))
        for index, teacher in enumerate(self.teachers, 1):
            self.assertEqual(index, teacher["order"])
            self.assertTrue(teacher["homepage"].startswith("https://gr.xjtu.edu.cn/"))
            self.assertEqual(CHECKED_AT, teacher["checked_at"])
            self.assertGreaterEqual(len(teacher["checked_pages"]), 2)
            self.assertIn(teacher["homepage"], teacher["checked_pages"])
            if teacher["name"] == "桂小林":
                # 桂小林主页没有“我的新闻”入口，用“科研方向介绍”页补足第二页。
                self.assertTrue(
                    any("zdylm" in page for page in teacher["checked_pages"]),
                    "桂小林 should include the research-direction page",
                )
            else:
                self.assertTrue(
                    any("article" in page for page in teacher["checked_pages"]),
                    f"{teacher['name']} should include a 我的新闻 page",
                )
            for field in FIELDS:
                self.assertIn(teacher[field]["status"], ALLOWED[field], (teacher["name"], field))

    def test_sample_has_status_diversity(self):
        accepted = [t for t in self.teachers if t["undergrad"]["status"] == "accepted"]
        self.assertGreaterEqual(len(accepted), 2)
        self.assertTrue(any(t["recency"]["status"] == "long_term" for t in self.teachers))
        self.assertTrue(any(t["recency"]["status"] == "posted_quota_tbd" for t in self.teachers))
        none_found = [t for t in self.teachers if t["recency"]["status"] == "none_found"]
        self.assertGreaterEqual(len(none_found), 10)

    def test_positive_claims_have_quotes_and_sources(self):
        for teacher in self.teachers:
            for field in FIELDS:
                entry = teacher[field]
                if entry["status"] in ("not_stated", "none_found"):
                    self.assertIsNone(entry.get("quote"), (teacher["name"], field))
                    self.assertIsNone(entry.get("source"), (teacher["name"], field))
                    continue
                self.assertTrue(entry.get("quote"), (teacher["name"], field))
                self.assertTrue(entry.get("source"), (teacher["name"], field))
                self.assertTrue(
                    str(entry["source"]).startswith("https://gr.xjtu.edu.cn/"),
                    (teacher["name"], field),
                )

    def test_accepted_entries_are_about_undergraduates(self):
        for teacher in self.teachers:
            entry = teacher["undergrad"]
            if entry["status"] == "accepted":
                self.assertIn("本科", entry["quote"], teacher["name"])

    def test_recency_quotes_match_their_category(self):
        for teacher in self.teachers:
            entry = teacher["recency"]
            if entry["status"] == "long_term":
                self.assertTrue(
                    any(word in entry["quote"] for word in ("长期", "常年")),
                    teacher["name"],
                )
            if entry["status"] == "posted_quota_tbd":
                self.assertIn("本科", entry["quote"], teacher["name"])

    def test_roster_matches_faculty_sample(self):
        roster = load("eval/sample-teachers.json")
        self.assertIn("selection", roster)
        self.assertIn("units_teacherlist.jsp", roster["selection"]["directory_url"])
        self.assertEqual("1025", roster["selection"]["college_id"])
        self.assertEqual(CHECKED_AT, roster["selection"]["selected_at"])
        self.assertEqual(
            [t["name"] for t in self.teachers],
            [t["name"] for t in roster["teachers"]],
        )

    def test_development_cases_cover_required_evidence(self):
        text = (ROOT / "eval/development-cases.md").read_text(encoding="utf-8")
        for phrase in [
            "张妮",
            "曹建福",
            "刘龙军",
            "大二、大三",
            "8-10 小时",
            "常年招收",
            "合作项目",
            "企业自行招募",
            "归属不明",
            "待核实线索",
        ]:
            self.assertIn(phrase, text)

    def test_eval_readme_documents_sample_limits(self):
        text = (ROOT / "eval/README.md").read_text(encoding="utf-8")
        for phrase in ["选样规则", "核查日期", "只描述本轮覆盖", "不用于对外宣传"]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
