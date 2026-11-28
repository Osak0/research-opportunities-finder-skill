# -*- coding: utf-8 -*-
import csv
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_results as ex  # noqa: E402

EXAMPLE_URL = "https://gr.xjtu.edu.cn/example/zh_CN/index.htm"


def make_result(name="张三", results=None):
    result = {
        "id": "example",
        "name": name,
        "college": "计算机科学与技术学院",
        "lab": "示例实验室",
        "title": "副教授",
        "direction": "多模态\n大模型",
        "topic": "多模态大模型科研训练",
        "undergrad_statement": "欢迎本科生联系科研训练。",
        "conditions": {
            "direction": {
                "status": "meets",
                "quote": "研究方向包括多模态大模型",
                "source": EXAMPLE_URL,
                "published_at": None,
                "checked_at": "2026-11-27",
            },
            "undergrad": {
                "status": "meets",
                "quote": "欢迎本科生联系科研训练",
                "source": EXAMPLE_URL,
                "published_at": None,
                "checked_at": "2026-11-27",
            },
            "grade": {
                "status": "unknown",
                "quote": None,
                "source": None,
                "published_at": None,
                "checked_at": "2026-11-27",
            },
            "school": {
                "status": "unknown",
                "quote": None,
                "source": None,
                "published_at": None,
                "checked_at": "2026-11-27",
            },
            "time": {
                "status": "unknown",
                "quote": None,
                "source": None,
                "published_at": None,
                "checked_at": "2026-11-27",
            },
        },
        "recency": {
            "status": "posted_quota_tbd",
            "quote": "欢迎本科生联系科研训练",
            "source": EXAMPLE_URL,
            "published_at": None,
            "checked_at": "2026-11-27",
        },
        "unknowns": ["年级要求", "每周投入时间"],
        "sources": [
            {
                "label": "教师主页",
                "url": EXAMPLE_URL,
                "published_at": None,
                "checked_at": "2026-11-27",
            }
        ],
        "group": "confirmed",
        "fit_notes": "方向直接相关。",
        "recommendation": None,
        "notes": "",
    }
    data = {
        "query": {
            "mode": "information",
            "text": "我想找计算机视觉方向的本科生科研实习",
            "conditions": {
                "direction": "计算机视觉",
                "grade": "大二",
                "school": "西安交通大学",
            },
            "coverage": {
                "scope": "计算机学院教师目录前 20 位",
                "discovered": 20,
                "read_in_depth": 20,
                "verified": 2,
                "failed_pages": [],
                "stop_reason": "预算用尽",
                "statement": "本轮覆盖计算机学院教师目录前 20 位；未遍历全目录。",
            },
            "checked_at": "2026-11-27",
        },
        "results": [result] if results is None else results,
    }
    return data


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.csv_path = self.dir / "results.csv"
        self.docx_path = self.dir / "results.docx"

    def tearDown(self):
        self.tmp.cleanup()

    def test_csv_contains_headers_and_escapes(self):
        data = make_result(name="张三, 李四")
        ex.write_csv(data, str(self.csv_path))
        with open(self.csv_path, encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(1, len(rows))
        self.assertEqual("张三, 李四", rows[0]["name"])
        self.assertEqual("多模态\n大模型", rows[0]["direction"])
        self.assertEqual("年级要求；每周投入时间", rows[0]["unknowns"])
        self.assertIn(EXAMPLE_URL, rows[0]["sources"])
        self.assertEqual("信息展示", rows[0]["query_mode"])
        self.assertEqual("", rows[0]["recommendation"])
        self.assertIn("未遍历全目录", rows[0]["coverage_statement"])

    def test_docx_contains_hyperlinks_and_valid_package(self):
        data = make_result()
        ex.write_docx(data, str(self.docx_path))
        with zipfile.ZipFile(self.docx_path) as z:
            names = z.namelist()
            self.assertIn("[Content_Types].xml", names)
            self.assertIn("word/document.xml", names)
            self.assertIn("word/_rels/document.xml.rels", names)
            doc = z.read("word/document.xml").decode("utf-8")
            rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
        self.assertIn("张三", doc)
        self.assertIn("多模态", doc)
        self.assertIn("检索条件：研究方向：计算机视觉", doc)
        self.assertIn("研究方向：明确满足", doc)
        self.assertIn("本科生资格：明确满足", doc)
        self.assertIn("w:hyperlink", doc)
        self.assertIn(f'Target="{EXAMPLE_URL}"', rels)

    def test_recommendation_is_exported(self):
        data = make_result()
        data["results"][0]["recommendation"] = "优先了解：方向直接相关。"
        ex.write_csv(data, str(self.csv_path))
        ex.write_docx(data, str(self.docx_path))
        with open(self.csv_path, encoding="utf-8-sig", newline="") as f:
            row = next(csv.DictReader(f))
        with zipfile.ZipFile(self.docx_path) as z:
            doc = z.read("word/document.xml").decode("utf-8")
        self.assertEqual("优先了解：方向直接相关。", row["recommendation"])
        self.assertIn("推荐：", doc)
        self.assertIn("优先了解：方向直接相关。", doc)

    def test_docx_omits_null_optional_values(self):
        data = make_result()
        data["query"]["conditions"]["grade"] = None
        data["results"][0]["notes"] = None
        ex.write_docx(data, str(self.docx_path))
        with zipfile.ZipFile(self.docx_path) as z:
            doc = z.read("word/document.xml").decode("utf-8")
        self.assertNotIn("None", doc)

    def test_same_result_set_in_csv_and_docx(self):
        second = make_result(name="李四")["results"][0]
        data = make_result(results=[make_result()["results"][0], second])
        ex.write_csv(data, str(self.csv_path))
        ex.write_docx(data, str(self.docx_path))
        with open(self.csv_path, encoding="utf-8-sig", newline="") as f:
            csv_names = [row["name"] for row in csv.DictReader(f)]
        with zipfile.ZipFile(self.docx_path) as z:
            doc = z.read("word/document.xml").decode("utf-8")
        self.assertEqual(["张三", "李四"], csv_names)
        for name in csv_names:
            self.assertIn(name, doc)

    def test_validation_rejects_missing_results(self):
        data = make_result()
        del data["results"]
        with self.assertRaisesRegex(ValueError, "results"):
            ex.validate_results(data)

    def test_validation_rejects_result_without_source(self):
        data = make_result()
        data["results"][0]["sources"] = []
        with self.assertRaisesRegex(ValueError, "sources"):
            ex.validate_results(data)

    def test_validation_rejects_unknown_group(self):
        data = make_result()
        data["results"][0]["group"] = "maybe"
        with self.assertRaisesRegex(ValueError, "group"):
            ex.validate_results(data)

    def test_empty_results_export_is_valid(self):
        data = make_result(results=[])
        ex.write_csv(data, str(self.csv_path))
        ex.write_docx(data, str(self.docx_path))
        with open(self.csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            self.assertIsNotNone(reader.fieldnames)
            self.assertEqual([], list(reader))
        with zipfile.ZipFile(self.docx_path) as z:
            doc = z.read("word/document.xml").decode("utf-8")
        self.assertIn("本轮没有明确匹配", doc)
        self.assertIn("未遍历全目录", doc)

    def test_validation_rejects_confirmed_with_conflicting_condition(self):
        data = make_result()
        data["results"][0]["conditions"]["direction"]["status"] = "conflicts"
        with self.assertRaisesRegex(ValueError, "confirmed"):
            ex.validate_results(data)

    def test_validation_rejects_confirmed_with_non_current_recency(self):
        for status in ("deadline_expired", "none_found"):
            with self.subTest(status=status):
                data = make_result()
                data["results"][0]["recency"]["status"] = status
                with self.assertRaisesRegex(ValueError, "confirmed"):
                    ex.validate_results(data)

    def test_validation_rejects_undergrad_meets_with_none_found(self):
        data = make_result()
        data["results"][0]["group"] = "pending"
        data["results"][0]["recency"].update(
            {"status": "none_found", "quote": None, "source": None}
        )
        with self.assertRaisesRegex(ValueError, "none_found"):
            ex.validate_results(data)

    def test_validation_rejects_pending_with_expired_recency(self):
        data = make_result()
        data["results"][0]["group"] = "pending"
        data["results"][0]["recency"]["status"] = "deadline_expired"
        with self.assertRaisesRegex(ValueError, "pending"):
            ex.validate_results(data)

    def test_validation_requires_evidence_for_positive_condition(self):
        data = make_result()
        data["results"][0]["conditions"]["direction"]["quote"] = None
        with self.assertRaisesRegex(ValueError, "conditions.direction"):
            ex.validate_results(data)

    def test_validation_requires_evidence_for_recency_claim(self):
        data = make_result()
        data["results"][0]["recency"].update(
            {"status": "long_term", "quote": None, "source": None}
        )
        with self.assertRaisesRegex(ValueError, "recency"):
            ex.validate_results(data)

    def test_validation_requires_unknowns_array(self):
        data = make_result()
        del data["results"][0]["unknowns"]
        with self.assertRaisesRegex(ValueError, "unknowns"):
            ex.validate_results(data)

    def test_docx_without_confirmed_reports_zero_confirmed(self):
        data = make_result()
        result = data["results"][0]
        result["group"] = "pending"
        result["conditions"]["undergrad"].update(
            {"status": "unknown", "quote": None, "source": None}
        )
        result["recency"].update(
            {"status": "none_found", "quote": None, "source": None}
        )
        ex.write_docx(data, str(self.docx_path))
        with zipfile.ZipFile(self.docx_path) as z:
            doc = z.read("word/document.xml").decode("utf-8")
        self.assertIn("本轮没有明确匹配", doc)
        self.assertIn("不代表已确认机会", doc)

    def test_example_result_is_valid(self):
        data = json.loads(
            (ROOT / "assets/example-result.json").read_text(encoding="utf-8")
        )
        ex.validate_results(data)

    def test_cli_exports_both_formats(self):
        input_path = self.dir / "input.json"
        out_dir = self.dir / "out"
        input_path.write_text(
            json.dumps(make_result(), ensure_ascii=False), encoding="utf-8"
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "export_results.py"),
                str(input_path),
                "--out-dir",
                str(out_dir),
            ],
            check=True,
            capture_output=True,
        )
        self.assertTrue((out_dir / "results.csv").is_file())
        self.assertTrue((out_dir / "results.docx").is_file())


if __name__ == "__main__":
    unittest.main()
