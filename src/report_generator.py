from __future__ import annotations

from src.extractor import extract_interview_signals
from src.models import (
    AnswerFramework,
    ConfidenceScore,
    ExampleAnswer,
    InterviewRound,
    JobInfo,
    PreparationAction,
    Report,
)
from src.query_builder import build_search_keywords
from src.rules import ROLE_PROFILES


ROUND_FOCUS_BY_ROLE = {
    "business_analyst": {
        "一面": ["SQL基础与数据处理", "指标定义准确性", "业务理解"],
        "二面": ["Case拆解", "异动归因", "AB测试设计"],
        "三面": ["项目深挖", "业务优先级判断", "落地协同"],
        "HR面": ["动机匹配", "稳定性", "沟通风格"],
    },
    "strategy_product": {
        "一面": ["策略基本功", "增长漏斗拆解", "业务敏感度"],
        "二面": ["供需匹配策略", "实验方案", "效果评估"],
        "三面": ["跨团队推进", "策略落地复盘", "目标管理"],
        "HR面": ["岗位动机", "协作方式", "压力应对"],
    },
    "ai_product": {
        "一面": ["场景理解", "需求抽象", "产品结构化表达"],
        "二面": ["RAG/Agent方案", "模型边界", "评估方法"],
        "三面": ["商业化与成本", "风险治理", "路线取舍"],
        "HR面": ["组织匹配", "学习能力", "沟通协作"],
    },
    "product_manager": {
        "一面": ["需求定义", "场景分析", "功能取舍"],
        "二面": ["产品方案", "指标设计", "业务协同"],
        "三面": ["项目推进", "冲突处理", "结果复盘"],
        "HR面": ["动机与稳定性", "团队价值观", "成长预期"],
    },
    "generic": {
        "一面": ["岗位基本能力"],
        "二面": ["项目与业务"],
        "三面": ["综合评估"],
        "HR面": ["文化匹配"],
    },
}

FRAMEWORK_STEPS = {
    "SQL题": ["澄清口径与表结构", "先写主查询再补边界", "验证空值/重复/时间窗", "口述复杂度与优化"],
    "异动分析题": ["先定义异动指标与时间段", "分层拆解影响因子", "提出可验证假设", "给出验证路径与优先级"],
    "项目题": ["背景-目标-动作-结果", "量化贡献与对照组", "关键决策和取舍", "复盘可迁移方法"],
    "Case题": ["重述问题与目标", "拆解漏斗或业务链路", "定位核心矛盾", "给方案+风险+验证指标"],
    "AB测试题": ["明确实验目标与主指标", "设计分流与样本量", "识别干扰因素", "解释结果并给后续动作"],
    "策略拆解题": ["定义目标与约束", "拆成可执行杠杆", "比较策略成本收益", "制定实验与迭代节奏"],
    "增长分析题": ["先定增长阶段与北极星", "拆漏斗找断点", "提杠杆并估算影响", "明确验收指标"],
    "实验设计题": ["假设-变量-分组", "指标与样本量", "观察窗口", "判定标准与回滚条件"],
    "项目推进题": ["目标对齐", "里程碑与依赖", "风险管理", "复盘机制"],
}


def _infer_rounds(job: JobInfo, extracted_rounds: list[InterviewRound]) -> list[InterviewRound]:
    focus_map = ROUND_FOCUS_BY_ROLE.get(job.role_type, ROUND_FOCUS_BY_ROLE["generic"])
    rounds_by_name = {r.round_name: r for r in extracted_rounds}

    final: list[InterviewRound] = []
    for name in ["一面", "二面", "三面", "HR面"]:
        if name in rounds_by_name:
            r = rounds_by_name[name]
            r.focus = focus_map.get(name, [])
            r.inferred = r.evidence_count < 2 or r.estimated_duration_minutes is None
            final.append(r)
        else:
            final.append(
                InterviewRound(
                    round_name=name,
                    estimated_duration_minutes=None,
                    focus=focus_map.get(name, []),
                    evidence_count=0,
                    inferred=True,
                )
            )

    return final


def _frameworks_for_role(role_type: str) -> list[AnswerFramework]:
    frameworks = ROLE_PROFILES.get(role_type, ROLE_PROFILES["generic"]).get("frameworks", ["项目题"])
    result: list[AnswerFramework] = []
    for name in frameworks:
        result.append(
            AnswerFramework(
                framework_name=name,
                when_to_use=f"当问题属于{name}或同类场景时",
                steps=FRAMEWORK_STEPS.get(name, ["定义目标", "拆解问题", "给出方案", "说明验证"]),
            )
        )
    return result


