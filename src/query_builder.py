from __future__ import annotations

from src.models import JobInfo, SearchKeywords
from src.rules import ROLE_PROFILES


def build_search_keywords(job: JobInfo) -> SearchKeywords:
    profile = ROLE_PROFILES[job.role_type]

    job_terms = [job.position_name, job.direction]
    company_terms = [job.company] if job.company != "未明确" else []
    interview_terms = ["面经", "面试题", "面试复盘", "真题"]
    round_terms = ["一面", "二面", "三面", "HR面", "终面"]
    ability_terms = profile["query_tokens"]

    # 组合检索词，提升可解释性
    combo_terms = []
    for base in (company_terms[:1] or [""]):
        for role in job_terms[:1]:
            for hint in interview_terms[:2]:
                combo_terms.append(" ".join(x for x in [base, role, hint] if x))

    return SearchKeywords(
        groups={
            "岗位词": job_terms,
            "公司词": company_terms,
            "面经词": interview_terms,
            "轮次词": round_terms,
            "能力词": ability_terms,
            "推荐组合词": combo_terms[:8],
        }
    )
