from __future__ import annotations

import re
from src.models import JobInfo
from src.rules import COMPANY_TOKENS, ROLE_PROFILES


def _detect_company(text: str) -> str:
    for token in COMPANY_TOKENS:
        if token.lower() in text.lower():
            return token
    return "未明确"


def _detect_role_type(text: str) -> str:
    lower = text.lower()
    for role_type, profile in ROLE_PROFILES.items():
        for alias in profile["aliases"]:
            if alias.lower() in lower:
                return role_type
    return "generic"


def _extract_position_name(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    return text or "未命名岗位"


def parse_job(user_input: str) -> JobInfo:
    role_type = _detect_role_type(user_input)
    company = _detect_company(user_input)
    profile = ROLE_PROFILES[role_type]

    if "实习" in user_input:
        direction_suffix = "（实习）"
    elif any(x in user_input for x in ["校招", "应届"]):
        direction_suffix = "（校招）"
    else:
        direction_suffix = "（社招/未标注）"

    return JobInfo(
        raw_input=user_input,
        company=company,
        position_name=_extract_position_name(user_input),
        direction=profile["direction"],
        role_type=role_type,
        possible_business_lines=profile["business_lines"],
        core_capabilities=profile["capabilities"] + [direction_suffix],
    )