def _preparation_actions(job: JobInfo) -> list[PreparationAction]:
    if job.role_type == "business_analyst":
        return [
            PreparationAction("P0", "完成10道SQL高频题并口述思路", "一页SQL错题+口径清单"),
            PreparationAction("P0", "整理2个项目的量化复盘", "每个项目1页STAR+指标变化"),
            PreparationAction("P1", "准备2个AB测试设计案例", "实验目标/分流/显著性模板"),
            PreparationAction("P1", "练习3个异动分析case", "归因树+验证计划"),
            PreparationAction("P2", "按业务线准备问题清单", "面试反问10条"),
        ]
    if job.role_type == "strategy_product":
        return [
            PreparationAction("P0", "构建增长漏斗+策略杠杆库", "1页增长诊断模板"),
            PreparationAction("P0", "准备供需匹配与策略取舍案例", "2个策略case拆解稿"),
            PreparationAction("P1", "练习实验设计与归因表达", "实验设计答题卡"),
            PreparationAction("P1", "沉淀跨团队推进故事", "冲突处理STAR文档"),
            PreparationAction("P2", "按目标公司业务线做对齐", "业务线调研卡片"),
        ]
    if job.role_type == "ai_product":
        return [
            PreparationAction("P0", "准备2个AI产品场景方案", "场景-模型-评估三联表"),
            PreparationAction("P0", "整理RAG/Agent架构取舍", "架构图+风险清单"),
            PreparationAction("P1", "设计离线/在线评估指标", "评估看板模板"),
            PreparationAction("P1", "准备模型边界失败案例", "失败复盘卡片"),
            PreparationAction("P2", "准备商业化与成本讨论", "ROI估算表"),
        ]
    return [
        PreparationAction("P0", "完成岗位核心项目复盘", "项目量化文档"),
        PreparationAction("P1", "练习岗位相关case", "结构化答题模板"),
        PreparationAction("P2", "准备反问问题", "反问清单"),
    ]


def _example_answer_by_category(category: str, question: str) -> ExampleAnswer:
    templates = {
        "SQL题": (
            [
                "先确认口径（时间窗、去重粒度、用户定义）",
                "说明关键表和连接关系，再给核心SQL主干",
                "补充边界处理：空值、重复、异常时间",
                "最后给性能优化或校验方式",
            ],
            "不要只给语法，必须先讲业务口径。",
        ),
        "指标与异动分析": (
            [
                "先定义异常发生区间与主指标",
                "按漏斗/人群/渠道拆解定位断点",
                "提出2-3个可验证假设并给数据验证路径",
                "给出短期止损+长期优化动作",
            ],
            "避免直接拍脑袋结论，必须给验证链路。",
        ),
        "AB测试": (
            [
                "明确实验目标和主次指标",
                "描述分流策略、样本量和观测窗口",
                "识别干扰因素与分层方案",
                "给出判定标准与上线/回滚策略",
            ],
            "不要只说显著性，需结合业务收益解释。",
        ),
        "策略拆解": (
            [
                "重述目标和业务约束",
                "拆分成可执行策略杠杆",
                "按影响-成本优先级排序",
                "设计验证实验并定义成功标准",
            ],
            "避免泛泛而谈，必须给取舍依据。",
        ),
    }
    steps, caution = templates.get(
        category,
        (
            [
                "先重述问题并确认目标",
                "给结构化拆解路径",
                "给可执行方案和指标",
                "补充风险与兜底方案",
            ],
            "避免只讲概念，要有落地动作与指标。",
        ),
    )
    return ExampleAnswer(question=question, answer_outline=steps, caution=caution)


def _build_example_answers(extracted_categories) -> list[ExampleAnswer]:
    answers: list[ExampleAnswer] = []
    for category in extracted_categories[:4]:
        if not category.questions:
            continue
        answers.append(_example_answer_by_category(category.category, category.questions[0].question))
    return answers


def _score(v: float) -> float:
    return round(max(0.0, min(1.0, v)), 2)


def _build_confidence(job: JobInfo, rounds: list[InterviewRound], extracted: dict) -> ConfidenceScore:
    source = extracted["source_summary"]
    used_posts = source.get("used_posts", 0)
    unique_questions = source.get("unique_questions", 0)
    extracted_q = source.get("extracted_questions", 0)

    role_parse = 1.0 if job.role_type != "generic" else 0.55
    retrieval = 0.4 + min(0.5, used_posts * 0.1)
    rounds_score = 1.0 - (sum(1 for r in rounds if r.inferred) / max(1, len(rounds))) * 0.5
    questions_score = 0.25 + min(0.75, unique_questions * 0.08)
    synthesis = 0.35 + min(0.55, extracted_q * 0.04)

    modules = {
        "岗位解析": _score(role_parse),
        "内容证据": _score(retrieval),
        "轮次判断": _score(rounds_score),
        "高频问题提炼": _score(questions_score),
        "岗位化推理": _score(synthesis),
    }
    overall = _score(sum(modules.values()) / len(modules))

    basis = [
        f"有效面经条数={used_posts}",
        f"去重后问题数={unique_questions}",
        f"轮次中推断占比={sum(1 for r in rounds if r.inferred)}/{len(rounds)}",
    ]

    return ConfidenceScore(overall=overall, modules=modules, basis=basis)


def build_report(job: JobInfo, posts: list[dict]) -> Report:
    extracted = extract_interview_signals(job, posts)
    rounds = _infer_rounds(job, extracted["rounds"])
    questions = extracted["question_categories"]

    return Report(
        target_job_info=job,
        recommended_search_keywords=build_search_keywords(job),
        interview_rounds=rounds,
        high_frequency_questions=questions,
        answer_frameworks=_frameworks_for_role(job.role_type),
        preparation_suggestions=_preparation_actions(job),
        example_answers=_build_example_answers(questions),
        confidence=_build_confidence(job, rounds, extracted),
        source_summary=extracted["source_summary"],
    )
