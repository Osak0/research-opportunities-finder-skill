# 西交大本科科研机会发现 Skill · MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 交付一个可被学生用自然语言调用、遵循固定证据与时效规则的西交大本科科研机会发现 Skill，并附带可复核的 20 人教师样本、跨院系开发案例、对话场景验收表和 CSV/Word 导出工具。

**Architecture:** Skill 以 `SKILL.md` 为运行入口，把检索路径、证据判定、时效分类和交付模板拆到 `references/`；结果先落为统一 JSON，再由 `scripts/export_results.py` 从同一份 JSON 生成 CSV 与 DOCX。`eval/` 保存 20 人固定样本、3 个跨院系开发案例和对话验收场景，用标准库 `unittest` 验证结构、证据字段和文档契约。

**Tech Stack:** Markdown、JSON Schema、Python 3 标准库（`argparse`、`csv`、`json`、`zipfile`、`xml.etree`、`unittest`）。不引入第三方运行时依赖。

**Spec:** `research-opportunities-finder-skill.md`（产品计划）与 `GLOSSARY.md`（术语约束）。

## Global Constraints

- 首版固定服务对象：西安交通大学本科生；固定范围：西交大本校科研实习。
- 机会归属以招募主体和学生实际加入的团队为准；校内课题组招人加入的合作项目可纳入，须注明合作方与实际工作地点（未知标待确认）。
- 企业自行招募、由校内教师转发的岗位排除；归属无法核实的联合项目只保留为待核实线索。
- 两种模式：信息展示（中性排列、无匹配分数/优先推荐）与匹配模式（解释取舍、可推荐 1–3 个）；模式不明时先让用户选择。
- 每条影响筛选的判断必须有原句、直达页面、发布日期（若有）和核查日期；肯定判断必须由原文支撑。
- 条件状态只用：`明确满足` / `明确冲突` / `未说明`；硬条件冲突排除，未知留给用户判断。
- 时效类别只用：`明确有效期` / `长期接收` / `曾发布-当前名额待确认` / `已截止` / `未找到本科生招募信息`。
- 过期公告不能作为当前名额的依据；未注明截止日的公告不能推断“当前仍在招”。
- 零个明确匹配是有效结果，不得用相似候选填充。
- 默认对话列表；用户要求 CSV 或 Word（.docx）时从同一份结果生成，仅换格式不换结果。
- 开放式搜索默认以精读 20 位候选为开发测试预算；预算用尽时用“本轮找到”表述，不声称查全。
- 仅当用户明确要求查全有限目录时才遍历该目录，并注明实际覆盖与未能核验部分。
- 不展示教师人品、课题组氛围或从论文/职称推测的指导风格；职称、名气、论文总量不作默认排序依据。

## Review Focus

- 用户明确说“跨校/外校/企业实习”时，Skill 不应硬套校内范围，而应说明首版范围并停止或给出校内替代路径。
- 用户给出互相冲突的硬条件（如“只要大二”且“只接受研究生公告”）时，应返回零个明确匹配，而不是放宽条件。
- 公告只有发布日期、没有截止日时，不能写成“当前仍在招”；应落在“曾发布-当前名额待确认”或“未说明”。
- 页面打不开、只有搜索摘要或转载截图时，不能进入明确匹配组；应进入待核实线索。
- 用户中途追加条件时，不能只过滤旧名单；应按合并后的条件重新发现、核验并交付独立完整的新结果。
- 用户说“只比较这几位”时，不能悄悄扩展候选；补充核验只能发生在指定候选范围内。
- 用户只要求“已确认资格”时，不能把资格待确认组混入结果。
- 导出请求只换格式时，CSV/DOCX 的结果集合必须与对话列表一致；空结果也必须生成可读文件。

---

### Task 1: 结果 JSON 契约与 CSV/DOCX 导出

**Files:**
- Create: `assets/result.schema.json`
- Create: `assets/example-result.json`
- Create: `scripts/export_results.py`
- Test: `tests/test_export_results.py`

**Interfaces:**
- Consumes: 无。
- Produces:
  - `load_results(path: str) -> dict`
  - `validate_results(data: dict) -> None`（失败抛 `ValueError`，消息含字段名）
  - `write_csv(data: dict, path: str) -> None`
  - `write_docx(data: dict, path: str) -> None`
  - CLI：`python scripts/export_results.py <results.json> --out-dir <dir> [--formats csv,docx]`
  - 结果 JSON 顶层：`query`（`mode`、`conditions`、`coverage`、`checked_at`）与 `results`（数组）。每条结果至少含 `name`、`college`、`direction`、`undergrad_statement`、`conditions`、`unknowns`、`sources`、`group`。

