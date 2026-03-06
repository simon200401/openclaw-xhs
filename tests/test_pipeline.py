from src.report_generator import build_report
from src.role_parser import parse_job
from src.sample_loader import load_sample_posts


def test_role_differentiation_between_ba_and_strategy_product():
    samples = load_sample_posts()

    ba_job = parse_job("美团商业分析实习")
    ba_report = build_report(ba_job, samples["美团商业分析实习"])

    sp_job = parse_job("快手策略产品实习")
    sp_report = build_report(sp_job, samples["快手策略产品实习"])

    ba_categories = {c.category for c in ba_report.high_frequency_questions}
    sp_categories = {c.category for c in sp_report.high_frequency_questions}

    assert "SQL题" in ba_categories
    assert "策略拆解" in sp_categories or "增长Case" in sp_categories
    assert ba_categories != sp_categories


def test_rounds_always_include_inference_label_when_insufficient_evidence():
    job = parse_job("某公司AI产品实习")
    report = build_report(job, posts=[])

    assert len(report.interview_rounds) == 4
    assert all(r.inferred for r in report.interview_rounds)
    assert all(r.estimated_duration_minutes is None for r in report.interview_rounds)
