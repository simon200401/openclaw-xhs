from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "user_state.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_state() -> dict[str, Any]:
    return {"history": [], "favorites": []}


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return _default_state()
    with STATE_PATH.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return _default_state()
    if not isinstance(data, dict):
        return _default_state()
    data.setdefault("history", [])
    data.setdefault("favorites", [])
    return data


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def append_history(job_input: str, report_obj: Any) -> dict[str, Any]:
    state = load_state()
    item = {
        "id": str(uuid.uuid4()),
        "job_input": job_input,
        "created_at": _utc_now_iso(),
        "report": asdict(report_obj),
    }
    state["history"].insert(0, item)
    state["history"] = state["history"][:50]
    save_state(state)
    return item


def list_history() -> list[dict[str, Any]]:
    return load_state()["history"]


def get_history_item(history_id: str) -> Optional[Dict[str, Any]]:
    for item in load_state()["history"]:
        if item.get("id") == history_id:
            return item
    return None


def delete_history_item(history_id: str) -> bool:
    state = load_state()
    before = len(state["history"])
    state["history"] = [h for h in state["history"] if h.get("id") != history_id]
    state["favorites"] = [f for f in state["favorites"] if f.get("history_id") != history_id]
    changed = len(state["history"]) != before
    if changed:
        save_state(state)
    return changed


def add_favorite(history_id: str, note: str = "") -> Optional[Dict[str, Any]]:
    state = load_state()
    history = next((h for h in state["history"] if h.get("id") == history_id), None)
    if history is None:
        return None
    if any(f.get("history_id") == history_id for f in state["favorites"]):
        return next(f for f in state["favorites"] if f.get("history_id") == history_id)

    fav = {
        "history_id": history_id,
        "job_input": history.get("job_input", ""),
        "note": note,
        "created_at": _utc_now_iso(),
    }
    state["favorites"].insert(0, fav)
    save_state(state)
    return fav


def remove_favorite(history_id: str) -> bool:
    state = load_state()
    before = len(state["favorites"])
    state["favorites"] = [f for f in state["favorites"] if f.get("history_id") != history_id]
    changed = len(state["favorites"]) != before
    if changed:
        save_state(state)
    return changed


def list_favorites() -> list[dict[str, Any]]:
    return load_state()["favorites"]