- [x] **Step 1: 写失败测试（CSV 字段与转义）**

```python
def test_csv_contains_headers_and_escapes(self):
    data = make_result(
        name='张三, 李四',
        direction='多模态\n大模型',
        unknowns=['年级要求', '每周投入时间'],
        sources=[{'label': '教师主页', 'url': 'https://gr.xjtu.edu.cn/example/zh_CN/index.htm'}],
    )
    write_csv(data, self.csv_path)
    with open(self.csv_path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    self.assertEqual(1, len(rows))
    self.assertEqual('张三, 李四', rows[0]['name'])
    self.assertEqual('多模态\n大模型', rows[0]['direction'])
    self.assertEqual('年级要求；每周投入时间', rows[0]['unknowns'])
    self.assertIn('https://gr.xjtu.edu.cn/example/zh_CN/index.htm', rows[0]['sources'])
```

- [x] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_export_results -v`
Expected: FAIL，`ModuleNotFoundError` 或 `ImportError`（`scripts.export_results` 尚不存在）。

- [x] **Step 3: 写失败测试（DOCX 包、超链接与空结果）**

```python
def test_docx_contains_hyperlinks_and_valid_package(self):
    data = make_result()
    write_docx(data, self.docx_path)
    with zipfile.ZipFile(self.docx_path) as z:
        self.assertIn('word/document.xml', z.namelist())
        doc = z.read('word/document.xml').decode('utf-8')
        rels = z.read('word/_rels/document.xml.rels').decode('utf-8')
    self.assertIn('张三', doc)
    self.assertIn('Target="https://gr.xjtu.edu.cn/example/zh_CN/index.htm"', rels)
    self.assertIn('w:hyperlink', doc)

def test_empty_results_export_is_valid(self):
    data = make_result(results=[])
    write_csv(data, self.csv_path)
    write_docx(data, self.docx_path)
    ...
    self.assertIn('本轮没有明确匹配', doc)
```

- [x] **Step 4: 运行测试确认失败**

Run: `python -m unittest tests.test_export_results -v`
Expected: FAIL，`write_docx`/`write_csv` 不存在。

- [x] **Step 5: 写失败测试（校验与格式一致性）**

```python
def test_validation_rejects_result_without_source(self):
    data = make_result()
    data['results'][0]['sources'] = []
    with self.assertRaisesRegex(ValueError, 'sources'):
        validate_results(data)

def test_csv_and_docx_export_same_result_set(self):
    data = make_result(results=[make_result()['results'][0], make_result(name='李四')['results'][0]])
    write_csv(data, self.csv_path)
    write_docx(data, self.docx_path)
    ...
    self.assertEqual(['张三', '李四'], csv_names)
    self.assertTrue(all(name in doc for name in csv_names))
```

- [x] **Step 6: 运行测试确认失败**

Run: `python -m unittest tests.test_export_results -v`
Expected: FAIL，`validate_results` 不存在或未拒绝空来源。

- [x] **Step 7: 实现最小导出器**

要求：
- `validate_results` 检查 `results` 为数组、每条有非空 `name`、`sources` 为非空数组且每项有 `label`/`url`；空 `results` 合法。
- CSV 使用 `utf-8-sig`、固定表头；列表字段用 `；` 连接，来源用 `label：url` 连接。
- DOCX 用 `zipfile` 手写 `[Content_Types].xml`、`_rels/.rels`、`word/document.xml`、`word/_rels/document.xml.rels`；正文含标题、查询信息、每条结果字段、来源超链接、空结果提示；XML 转义；中文字体 `Microsoft YaHei`。
- CLI 默认输出 `results.csv` 与 `results.docx` 到 `--out-dir`（默认当前目录）。

- [x] **Step 8: 运行测试确认通过**

Run: `python -m unittest tests.test_export_results -v`
Expected: PASS（全部用例）。

- [x] **Step 9: 写 JSON Schema 与示例结果**

`assets/result.schema.json` 覆盖 `query`/`results`、`group` 枚举（`confirmed`/`pending`/`lead`）、`conditions` 对象和 `sources` 数组。`assets/example-result.json` 含 1 条明确匹配 + 1 条待核实线索，字段与导出器一致。

- [x] **Step 10: 用示例结果跑通 CLI**

Run: `python scripts/export_results.py assets/example-result.json --out-dir .tmp-export --formats csv,docx`
Expected: 生成 `.tmp-export/results.csv` 与 `.tmp-export/results.docx`，命令退出码 0。

- [x] **Step 11: 提交**

```bash
git add assets/result.schema.json assets/example-result.json scripts/export_results.py tests/test_export_results.py
git commit -m "feat: add result contract and csv/docx export"
```

---

### Task 2: Skill 运行入口与三份配套规则

**Files:**
- Create: `SKILL.md`
- Create: `references/xjtu-search-playbook.md`
- Create: `references/evidence-rules.md`
- Create: `references/result-format.md`
- Create: `README.md`
- Test: `tests/test_skill_contract.py`

**Interfaces:**
- Consumes: Task 1 的 `scripts/export_results.py` 与结果 JSON 字段。
- Produces: 可被宿主加载的 `SKILL.md`（frontmatter `name: xjtu-research-opportunities`）；三份 reference 的稳定文件名；README 的安装与调用说明。

- [x] **Step 1: 写失败测试（文件与 frontmatter）**

```python
def test_skill_frontmatter_and_references_exist(self):
    text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    self.assertTrue(text.startswith('---\n'))
    self.assertIn('name: xjtu-research-opportunities', text)
    self.assertIn('description:', text)
    for rel in ['references/xjtu-search-playbook.md', 'references/evidence-rules.md', 'references/result-format.md']:
        self.assertTrue((ROOT / rel).is_file(), rel)
