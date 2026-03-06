from __future__ import annotations

from typing import Any


def report_to_markdown(report: dict[str, Any]) -> str:
    job = report["target_job_info"]
    rounds = report["interview_rounds"]
    cats = report["high_frequency_questions"]
    frameworks = report["answer_frameworks"]
    prep = report["preparation_suggestions"]
    examples = report.get("example_answers", [])
    conf = report.get("confidence", {})

    lines: list[str] = []
    lines.append(f"# 岗位面试情报报告 - {job['position_name']}")
    lines.append("")
    lines.append("## 1. 目标岗位信息")
    lines.append(f"- 公司：{job['company']}")
    lines.append(f"- 岗位方向：{job['direction']}")
    lines.append(f"- 岗位类型：{job['role_type']}")
    lines.append(f"- 可能业务线：{' / '.join(job['possible_business_lines'])}")
    lines.append(f"- 核心能力：{' / '.join(job['core_capabilities'])}")
    lines.append("")

    lines.append("## 2. 面试轮次信息")
    for r in rounds:
        duration = f"{r['estimated_duration_minutes']}分钟" if r["estimated_duration_minutes"] else "未明确"
        mark = "根据面经与岗位特征推测" if r["inferred"] else "来自面经证据"
        lines.append(f"- {r['round_name']} | 时长：{duration} | 重点：{' / '.join(r['focus'])} | {mark}")
    lines.append("")

    lines.append("## 3. 高频问题")
    for c in cats:
        lines.append(f"### {c['category']}（{c['frequency']}）")
        lines.append(f"- 考察能力：{c['assessed_capability']}")
        for q in c["questions"]:
            lines.append(f"- [{q['frequency']}] {q['question']}")
    lines.append("")

    lines.append("## 4. 答题框架")
    for f in frameworks:
        lines.append(f"- {f['framework_name']}：{' -> '.join(f['steps'])}")
    lines.append("")

    lines.append("## 5. 准备建议")
    for p in prep:
        lines.append(f"- {p['priority']} | {p['action']} | 产出：{p['deliverable']}")
    lines.append("")

    lines.append("## 6. 示例答案")
    for e in examples:
        lines.append(f"- 问题：{e['question']}")
        lines.append(f"- 作答提纲：{' -> '.join(e['answer_outline'])}")
        lines.append(f"- 注意点：{e['caution']}")
    lines.append("")

    lines.append("## 7. 置信度")
    overall = conf.get("overall", 0)
    lines.append(f"- 总体置信度：{overall}")
    for k, v in conf.get("modules", {}).items():
        lines.append(f"- {k}：{v}")
    for b in conf.get("basis", []):
        lines.append(f"- 依据：{b}")

    return "\n".join(lines)
