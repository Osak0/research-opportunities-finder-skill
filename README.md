# Research Opportunities Finder

用公开来源查找本科生科研机会。你可以探索方向、筛选导师和项目，或结合自己的基础和时间比较候选。覆盖校内、跨校、海外以及研究机构和企业发布的研究型机会，具体范围由你的问题决定。

结果会注明招募条件、时效、原文、来源页面与核查日期。页面无法访问或公开信息不足时，结果会明确标注待确认事项。

## 安装

将仓库内容放入宿主技能目录下的 `research-opportunities-finder/`。保留 `SKILL.md`、`references/`、`assets/` 和 `scripts/`。技能入口是 `SKILL.md`，导出需要 Python 3.10 或更高版本，仅使用标准库。

## 使用示例

- “我想找接受外校本科生、可以远程参与的计算机视觉项目，客观列出公开条件。”
- “我会 Python，每周能投入 6 小时，帮我比较本地几个实验室的智能体研究项目。”
- “我对生物信息学感兴趣，想了解适合本科阶段参与的研究方向。”
- “仅比较我提供的三个团队链接，再把结果导成 Word 和 CSV。”

## 导出

Skill 按 [结果格式](references/result-format.md) 和 [JSON Schema](assets/result.schema.json) 生成结果 JSON。使用同一份 JSON 导出两种格式：

```bash
python scripts/export_results.py results.json --out-dir out --formats csv,docx
```

## 文件说明

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 技能入口、检索范围、交互模式与交付规则 |
| [检索指南](references/search-playbook.md) | 查找机构目录、团队主页和公开项目公告 |
| [证据规则](references/evidence-rules.md) | 判断条件、来源、时效和项目归属 |
| [结果格式](references/result-format.md) | 对话模板、JSON 字段和导出格式 |
| [术语表](GLOSSARY.md) | 统一检索和交付术语 |

检索覆盖公开可访问的来源。候选是否仍有名额，以公开招募信息及招募方确认为准。
