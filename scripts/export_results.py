# -*- coding: utf-8 -*-
"""Export a research-opportunity result JSON to CSV and DOCX.

Usage:
    python scripts/export_results.py results.json --out-dir out --formats csv,docx

The exporter intentionally uses only the Python standard library so the skill
works in a bare host environment. The DOCX is a minimal but valid OOXML
package with external hyperlinks for every source.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import zipfile
from xml.sax.saxutils import escape, quoteattr

STATUS_LABELS = {
    "meets": "明确满足",
    "conflicts": "明确冲突",
    "unknown": "未说明",
}
RECENCY_LABELS = {
    "deadline_open": "明确有效期（未截止）",
    "long_term": "长期接收",
    "posted_quota_tbd": "曾发布-当前名额待确认",
    "deadline_expired": "已截止",
    "none_found": "未找到本科生招募信息",
}
GROUP_LABELS = {
    "confirmed": "明确匹配",
    "pending": "资格待确认",
    "lead": "待核实线索",
}
GROUP_ORDER = ("confirmed", "pending", "lead")
MODE_LABELS = {
    "information": "信息展示",
    "matching": "匹配模式",
}
CSV_COLUMNS = [
    "name",
    "college",
    "lab",
    "title",
    "direction",
    "topic",
    "undergrad_statement",
    "direction_status",
    "undergrad_status",
    "grade_status",
    "school_status",
    "time_status",
    "recency_status",
    "unknowns",
    "group",
    "fit_notes",
    "sources",
    "notes",
    "query_mode",
    "coverage_statement",
    "checked_at",
]
CONDITION_FIELDS = ("direction", "undergrad", "grade", "school", "time")


def load_results(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    validate_results(data)
    return data


def validate_results(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("results: root must be a JSON object")
    query = data.get("query")
    if not isinstance(query, dict):
        raise ValueError("query: required object")
    if query.get("mode") not in MODE_LABELS:
        raise ValueError("query.mode: must be information or matching")
    if not str(query.get("checked_at", "")).strip():
        raise ValueError("query.checked_at: required")
    coverage = query.get("coverage")
    if not isinstance(coverage, dict) or not str(coverage.get("statement", "")).strip():
        raise ValueError("query.coverage.statement: required")

    results = data.get("results")
    if not isinstance(results, list):
        raise ValueError(
            "results: required array; use [] for a valid zero-match result"
        )
    for index, result in enumerate(results):
        prefix = f"results[{index}]"
        if not isinstance(result, dict):
            raise ValueError(f"{prefix}: must be an object")
        for key in ("name", "college", "direction", "undergrad_statement"):
            if not str(result.get(key, "")).strip():
                raise ValueError(f"{prefix}.{key}: required")
        if result.get("group") not in GROUP_LABELS:
            raise ValueError(
                f"{prefix}.group: must be one of {', '.join(GROUP_LABELS)}"
            )
        conditions = result.get("conditions")
        if not isinstance(conditions, dict):
            raise ValueError(f"{prefix}.conditions: required object")
        for field in CONDITION_FIELDS:
            condition = conditions.get(field)
            if not isinstance(condition, dict) or not condition.get("status"):
                raise ValueError(f"{prefix}.conditions.{field}: required")
            if condition["status"] not in STATUS_LABELS:
                raise ValueError(
                    f"{prefix}.conditions.{field}.status: must be one of "
                    f"{', '.join(STATUS_LABELS)}"
                )
        recency = result.get("recency")
        if not isinstance(recency, dict) or not recency.get("status"):
            raise ValueError(f"{prefix}.recency: required")
        if recency["status"] not in RECENCY_LABELS:
            raise ValueError(
                f"{prefix}.recency.status: must be one of "
                f"{', '.join(RECENCY_LABELS)}"
            )
        sources = result.get("sources")
        if not isinstance(sources, list) or not sources:
            raise ValueError(f"{prefix}.sources: at least one source is required")
        for source_index, source in enumerate(sources):
            if not isinstance(source, dict):
                raise ValueError(f"{prefix}.sources[{source_index}]: must be an object")
            if not str(source.get("label", "")).strip():
                raise ValueError(f"{prefix}.sources[{source_index}].label: required")
            if not str(source.get("url", "")).strip():
                raise ValueError(f"{prefix}.sources[{source_index}].url: required")
        if not isinstance(result.get("unknowns", []), list):
            raise ValueError(f"{prefix}.unknowns: must be an array")


def _status_label(result: dict, field: str) -> str:
    return STATUS_LABELS[result["conditions"][field]["status"]]


def _sources_text(sources: list) -> str:
    return "；".join(f"{s['label']}：{s['url']}" for s in sources)


def write_csv(data: dict, path: str) -> None:
    validate_results(data)
    query = data["query"]
    coverage_statement = query.get("coverage", {}).get("statement", "")
    rows = []
    for result in data["results"]:
        rows.append(
            {
                "name": result["name"],
                "college": result.get("college", ""),
                "lab": result.get("lab", ""),
                "title": result.get("title", ""),
                "direction": result.get("direction", ""),
                "topic": result.get("topic", ""),
                "undergrad_statement": result.get("undergrad_statement", ""),
                "direction_status": _status_label(result, "direction"),
                "undergrad_status": _status_label(result, "undergrad"),
                "grade_status": _status_label(result, "grade"),
                "school_status": _status_label(result, "school"),
                "time_status": _status_label(result, "time"),
                "recency_status": RECENCY_LABELS[result["recency"]["status"]],
                "unknowns": "；".join(result.get("unknowns") or []),
                "group": GROUP_LABELS[result["group"]],
                "fit_notes": result.get("fit_notes") or "",
                "sources": _sources_text(result["sources"]),
                "notes": result.get("notes") or "",
                "query_mode": query["mode"],
                "coverage_statement": coverage_statement,
                "checked_at": result.get("checked_at") or query["checked_at"],
            }
        )
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _run(text: str, bold: bool = False, size: int = 21, color: str | None = None,
         underline: bool = False) -> str:
    props = [
        '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Microsoft YaHei"/>',
        f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>',
    ]
    if bold:
        props.append("<w:b/><w:bCs/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if underline:
        props.append('<w:u w:val="single"/>')
    return (
        "<w:r><w:rPr>" + "".join(props) + "</w:rPr>"
        f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
    )


def _paragraph(runs: str, space_after: int = 80, keep_next: bool = False) -> str:
    props = [f'<w:spacing w:after="{space_after}" w:line="300" w:lineRule="auto"/>']
    if keep_next:
        props.append("<w:keepNext/>")
    return f"<w:p><w:pPr>{''.join(props)}</w:pPr>{runs}</w:p>"


def _hyperlink(text: str, rel_id: str) -> str:
    return (
        f'<w:hyperlink r:id="{rel_id}">'
        + _run(text, color="0563C1", underline=True)
        + "</w:hyperlink>"
    )


def _build_docx_parts(data: dict) -> dict:
    query = data["query"]
    coverage = query.get("coverage", {})
    conditions = query.get("conditions", {})
    condition_text = "；".join(
        f"{key}：{value}" for key, value in conditions.items() if str(value).strip()
    )
    mode = MODE_LABELS[query["mode"]]

    rels = []
    rel_id = 1

    def source_rel(url: str) -> str:
        nonlocal rel_id
        current = f"rIdSource{rel_id}"
        rel_id += 1
        rels.append(
            "<Relationship "
            f'Id="{current}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" '
            f"Target={quoteattr(url)} TargetMode=\"External\"/>"
        )
        return current

    body = []
    body.append(_paragraph(_run("西交大本科科研机会发现结果", bold=True, size=32), 200))
    body.append(_paragraph(_run(f"模式：{mode}", bold=True, size=23), 60))
    if condition_text:
        body.append(_paragraph(_run(f"检索条件：{condition_text}"), 60))
    body.append(_paragraph(_run(f"核查日期：{query['checked_at']}"), 60))
    if coverage.get("statement"):
        body.append(_paragraph(_run(f"覆盖说明：{coverage['statement']}"), 60))
    if coverage.get("stop_reason"):
        body.append(_paragraph(_run(f"停止原因：{coverage['stop_reason']}"), 60))
    body.append(_paragraph(_run("", size=10), 40))

    if not data["results"]:
        body.append(_paragraph(_run("本轮没有明确匹配。", bold=True, size=24), 100))
        body.append(
            _paragraph(
                _run(
                    "零个明确匹配是有效结果；未用相似候选填充。"
                    "可以放宽非硬条件后重新搜索。",
                    size=21,
                ),
                100,
            )
        )

    for group in GROUP_ORDER:
        group_results = [r for r in data["results"] if r["group"] == group]
        if not group_results:
            continue
        body.append(
            _paragraph(
                _run(f"{GROUP_LABELS[group]}（{len(group_results)}）", bold=True, size=28),
                100,
                keep_next=True,
            )
        )
        for number, result in enumerate(group_results, 1):
            heading = f"{number}. {result['name']} · {result.get('college', '')}"
            body.append(_paragraph(_run(heading, bold=True, size=24), 60, keep_next=True))
            details = [
                ("实验室", result.get("lab", "")),
                ("职称", result.get("title", "")),
                ("研究方向", result.get("direction", "")),
                ("具体课题", result.get("topic", "")),
                ("本科生招募", result.get("undergrad_statement", "")),
                (
                    "条件判断",
                    "；".join(
                        f"{field}：{_status_label(result, field)}"
                        for field in CONDITION_FIELDS
                    ),
                ),
                ("时效", RECENCY_LABELS[result["recency"]["status"]]),
                ("待确认", "；".join(result.get("unknowns") or [])),
                ("匹配说明", result.get("fit_notes", "")),
                ("备注", result.get("notes", "")),
            ]
            for label, value in details:
                if str(value).strip():
                    body.append(
                        _paragraph(
                            _run(f"{label}：", bold=True) + _run(str(value)),
                            40,
                        )
                    )
            source_runs = [_run("来源：", bold=True)]
            for index, source in enumerate(result["sources"]):
                if index:
                    source_runs.append(_run("；"))
                rid = source_rel(source["url"])
                source_runs.append(_hyperlink(f"{source['label']}：{source['url']}", rid))
            body.append(_paragraph("".join(source_runs), 120))
            body.append(
                _paragraph(
                    _run("—" * 24, size=16, color="BFBFBF"),
                    60,
                )
            )

    sect = (
        "<w:sectPr>"
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="708" w:footer="708" w:gutter="0"/>'
        "</w:sectPr>"
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<w:body>"
        + "".join(body)
        + sect
        + "</w:body></w:document>"
    )
    document_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels)
        + "</Relationships>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    package_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        "</Relationships>"
    )
    return {
        "[Content_Types].xml": content_types,
        "_rels/.rels": package_rels,
        "word/document.xml": document,
        "word/_rels/document.xml.rels": document_rels,
    }


def write_docx(data: dict, path: str) -> None:
    validate_results(data)
    parts = _build_docx_parts(data)
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in parts.items():
            z.writestr(name, content.encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="result JSON produced by the skill")
    parser.add_argument("--out-dir", default=".", help="output directory (default: .)")
    parser.add_argument(
        "--formats",
        default="csv,docx",
        help="comma-separated formats: csv,docx (default: csv,docx)",
    )
    args = parser.parse_args(argv)
    formats = [item.strip().lower() for item in args.formats.split(",") if item.strip()]
    unknown = [item for item in formats if item not in ("csv", "docx")]
    if unknown:
        parser.error(f"unknown format(s): {', '.join(unknown)}")
    if not formats:
        parser.error("at least one format is required")

    data = load_results(args.input)
    os.makedirs(args.out_dir, exist_ok=True)
    written = []
    if "csv" in formats:
        path = os.path.join(args.out_dir, "results.csv")
        write_csv(data, path)
        written.append(path)
    if "docx" in formats:
        path = os.path.join(args.out_dir, "results.docx")
        write_docx(data, path)
        written.append(path)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