```

- [x] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_skill_contract -v`
Expected: FAIL，`SKILL.md` 不存在。

- [x] **Step 3: 写失败测试（运行规则清单）**

测试逐项断言 `SKILL.md` 含以下规则关键词/句子：
`信息展示`、`匹配模式`、`先确定交互模式`、`明确满足`、`明确冲突`、`未说明`、`长期接收`、`曾发布-当前名额待确认`、`已截止`、`待核实线索`、`零个明确匹配`、`CSV`、`.docx`、`同一份结果`、`20 位候选`、`校内`、`企业自行招募`、`合作项目`、`来源`、`核查日期`、`scripts/export_results.py`。

- [x] **Step 4: 运行测试确认失败**

Run: `python -m unittest tests.test_skill_contract -v`
Expected: FAIL，缺少规则条目。

- [x] **Step 5: 写 `SKILL.md`**

结构固定为：
1. 适用范围与默认身份（含排除项、归属规则）。
2. 调用入口：模式判定/追问规则。
3. 条件解析：硬条件 vs 偏好、何时追问、跳过规则。
4. 检索：双路径、预算、覆盖记录。
5. 核验：字段状态、证据等级、时效分类。
6. 交付：信息展示/匹配模式的对话模板、待确认项、来源。
7. 导出：同一份 JSON → CSV/DOCX 的命令。
8. 新要求、限定候选、查全目录、零结果的处理。
9. 禁止事项：不伪造、不用搜索摘要当原文、不把旧公告当当前名额。

- [x] **Step 6: 写三份 reference**

- `xjtu-search-playbook.md`：门户入口、CS/AI/自动化/软件/网安等学院 id、教师页栏目、分页限制、关键词与同义词、双路径、预算与覆盖记录、已知不可达页面的处理。
- `evidence-rules.md`：E1/E2/待核实证据等级；方向/本科生/年级/校籍/时间的判定；原文引用、发布日期、核查日期；时效五类；去重与归属；冲突证据。
- `result-format.md`：对话列表模板（信息展示/匹配模式）、待确认项、覆盖说明、JSON 字段表、CSV/DOCX 列、导出命令。

- [x] **Step 7: 写 `README.md`**

包含：Skill 是什么、首版范围、安装位置、调用示例（信息展示/匹配/比较/导出）、运行测试命令、样本与验收文件位置、已知限制。

- [x] **Step 8: 运行测试确认通过**

Run: `python -m unittest tests.test_skill_contract -v`
Expected: PASS。

- [x] **Step 9: 提交**

```bash
git add SKILL.md README.md references tests/test_skill_contract.py
git commit -m "feat: add skill workflow and evidence rules"
```

---

### Task 3: 20 人教师样本与跨院系开发案例

**Files:**
- Create: `eval/sample-teachers.json`
- Create: `eval/faculty-sample.json`
- Create: `eval/development-cases.md`
- Create: `eval/README.md`
- Test: `tests/test_eval_sample.py`

