# xjtu-research-opportunities

西交大本科生科研机会发现 Skill。学生用自然语言提出方向、年级、时间等条件，Skill 检索西交大教师门户与公开页面，按统一证据规则核验，输出带原文、直达页面、发布日期和核查日期的候选名单；默认对话交付，可按需导出 CSV 或 Word。

## 首版范围

- 固定服务**西安交通大学本科生**，范围限**西交大本校科研实习**。
- 首批测试领域为计算机与人工智能，可发现西交大其他院系的机会。
- 校内课题组招收学生加入的合作项目可纳入，须注明合作方与实际工作地点；企业自行招募、教师仅转发的岗位排除；归属无法核实的联合项目只作待核实线索。
- 不做跨校申请、校内登录、简历投递或历史记录。

## 安装

把整个目录放到宿主的 skills 目录，例如：

```text
<skills-dir>/xjtu-research-opportunities/
├── SKILL.md
├── references/
├── assets/
├── scripts/
└── eval/
```

宿主通过 `SKILL.md` 的 frontmatter（`name: xjtu-research-opportunities`）识别技能。`references/` 必须与 `SKILL.md` 一起保留；`scripts/export_results.py` 只在导出时调用，运行时不需要第三方 Python 包。

## 调用示例

**信息展示（按条件列老师）**

> 我是西交大计算机大二学生，想找做大模型或智能体、明确欢迎本科生的课题组，先客观列出来。

**匹配模式（结合背景比较）**

> 我会 Python，做过一点 RAG，每周能投入 6 小时，想找智能体方向能带本科生的老师，帮我按匹配程度排一下。

**探索方向**

> 我对 AI 感兴趣但还没定方向，西交大有哪些本科生能参与的细分方向？

**限定候选比较**

> 就在曹相湧、邓辉琦、安文斌这三位里比较，别加别人。

**导出**

> 把刚才的结果导成 Word 和 CSV。

导出命令（结果 JSON 由 Skill 生成）：

```bash
python scripts/export_results.py results.json --out-dir out --formats csv,docx
```

## 目录结构

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 运行入口：范围、模式、条件、检索、核验、交付、导出、禁止事项 |
| `references/xjtu-search-playbook.md` | 门户入口、学院 id、教师页栏目、关键词、预算与已知问题 |
| `references/evidence-rules.md` | E1/E2/E3 证据等级、五类条件、时效五类、归属与分组 |
| `references/result-format.md` | 对话模板、JSON 字段、CSV/DOCX 列、导出命令 |
| `assets/result.schema.json` | 结果 JSON Schema |
| `assets/example-result.json` | 含明确匹配与资格待确认的示例结果 |
| `scripts/export_results.py` | 标准库实现的 CSV/DOCX 导出器 |
| `tests/` | 导出、Skill 契约、样本与验收场景测试 |
| `eval/` | 20 人教师样本、跨院系开发案例、S1–S20 验收场景 |

## 运行测试

```bash
python -m unittest discover -s tests -v
```

仅需 Python 3.10+ 标准库；不需要 `python-docx`、`pytest` 或网络。

导出示例：

```bash
python scripts/export_results.py assets/example-result.json --out-dir .tmp-export --formats csv,docx
```

## 如何验收

1. 运行全部测试，确认导出、契约、样本结构和场景覆盖通过。
2. 用 `eval/development-cases.md` 里的 3 个页面做阅读测试：张妮（明确大二/大三）、曹建福（有发布日期、无截止日期）、刘龙军（常年招收），核对方向、资格、年级、时效判断。
3. 按 `eval/scenarios.md` 的 S1–S20 做对话走查，记录实际覆盖、误判和漏检。
4. 用 `eval/faculty-sample.json` 复核 20 人样本的字段和原文；样本只描述本轮覆盖，不用于对外宣传。
5. 小规模学生试用需真实学生参与，不能由自动化测试代替。

## 已知限制

- 只支持西交大本校，不支持跨校、外校、企业自行招募的岗位。
- 不做校内登录，不读取需要登录的页面；打不开或只有摘要/截图的页面只能作待核实线索。
- 不自动遍历全部学院目录；开放式搜索默认精读 20 位候选，预算用尽时用“本轮找到”表述。
- 教师样本固定为计算机学院目录前 20 位，规模小，结论只描述本轮覆盖。
- 时效判断依赖页面原文；没有截止日期的公告不能确认当前名额。
- 真实学生试用与对照实验尚未完成，相关指标仅用于内部开发。
