from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from src.models import InterviewRound, JobInfo, QuestionCategory, QuestionItem
from src.rules import AD_PATTERNS, LOW_INFO_PATTERNS, QUESTION_HINTS, ROLE_PROFILES, ROUND_PATTERNS


def _text_of_post(post: dict[str, Any]) -> str:
    title = str(post.get("title", ""))
    content = str(post.get("content", ""))
    tags = " ".join(post.get("tags", [])) if isinstance(post.get("tags"), list) else ""
    return f"{title}\n{content}\n{tags}".strip()


def _is_invalid_post(text: str) -> bool:
    lower = text.lower()
    if any(x in lower for x in AD_PATTERNS):
        return True
    info_len = len(re.sub(r"\s+", "", text))
    if info_len < 40:
        return True
    if any(x in text for x in LOW_INFO_PATTERNS) and "面试" not in text:
        return True
    return False


def _extract_rounds(text: str) -> tuple[dict[str, int], dict[str, list[int]]]:
    round_counter: dict[str, int] = defaultdict(int)
    round_durations: dict[str, list[int]] = defaultdict(list)

    for round_name, aliases in ROUND_PATTERNS.items():
        for alias in aliases:
            if alias.lower() in text.lower():
                round_counter[round_name] += 1

                # 只在该段附近抓取时长
                for m in re.finditer(r"(\d{1,3})\s*(分钟|min|mins)", text.lower()):
                    minute = int(m.group(1))
                    if 5 <= minute <= 180:
                        round_durations[round_name].append(minute)
    return round_counter, round_durations


def _extract_questions(text: str) -> list[str]:
    candidates: list[str] = []
    # 按标点和换行切分
    chunks = re.split(r"[\n。；;]", text)
    for chunk in chunks:
        line = chunk.strip(" -•\t")
        if not line:
            continue
        lower = line.lower()
        has_question_mark = "?" in line or "？" in line
        has_hint = any(hint in lower for hint in QUESTION_HINTS)
        if has_question_mark or has_hint:
            line = re.sub(r"^[0-9一二三四五六七八九十]+[、.)]\s*", "", line)
            line = re.sub(r"\s+", " ", line).strip()
            if 8 <= len(line) <= 120:
                candidates.append(line)
    return candidates


def _normalize_question(q: str) -> str:
    q = q.strip()
    q = q.replace("？", "?")
    q = re.sub(r"\s+", " ", q)
    q = re.sub(r"(请问|能否|可以)", "", q)
    return q.strip(" ?")


def _category_rules(role_type: str) -> dict[str, list[str]]:
    if role_type == "business_analyst":
        return {
            "SQL题": ["sql", "join", "窗口函数", "留存", "转化", "查询"],
            "指标与异动分析": ["指标", "波动", "异动", "原因", "漏斗", "留存"],
            "Case拆解": ["case", "分析", "怎么提升", "策略"],
            "项目深挖": ["项目", "负责", "难点", "复盘"],
            "AB测试": ["ab", "a/b", "实验", "显著性", "分流"],
        }
    if role_type == "strategy_product":
        return {
            "策略拆解": ["策略", "目标", "拆解", "权衡"],
            "增长Case": ["增长", "转化", "拉新", "留存"],
            "供需匹配": ["供需", "匹配", "分发", "调度"],
            "实验设计": ["实验", "ab", "因果", "验证"],
            "项目推进": ["推动", "协作", "冲突", "排期"],
        }
    if role_type == "ai_product":
        return {
            "场景设计": ["场景", "用户需求", "工作流", "体验"],
            "模型边界": ["幻觉", "边界", "能力", "失败案例"],
            "RAG/Agent": ["rag", "agent", "检索", "工具调用"],
            "评估方法": ["评估", "指标", "效果", "benchmark"],
            "产品策略": ["商业化", "成本", "安全", "路线"],
        }
    return {
        "需求分析": ["需求", "场景", "用户"],
        "产品设计": ["设计", "方案", "流程"],
        "项目推进": ["推进", "协作", "冲突"],
    }


