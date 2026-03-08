from fastapi.testclient import TestClient

from app.main import app


def test_analyze_with_xiaohongshu_enabled_falls_back_without_crash():
    client = TestClient(app)
    resp = client.post(
        "/api/analyze",
        json={"job_input": "美团商业分析实习", "use_xiaohongshu": True, "save_history": False},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["meta"]["data_source"] in {"xiaohongshu", "sample_fallback"}
    assert "report" in data


def test_status_endpoint_always_returns_xiaohongshu_key():
    client = TestClient(app)
    resp = client.get("/api/status")

    assert resp.status_code == 200
    payload = resp.json()
    assert "xiaohongshu" in payload
    assert "available" in payload["xiaohongshu"]
    assert "cookies_source" in payload["xiaohongshu"]
