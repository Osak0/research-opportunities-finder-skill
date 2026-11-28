# 结果格式与交付模板

结果先写成一份 JSON，再从同一份 JSON 生成对话列表、CSV 和 DOCX。字段定义以 `assets/result.schema.json` 为准，本文件说明怎么写、怎么展示。

## 1. 对话交付模板

### 1.1 信息展示模式

```text
本轮找到 N 位有公开依据的候选（覆盖：……；核查日期：YYYY-MM-DD）。

按学院/目录顺序列出，排列不代表优先推荐。

1. 姓名 · 学院 · 职称
   实验室/团队：
   研究方向：
   具体课题/成果：
   本科生招募：原文“……”（发布日期：……；时效：……）
   条件：方向 明确满足；本科生 明确满足/未说明；年级 未说明；校籍 未说明；时间 未说明
   待确认：年级要求、当前名额、每周投入
   来源：标签：URL

（找导师时，资格待确认组另列，写明缺哪项；找项目时不列）

覆盖说明：本轮精读 X 位候选，未遍历全目录；失败页面：……；停止原因：……。
```

### 1.2 匹配模式

```text
按你的条件（……），先说结论：有区分依据时推荐优先了解 1–3 位；依据不足时并列。

一、有公开依据符合条件
1. 姓名 · 学院
   匹配依据：方向/课题原文……
   取舍：……
   未知信息：……

二、资格待确认（找导师时；找项目时不列）
1. 姓名 · 学院
   方向依据：……
   待确认：本科生资格/年级/当前名额……

三、待核实线索（如有）
……

覆盖说明：……；核查日期：……。
```

要求：

- 信息展示模式**中性排列**，不写匹配分数、不写“最推荐”。
- 匹配模式先列有公开依据符合条件者，再列资格待确认者；两组分别说明学术匹配依据。
- 推荐只在有区分依据时给；依据不足时并列，不硬凑。
- 学生要求“只看已确认资格”时，只保留第一组。
- 每条都保留**待确认**项和**来源**链接；不把未知条件写成满足。

## 2. 结果 JSON

顶层：

```json
{
  "query": {
    "mode": "information",
    "text": "学生原始请求",
    "conditions": {"direction": "...", "grade": "大二"},
    "coverage": {
      "scope": "计算机学院教师目录前 20 位",
      "discovered": 20,
      "read_in_depth": 20,
      "verified": 3,
      "failed_pages": [],
      "stop_reason": "达到精读预算",
      "statement": "本轮覆盖……；未遍历全目录。"
    },
    "checked_at": "2026-11-27"
  },
  "results": []
}
```

`results` 每条字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 否 | 稳定标识，便于去重 |
| `name` | 是 | 教师姓名 |
| `college` | 是 | 学院 |
| `lab` | 否 | 实验室/团队 |
| `title` | 否 | 职称 |
| `direction` | 是 | 可归属到教师/团队的研究方向 |
| `topic` | 否 | 具体课题或本轮可说的研究主题 |
| `undergrad_statement` | 是 | 本科生招募原文；没有时写“未找到……” |
| `conditions` | 是 | 五个条件对象：`direction`、`undergrad`、`grade`、`school`、`time` |
| `recency` | 是 | 时效对象 |
| `unknowns` | 是 | 待确认项数组 |
| `sources` | 是 | 至少一条 `{label, url, published_at?, checked_at?}` |
| `group` | 是 | `confirmed` / `pending` / `lead` |
| `fit_notes` | 否 | 匹配说明；信息展示模式留空或写中性事实 |
| `recommendation` | 否 | 仅匹配模式且有区分依据时填写 |
| `notes` | 否 | 其他说明 |
| `checked_at` | 否 | 单条核查日期，缺省用 `query.checked_at` |

条件对象：

```json
{
  "status": "meets",
  "quote": "原文……",
  "source": "https://……",
  "published_at": "2026-08-28",
  "checked_at": "2026-11-27"
}
```

`status` 枚举与展示标签：

| JSON 值 | 中文展示 |
|---|---|
| `meets` | 明确满足 |
| `conflicts` | 明确冲突 |
| `unknown` | 未说明 |

`recency.status` 枚举与展示标签：

| JSON 值 | 中文展示 |
|---|---|
| `deadline_open` | 明确有效期（未截止） |
| `long_term` | 长期接收 |
| `posted_quota_tbd` | 曾发布-当前名额待确认 |
| `deadline_expired` | 已截止 |
| `none_found` | 未找到本科生招募信息 |

`group` 枚举与展示标签：

| JSON 值 | 中文展示 |
|---|---|
| `confirmed` | 明确匹配 |
| `pending` | 资格待确认 |
| `lead` | 待核实线索 |

`confirmed` 不得含“明确冲突”的条件，也不得使用 `deadline_expired` 或 `none_found` 作为时效；`deadline_expired` 不进入 `confirmed` 或 `pending`。零个 `confirmed` 时，找导师可保留 `pending` / `lead`；找项目只保留 `confirmed`，不能把 `pending` / `lead` 当成项目结果。两种情况都必须明确说明“明确匹配为 0”，不能把后两组当成已确认机会。

`query.mode`：`information`（信息展示）/ `matching`（匹配模式）。

## 3. CSV

固定表头（顺序固定）：

```text
name, college, lab, title, direction, topic, undergrad_statement,
direction_status, undergrad_status, grade_status, school_status, time_status,
recency_status, unknowns, group, fit_notes, recommendation, sources, notes,
query_mode, coverage_statement, checked_at
```

规则：

- 文件编码 **UTF-8 with BOM（`utf-8-sig`）**，Excel 直接打开不乱码。
- 列表字段用中文分号 `；` 连接；来源写成 `标签：URL`，多条来源也用 `；` 连接。
- `query_mode` 显示中文模式标签（`信息展示` / `匹配模式`），不直接写 JSON 枚举。
- 空结果也写出表头，不生成 0 字节文件。
- 换行、逗号、引号由 CSV writer 负责转义，不手工拼接。

## 4. DOCX

- 标题：西交大本科科研机会发现结果。
- 头部：模式、检索条件、核查日期、覆盖说明、停止原因。
- 按“明确匹配 → 资格待确认 → 待核实线索”分组；组内按本轮顺序。
- 每条含教师、学院/实验室、职称、方向、课题、本科生招募、条件判断、时效、待确认项、匹配说明、推荐、备注、来源。
- 检索条件与条件判断使用中文标签（研究方向/本科生资格/年级/校籍/时间），不直接展示 JSON 字段名。
- 来源写成可点击超链接；URL 原样保留，便于复核。
- 空结果或没有 `confirmed` 时写“本轮没有明确匹配”，并说明零结果是有效结果；找导师且仍有 `pending` / `lead` 时，注明“以下为资格待确认/待核实线索，不代表已确认机会”。不能生成空白文档。

## 5. 导出命令

```bash
python scripts/export_results.py results.json --out-dir out --formats csv,docx
```

- 默认格式 `csv,docx`；只导一种时用 `--formats csv` 或 `--formats docx`。
- 输出固定为 `out/results.csv`、`out/results.docx`。
- 只换格式时，输入同一份 `results.json`；不得为导出重新筛选或改写结果。
- 导出前会运行 `validate_results`：缺 `results`、缺来源、缺 `unknowns`、非法 `group` 或状态、肯定判断缺原句/直达页面、`confirmed` 含冲突条件或使用 `deadline_expired`/`none_found` 时效、`pending` 使用 `deadline_expired`、`undergrad` 明确满足却标 `none_found`，都会直接报错，消息带字段名。