def _capability_for_category(role_type: str, category: str) -> str:
    mapping = {
        "SQL题": "SQL建模与数据抽取能力",
        "指标与异动分析": "指标体系与归因能力",
        "Case拆解": "业务拆解与策略推演能力",
        "项目深挖": "项目贡献量化与反思能力",
        "AB测试": "实验设计与效果验证能力",
        "策略拆解": "策略目标拆解与约束权衡能力",
        "增长Case": "增长诊断与杠杆识别能力",
        "供需匹配": "双边市场机制理解能力",
        "实验设计": "策略实验与归因能力",
        "项目推进": "跨团队推进与落地能力",
        "场景设计": "AI场景抽象与用户价值判断",
        "模型边界": "模型能力边界识别与风险控制",
        "RAG/Agent": "系统方案设计与工程可行性判断",
        "评估方法": "离线/在线评估体系设计",
        "产品策略": "商业化、成本与安全平衡能力",
        "需求分析": "需求洞察与问题定义能力",
        "产品设计": "方案设计与取舍能力",
    }
    if category in mapping:
        return mapping[category]
    profile = ROLE_PROFILES.get(role_type, ROLE_PROFILES["generic"])
    return "、".join(profile["capabilities"][:2])


def extract_interview_signals(job: JobInfo, posts: list[dict[str, Any]]) -> dict[str, Any]:
    filtered_posts: list[str] = []
    dropped = 0

    round_counter: Counter[str] = Counter()
    round_durations: dict[str, list[int]] = defaultdict(list)
    raw_questions: list[str] = []

    for post in posts:
        text = _text_of_post(post)
        if _is_invalid_post(text):
            dropped += 1
            continue

        filtered_posts.append(text)
        rc, rd = _extract_rounds(text)
        for k, v in rc.items():
            round_counter[k] += v
        for k, v in rd.items():
            round_durations[k].extend(v)

        raw_questions.extend(_extract_questions(text))

    normalized = [_normalize_question(q) for q in raw_questions]
    normalized = [q for q in normalized if q]
    q_counter = Counter(normalized)

    rules = _category_rules(job.role_type)
    category_to_questions: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for q, cnt in q_counter.items():
        lower = q.lower()
        assigned = False
        for category, kws in rules.items():
            if any(kw in lower for kw in kws):
                category_to_questions[category].append((q, cnt))
                assigned = True
                break
        if not assigned:
            # 按岗位默认偏好收拢，避免过多“其他”
            first_category = next(iter(rules.keys()))
            category_to_questions[first_category].append((q, cnt))

    question_categories: list[QuestionCategory] = []
    for category, items in category_to_questions.items():
        items = sorted(items, key=lambda x: x[1], reverse=True)
        top_items = items[:8]
        max_count = top_items[0][1] if top_items else 0
        if max_count >= 3:
            freq = "高频"
        elif max_count == 2:
            freq = "中频"
        else:
            freq = "低频"

        question_categories.append(
            QuestionCategory(
                category=category,
                assessed_capability=_capability_for_category(job.role_type, category),
                frequency=freq,
                questions=[QuestionItem(question=q, frequency=("高频" if c >= 3 else "中频" if c == 2 else "低频")) for q, c in top_items],
            )
        )

    rounds: list[InterviewRound] = []
    for round_name in ["一面", "二面", "三面", "HR面"]:
        count = round_counter.get(round_name, 0)
        if count <= 0:
            continue
        durs = round_durations.get(round_name, [])
        dur = int(sum(durs) / len(durs)) if durs else None
        rounds.append(
            InterviewRound(
                round_name=round_name,
                estimated_duration_minutes=dur,
                focus=[],
                evidence_count=count,
                inferred=False,
            )
        )

    return {
        "rounds": rounds,
        "question_categories": sorted(question_categories, key=lambda x: {"高频": 0, "中频": 1, "低频": 2}[x.frequency]),
        "source_summary": {
            "input_posts": len(posts),
            "used_posts": len(filtered_posts),
            "dropped_posts": dropped,
            "extracted_questions": len(normalized),
            "unique_questions": len(q_counter),
        },
    }