**Interfaces:**
- Consumes: Task 2 的字段状态与时效分类。
- Produces: 20 条固定样本（每条含 `order`、`name`、`title`、`college`、`homepage`、`checked_at`、`checked_pages`、`direction`、`undergrad`、`grade`、`school`、`time`、`recency`、`unknowns`）；3 个跨院系案例。

- [x] **Step 1: 写失败测试（样本结构与多样性）**

```python
def test_sample_has_20_unique_teachers(self):
    data = json.loads((ROOT / 'eval/faculty-sample.json').read_text(encoding='utf-8'))
    self.assertEqual(20, len(data['teachers']))
    self.assertEqual(20, len({t['name'] for t in data['teachers']}))
    self.assertEqual(20, len({t['homepage'] for t in data['teachers']}))
    for t in data['teachers']:
        self.assertTrue(t['homepage'].startswith('https://gr.xjtu.edu.cn/'))
        self.assertEqual('2026-11-27', t['checked_at'])
        for field in ['direction', 'undergrad', 'grade', 'school', 'time', 'recency']:
            self.assertIn(t[field]['status'], ALLOWED[field])
```

- [x] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_eval_sample -v`
Expected: FAIL，`eval/faculty-sample.json` 不存在。

- [x] **Step 3: 写失败测试（证据与多样性）**

断言：
- 至少 2 条 `undergrad.status == 'accepted'`，且每条有 `quote` 与 `source`。
- 至少 1 条 `recency.status == 'long_term'`。
- 至少 1 条 `recency.status == 'posted_quota_tbd'`。
- 至少 10 条 `recency.status == 'none_found'`。
- 每条 `status != 'not_stated'`/`none_found` 的字段必须有非空 `quote` 与 `source`。
- `development-cases.md` 含张妮、曹建福、刘龙军姓名及关键原文（`大二、大三`、`8-10小时`、`常年招收`）。

- [x] **Step 4: 运行测试确认失败**

Run: `python -m unittest tests.test_eval_sample -v`
Expected: FAIL，缺少 `eval/development-cases.md` 或字段。

- [x] **Step 5: 固定 20 人名单**

从 `https://gr.xjtu.edu.cn/units_teacherlist.jsp?urltype=tsites.CollegeTeacherList&wbtreeid=1021&st=0&id=1025&lang=zh_CN` 的默认顺序取前 20 位：安健、安文斌、鲍军鹏、薄钧戈、曹相湧、陈衡、陈龙、陈妍、仇国巍、崔舒宁、戴慧珺、邓辉琦、丁菡、董小社、龚铁梁、桂小林、何晖、惠维、康宁、赖欣。写入 `eval/sample-teachers.json`，记录选样规则与核查日期 2026-11-27。

- [x] **Step 6: 逐页标注并写 `eval/faculty-sample.json`**

按 `references/evidence-rules.md` 标注。已核实的开发事实：
- 曹相湧首页：“欢迎本科生联系科研训练，每年招收（学/专）硕士3-4名，博士1-2名，欢迎联系！”→ `undergrad.accepted`，`recency.posted_quota_tbd`。
- 邓辉琦新闻（2025-04-08）：“长期招收硕士生、本科生……”→ `undergrad.accepted`，`recency.long_term`。
- 安文斌招生信息仅列 2027 计算机技术（专硕）；陈衡只列硕士/博士名额；丁菡只写 master/Ph.D. students → 本科生招募 `not_stated`，`recency.none_found`。
- 其余无招募信息的教师：`undergrad.not_stated`、`recency.none_found`，保留方向信息或标 `direction.not_stated`。
- 所有 `none_found` 条目的 `checked_pages` 至少含首页与“我的新闻”列表。

- [x] **Step 7: 写 `eval/development-cases.md`**

张妮（CS）：`https://gr.xjtu.edu.cn/nizhang/zh_CN/zdylm/1090690/list/index.htm`，原文含“科研实习生：欢迎大二、大三有余力的本科生加入”“保证每周至少 1 次一对一或小组科研讨论”“持续合作 6 个月以上”；时效标 `posted_quota_tbd`（无截止日）。
曹建福（自动化）：`https://gr.xjtu.edu.cn/cjf/zh_CN/article/256041/content/42033.htm`，发布时间 2026-08-28，原文含“招聘3-5名优秀本科生”“每周能来项目组8-10小时”；时效标 `posted_quota_tbd`。
刘龙军（人工智能）：`https://gr.xjtu.edu.cn/liulongjun/zh_CN/index.htm`，原文含“常年招收……本科生来课题组科研实习”；时效标 `long_term`。
另列三类归属场景（校内团队合作项目=纳入并注明合作方/地点；教师转发企业岗位=排除；归属不明联合项目=待核实线索）。

