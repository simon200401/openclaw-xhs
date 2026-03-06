from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from src.report_generator import build_report
from src.role_parser import parse_job
from src.sample_loader import load_sample_posts
from src import state_store


def test_report_contains_example_answers_and_confidence():
    samples = load_sample_posts()
    report = build_report(parse_job("美团商业分析实习"), samples["美团商业分析实习"])

    assert report.example_answers
    assert 0 <= report.confidence.overall <= 1
    assert "岗位解析" in report.confidence.modules


def test_p2_history_favorite_export_flow(tmp_path, monkeypatch):
    temp_state = tmp_path / "state.json"
    temp_state.write_text('{"history": [], "favorites": []}', encoding="utf-8")
    monkeypatch.setattr(state_store, "STATE_PATH", Path(temp_state))

    client = TestClient(app)

    analyze_res = client.post("/api/analyze", json={"job_input": "快手策略产品实习", "save_history": True})
    assert analyze_res.status_code == 200
    payload = analyze_res.json()
    history_id = payload["history_id"]
    assert history_id

    history_res = client.get("/api/history")
    assert history_res.status_code == 200
    assert any(x["id"] == history_id for x in history_res.json()["items"])

    fav_res = client.post("/api/favorites", json={"history_id": history_id})
    assert fav_res.status_code == 200

    exp_json = client.get(f"/api/export/{history_id}.json")
    assert exp_json.status_code == 200
    assert exp_json.json()["id"] == history_id

    exp_md = client.get(f"/api/export/{history_id}.md")
    assert exp_md.status_code == 200
    assert "岗位面试情报报告" in exp_md.text
