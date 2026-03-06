from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

FreqLevel = Literal["高频", "中频", "低频"]


@dataclass
class JobInfo:
    raw_input: str
    company: str
    position_name: str
    direction: str
    role_type: str
    possible_business_lines: List[str]
    core_capabilities: List[str]


@dataclass
class SearchKeywords:
    groups: dict[str, List[str]]


@dataclass
class InterviewRound:
    round_name: str
    estimated_duration_minutes: Optional[int]
    focus: List[str]
    evidence_count: int
    inferred: bool


@dataclass
class QuestionItem:
    question: str
    frequency: FreqLevel


@dataclass
class QuestionCategory:
    category: str
    assessed_capability: str
    frequency: FreqLevel
    questions: List[QuestionItem] = field(default_factory=list)


@dataclass
class AnswerFramework:
    framework_name: str
    when_to_use: str
    steps: List[str]


@dataclass
class PreparationAction:
    priority: Literal["P0", "P1", "P2"]
    action: str
    deliverable: str


@dataclass
class ExampleAnswer:
    question: str
    answer_outline: List[str]
    caution: str


@dataclass
class ConfidenceScore:
    overall: float
    modules: dict[str, float]
    basis: List[str]


@dataclass
class Report:
    target_job_info: JobInfo
    recommended_search_keywords: SearchKeywords
    interview_rounds: List[InterviewRound]
    high_frequency_questions: List[QuestionCategory]
    answer_frameworks: List[AnswerFramework]
    preparation_suggestions: List[PreparationAction]
    example_answers: List[ExampleAnswer]
    confidence: ConfidenceScore
    source_summary: dict[str, int]