- [x] **Step 8: 写 `eval/README.md`**

说明样本用途、选样规则、核查日期、字段含义、如何复测、如何新增样本；明确样本只描述本轮覆盖，不用于对外宣传。

- [x] **Step 9: 运行测试确认通过**

Run: `python -m unittest tests.test_eval_sample -v`
Expected: PASS。

- [x] **Step 10: 提交**

```bash
git add eval tests/test_eval_sample.py
git commit -m "test: add 20-teacher eval sample and development cases"
```

---

### Task 4: 对话验收场景与使用说明收口

**Files:**
- Create: `eval/scenarios.md`
- Modify: `README.md`
- Test: `tests/test_scenarios.py`

**Interfaces:**
- Consumes: Task 2 的规则与 Task 3 的样本。
- Produces: S1–S20 场景表；README 的“验收场景”和“已知限制”段落。

- [x] **Step 1: 写失败测试（场景覆盖）**

```python
REQUIRED = ['S1', 'S2', ..., 'S20']
def test_scenarios_cover_required_cases(self):
    text = (ROOT / 'eval/scenarios.md').read_text(encoding='utf-8')
    for sid in REQUIRED:
        self.assertIn(f'## {sid}', text)
    for phrase in ['模式不明', '追加条件', '限定候选', '零个明确匹配', '过期公告', '页面打不开', '只换格式', '跨校', '企业岗位', '合作项目', '归属不明', '查全有限目录']:
        self.assertIn(phrase, text)
```

- [x] **Step 2: 运行测试确认失败**

Run: `python -m unittest tests.test_scenarios -v`
Expected: FAIL，`eval/scenarios.md` 不存在。

- [x] **Step 3: 写 S1–S20 场景**

每条含：学生输入（自然语言）、预期模式、预期检索/核验行为、预期输出、不得出现的行为。必须覆盖：
S1 模式不明只问模式；S2 信息展示中性列表；S3 匹配模式分组与推荐；S4 跳过偏好后比较/并列；S5 严格条件零结果；S6 只看已确认资格；S7 无截止日公告；S8 过期公告；S9 页面打不开/仅截图；S10 追加条件重搜；S11 限定候选比较；S12 只换格式；S13 跨校请求；S14 教师转发企业岗位；S15 校内团队合作项目；S16 归属不明联合项目；S17 查全有限目录；S18 探索方向 3–5 个；S19 零结果表述；S20 新搜索发现旧名单外候选。

- [x] **Step 4: 运行测试确认失败**

Run: `python -m unittest tests.test_scenarios -v`
Expected: FAIL，缺少场景或关键词。

- [x] **Step 5: 更新 README**

增加“如何验收”一节：运行全部测试、用 3 个开发案例做页面阅读测试、用 S1–S20 做对话走查、记录实际覆盖和误判；增加“已知限制”：无跨校、无登录、无自动全目录遍历、样本仅 20 人、真实学生试用待做。

- [x] **Step 6: 运行全部测试确认通过**

Run: `python -m unittest discover -s tests -v`
Expected: PASS（Task 1–4 全部用例）。

- [x] **Step 7: 提交**

```bash
git add eval/scenarios.md README.md tests/test_scenarios.py
git commit -m "docs: add acceptance scenarios and mvp limits"
```

---

## Self-Review

- **Spec coverage:** 范围/归属（Task 2 + Task 3 开发案例）、两模式与三类任务（Task 2 + Task 4 S1–S6/S11/S18）、双路径检索与 20 人预算（Task 2）、证据与时效（Task 2 + Task 3）、交付与导出（Task 1 + Task 2）、20 人样本（Task 3）、验收场景（Task 4）。小规模学生试用不在本计划内，README 标为待做。
- **Step scan:** 每个测试步骤给出断言或断言清单；实现步骤给签名/行为，不写完整程序；导出 CLI 有明确命令与预期。
- **Type consistency:** `write_csv`/`write_docx`/`validate_results`/`load_results` 在测试与实现步骤中同名；JSON 字段 `query`/`results`/`sources`/`group` 在 Task 1/2/3 一致。
- **Review Focus:** 跨校、冲突条件、无截止日公告、打不开页面、追加条件、限定候选、只看已确认、格式一致性均有场景或测试承接。
- **Proportion:** 计划描述决策与验收，不替代 `SKILL.md` 正文；样本数据由 Task 3 落地。
