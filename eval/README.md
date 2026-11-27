# eval 目录说明

本目录保存开发测试用的固定样本、跨院系案例和对话验收场景。它不是对外招生产品，也不构成对任何教师的评价。

## 文件

| 文件 | 用途 |
|---|---|
| `sample-teachers.json` | 20 人选样名册：顺序、姓名、职称、主页、选样规则 |
| `faculty-sample.json` | 20 人逐页标注：方向、本科生资格、年级、校籍、时间、时效、原文与来源 |
| `development-cases.md` | 张妮、曹建福、刘龙军 3 个页面阅读案例，以及 3 类归属验收情形 |
| `scenarios.md` | S1–S20 对话验收场景与预期行为 |

## 选样规则

- 来源：西安交通大学计算机科学与技术学院教师目录默认顺序。
- 目录 URL：`https://gr.xjtu.edu.cn/units_teacherlist.jsp?urltype=tsites.CollegeTeacherList&wbtreeid=1021&st=0&id=1025&lang=zh_CN`
- 取前 20 位，顺序固定，不因目录更新替换；如需新增样本，另建文件或在末尾追加并注明日期，不要改动原 20 人。
- 核查日期：**2026-11-27**。所有 `checked_at` 均为该日期；复测时更新为实际日期，不能沿用旧日期冒充新核查。

## 字段含义

每个教师在 `faculty-sample.json` 中包含：

- `direction.status`：`stated`（页面有可归属的研究方向）/ `not_stated`（没有）。
- `undergrad.status`：`accepted`（明确欢迎本科生参与科研）/ `not_stated`（未提）/ `conflict`（明确只招研究生或不接收本科生）。
- `grade.status`、`school.status`、`time.status`：`stated` / `not_stated` / `conflict`。
- `recency.status`：`deadline_open` / `long_term` / `posted_quota_tbd` / `deadline_expired` / `none_found`。
- `quote`、`source`、`published_at`、`checked_at`：支撑判断的原句、直达页面、发布日期、核查日期。`not_stated` 和 `none_found` 不填原句与来源。
- `checked_pages`：实际查过的页面；至少包含主页和“我的新闻”列表，避免把“没查”写成“没有”。

## 怎样复测

1. 打开 `sample-teachers.json`，按顺序访问每位教师主页。
2. 对照 `faculty-sample.json` 的 `checked_pages`，重新阅读主页、招生信息、我的新闻和公告详情。
3. 逐项核对 `quote` 是否仍在页面原文中、`source` 是否能直达、`published_at` 是否与页面一致。
4. 运行 `python -m unittest tests.test_eval_sample -v`，确认结构、证据字段和多样性断言通过。
5. 如页面变化，记录变化日期和旧结论，不要静默改写历史样本；新增结论另起字段或另建文件。

## 使用边界

- 样本只描述本轮覆盖，不代表计算机学院或西交大全部教师，也不代表当前招生状态。
- 样本不用于对外宣传、排名或教师评价；不比较人品、课题组氛围或指导风格。
- 20 人样本规模小，不能据此推断全校召回率；开放搜索的额外发现需人工复核。
- 真实学生试用与对照实验尚未完成，相关指标只用于内部开发。
