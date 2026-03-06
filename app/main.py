from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from src.exporter import report_to_markdown
from src.report_generator import build_report
from src.role_parser import parse_job
from src.sample_loader import load_sample_posts
from src.state_store import (
    add_favorite,
    append_history,
    delete_history_item,
    get_history_item,
    list_favorites,
    list_history,
    remove_favorite,
)


app = FastAPI(title="岗位定制化面试情报平台", version="0.2.0")


class AnalyzeRequest(BaseModel):
    job_input: str
    posts: Optional[List[Dict[str, Any]]] = None
    save_history: bool = True


class FavoriteRequest(BaseModel):
    history_id: str
    note: str = ""


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    job = parse_job(req.job_input)
    sample = load_sample_posts()
    posts = req.posts if req.posts is not None else sample.get(req.job_input, [])
    report = build_report(job, posts)

    history_id = None
    if req.save_history:
        item = append_history(req.job_input, report)
        history_id = item["id"]

    return {"report": asdict(report), "history_id": history_id}


@app.get("/api/samples")
def samples():
    return {"jobs": list(load_sample_posts().keys())}


@app.get("/api/history")
def history_list():
    history = list_history()
    return {
        "items": [
            {
                "id": item["id"],
                "job_input": item.get("job_input", ""),
                "created_at": item.get("created_at", ""),
                "confidence": item.get("report", {}).get("confidence", {}).get("overall", 0),
            }
            for item in history
        ]
    }


@app.get("/api/history/{history_id}")
def history_get(history_id: str):
    item = get_history_item(history_id)
    if item is None:
        raise HTTPException(status_code=404, detail="history not found")
    return item


@app.delete("/api/history/{history_id}")
def history_delete(history_id: str):
    ok = delete_history_item(history_id)
    if not ok:
        raise HTTPException(status_code=404, detail="history not found")
    return {"ok": True}


@app.get("/api/favorites")
def favorites_list():
    return {"items": list_favorites()}


@app.post("/api/favorites")
def favorites_add(req: FavoriteRequest):
    fav = add_favorite(req.history_id, req.note)
    if fav is None:
        raise HTTPException(status_code=404, detail="history not found")
    return fav


@app.delete("/api/favorites/{history_id}")
def favorites_delete(history_id: str):
    ok = remove_favorite(history_id)
    if not ok:
        raise HTTPException(status_code=404, detail="favorite not found")
    return {"ok": True}


@app.get("/api/export/{history_id}.json")
def export_json(history_id: str):
    item = get_history_item(history_id)
    if item is None:
        raise HTTPException(status_code=404, detail="history not found")

    filename = f"interview_report_{history_id}.json"
    return JSONResponse(
        content=item,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/api/export/{history_id}.md")
def export_markdown(history_id: str):
    item = get_history_item(history_id)
    if item is None:
        raise HTTPException(status_code=404, detail="history not found")

    content = report_to_markdown(item["report"])
    filename = f"interview_report_{history_id}.md"
    return PlainTextResponse(
        content=content,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        media_type="text/markdown; charset=utf-8",
    )


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>岗位定制化面试情报平台</title>
  <style>
    :root {
      --bg: #f5f0e8;
      --card: #fffdf9;
      --ink: #1e1e1e;
      --muted: #5d5d5d;
      --accent: #1f6f78;
      --accent-2: #f4b942;
      --line: #e8dfd2;
      --danger: #b42318;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background: radial-gradient(circle at 10% 10%, #fff6de, var(--bg));
      font-family: "PingFang SC", "Noto Sans SC", sans-serif;
    }
    .wrap {
      max-width: 1160px;
      margin: 24px auto 40px;
      padding: 0 16px;
    }
    .hero {
      background: linear-gradient(120deg, #0f4c5c, #1f6f78 55%, #2d8a95);
      color: #fff;
      padding: 24px;
      border-radius: 16px;
      box-shadow: 0 12px 28px rgba(0,0,0,.12);
    }
    .hero h1 { margin: 0 0 10px; font-size: 28px; }
    .hero p { margin: 0; opacity: .92; }
    .panel {
      margin-top: 16px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
    }
    .tool-row {
      margin-top: 10px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    input, button, select {
      border: 1px solid var(--line);
      border-radius: 10px;
      font-size: 15px;
      padding: 10px 12px;
    }
    .btn {
      background: var(--accent-2);
      border: none;
      color: #2f2500;
      font-weight: 700;
      cursor: pointer;
    }
    .btn-ghost {
      background: #fff7e2;
      border: 1px solid #f0d492;
      color: #5e4300;
      font-weight: 600;
      cursor: pointer;
    }
    .btn-danger {
      background: #ffe8e6;
      border: 1px solid #ffcbc6;
      color: var(--danger);
      font-weight: 600;
      cursor: pointer;
    }
    .grid {
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 12px;
    }
    .card {
      grid-column: span 12;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 4px 10px rgba(0,0,0,.03);
    }
    .card h2 {
      margin: 0 0 10px;
      font-size: 18px;
      color: var(--accent);
    }
    .cols-2 { grid-column: span 6; }
    .cols-4 { grid-column: span 4; }
    .cols-8 { grid-column: span 8; }
    .tag {
      display: inline-block;
      margin: 0 8px 8px 0;
      padding: 4px 8px;
      border-radius: 99px;
      background: #e8f6f7;
      color: #0f4c5c;
      font-size: 13px;
    }
    .muted { color: var(--muted); }
    .table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    .table th, .table td {
      border-bottom: 1px solid var(--line);
      text-align: left;
      padding: 8px 6px;
      vertical-align: top;
    }
    .freq-high { color: #b42318; font-weight: 700; }
    .freq-mid { color: #b54708; font-weight: 700; }
    .freq-low { color: #475467; }
    .history-item {
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px;
      margin-bottom: 8px;
      background: #fff;
      cursor: pointer;
    }
    .history-item:hover { border-color: #9dc6ca; }
    ul { margin: 8px 0 0 18px; }
    @media (max-width: 900px) {
      .cols-2, .cols-4, .cols-8 { grid-column: span 12; }
      .panel { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>岗位定制化面试情报平台</h1>
      <p>围绕目标岗位提炼小红书面经，不输出通用题库。</p>
      <div class="panel">
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <input id="jobInput" style="min-width:320px;flex:1;" placeholder="例如：美团商业分析实习" />
          <select id="sampleSelect"></select>
        </div>
        <button class="btn" id="runBtn">生成岗位报告</button>
      </div>
      <div class="tool-row">
        <button class="btn-ghost" id="favBtn">收藏当前报告</button>
        <button class="btn-ghost" id="exportJsonBtn">导出 JSON</button>
        <button class="btn-ghost" id="exportMdBtn">导出 Markdown</button>
      </div>
    </div>

    <div class="grid">
      <div class="card cols-4">
        <h2>历史记录</h2>
        <div id="historyList" class="muted">暂无</div>
      </div>
      <div class="card cols-4">
        <h2>收藏</h2>
        <div id="favoriteList" class="muted">暂无</div>
      </div>
      <div class="card cols-4">
        <h2>状态</h2>
        <div id="statusBox" class="muted">等待生成报告</div>
      </div>
    </div>

    <div id="report" class="grid"></div>
  </div>
<script>
let currentHistoryId = null;
let currentReport = null;

function escapeHtml(s) {
  return String(s || '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}

async function loadSamples() {
  const res = await fetch('/api/samples');
  const data = await res.json();
  const select = document.getElementById('sampleSelect');
  select.innerHTML = '<option value="">选择内置示例</option>' + data.jobs.map(j => `<option>${escapeHtml(j)}</option>`).join('');
  select.onchange = () => {
    if (select.value) document.getElementById('jobInput').value = select.value;
  };
}

function freqClass(freq) {
  if (freq === '高频') return 'freq-high';
  if (freq === '中频') return 'freq-mid';
  return 'freq-low';
}

function setStatus(msg) {
  document.getElementById('statusBox').textContent = msg;
}

function render(report) {
  currentReport = report;
  const el = document.getElementById('report');
  const job = report.target_job_info;
  const kws = report.recommended_search_keywords.groups;
  const confidence = report.confidence || {overall: 0, modules: {}, basis: []};

  const roundRows = report.interview_rounds.map(r => `
    <tr>
      <td>${escapeHtml(r.round_name)}</td>
      <td>${r.estimated_duration_minutes ? r.estimated_duration_minutes + '分钟' : '未明确'}</td>
      <td>${(r.focus || []).map(escapeHtml).join(' / ') || '待补充'}</td>
      <td>${r.inferred ? '根据面经与岗位特征推测' : '来自面经证据'}</td>
    </tr>
  `).join('');

  const qCards = report.high_frequency_questions.map(c => `
    <div class="card cols-2">
      <h2>${escapeHtml(c.category)} <span class="${freqClass(c.frequency)}">${escapeHtml(c.frequency)}</span></h2>
      <div class="muted">考察能力：${escapeHtml(c.assessed_capability)}</div>
      <ul>${(c.questions || []).map(q => `<li><span class="${freqClass(q.frequency)}">[${escapeHtml(q.frequency)}]</span> ${escapeHtml(q.question)}</li>`).join('')}</ul>
    </div>
  `).join('');

  const frameworkRows = report.answer_frameworks.map(f => `
    <tr><td>${escapeHtml(f.framework_name)}</td><td>${escapeHtml(f.when_to_use)}</td><td>${(f.steps || []).map(escapeHtml).join(' → ')}</td></tr>
  `).join('');

  const prepRows = report.preparation_suggestions.map(p => `
    <tr><td>${escapeHtml(p.priority)}</td><td>${escapeHtml(p.action)}</td><td>${escapeHtml(p.deliverable)}</td></tr>
  `).join('');

  const exampleRows = (report.example_answers || []).map(e => `
    <tr>
      <td>${escapeHtml(e.question)}</td>
      <td>${(e.answer_outline || []).map(escapeHtml).join(' → ')}</td>
      <td>${escapeHtml(e.caution)}</td>
    </tr>
  `).join('');

  const confRows = Object.entries(confidence.modules || {}).map(([k, v]) => `
    <tr><td>${escapeHtml(k)}</td><td>${escapeHtml(v)}</td></tr>
  `).join('');

  el.innerHTML = `
    <div class="card cols-8">
      <h2>1. 目标岗位信息</h2>
      <div><b>岗位名称：</b>${escapeHtml(job.position_name)}</div>
      <div><b>公司：</b>${escapeHtml(job.company)}</div>
      <div><b>岗位方向：</b>${escapeHtml(job.direction)}</div>
      <div><b>岗位类型：</b>${escapeHtml(job.role_type)}</div>
      <div><b>可能业务线：</b>${(job.possible_business_lines || []).map(escapeHtml).join(' / ')}</div>
      <div><b>核心能力要求：</b>${(job.core_capabilities || []).map(escapeHtml).join(' / ')}</div>
    </div>
    <div class="card cols-4">
      <h2>P2: 置信度</h2>
      <div><b>总体：</b>${escapeHtml(confidence.overall)}</div>
      <table class="table"><tbody>${confRows}</tbody></table>
      <div class="muted">${(confidence.basis || []).map(escapeHtml).join('；')}</div>
    </div>

    <div class="card cols-2">
      <h2>2. 推荐搜索关键词</h2>
      ${Object.entries(kws).map(([k, arr]) => `<div><b>${escapeHtml(k)}：</b>${(arr || []).map(x => `<span class='tag'>${escapeHtml(x)}</span>`).join('')}</div>`).join('')}
    </div>
    <div class="card cols-2">
      <h2>样本统计</h2>
      <div><b>输入：</b>${report.source_summary.input_posts} 条</div>
      <div><b>使用：</b>${report.source_summary.used_posts} 条</div>
      <div><b>剔除：</b>${report.source_summary.dropped_posts} 条</div>
      <div><b>问题：</b>${report.source_summary.unique_questions} 个去重问题</div>
    </div>

    <div class="card">
      <h2>3. 面试轮次信息</h2>
      <table class="table">
        <thead><tr><th>轮次</th><th>预计时长</th><th>考察重点</th><th>说明</th></tr></thead>
        <tbody>${roundRows}</tbody>
      </table>
    </div>

    <div class="card">
      <h2>4. 高频面试问题</h2>
      <div class="grid">${qCards || '<div class="muted">暂无足够问题证据，可补充更多面经文本。</div>'}</div>
    </div>

    <div class="card">
      <h2>5. 答题框架速查</h2>
      <table class="table">
        <thead><tr><th>框架</th><th>适用场景</th><th>步骤</th></tr></thead>
        <tbody>${frameworkRows}</tbody>
      </table>
    </div>

    <div class="card">
      <h2>6. 准备建议</h2>
      <table class="table">
        <thead><tr><th>优先级</th><th>动作</th><th>产出物</th></tr></thead>
        <tbody>${prepRows}</tbody>
      </table>
    </div>

    <div class="card">
      <h2>P2: 示例答案</h2>
      <table class="table">
        <thead><tr><th>问题</th><th>作答提纲</th><th>注意点</th></tr></thead>
        <tbody>${exampleRows || '<tr><td colspan="3" class="muted">暂无</td></tr>'}</tbody>
      </table>
    </div>
  `;
}

async function refreshHistory() {
  const res = await fetch('/api/history');
  const data = await res.json();
  const box = document.getElementById('historyList');
  if (!data.items.length) {
    box.innerHTML = '<div class="muted">暂无</div>';
    return;
  }
  box.innerHTML = data.items.map(i => `
    <div class="history-item" data-id="${i.id}">
      <div><b>${escapeHtml(i.job_input)}</b></div>
      <div class="muted">置信度 ${escapeHtml(i.confidence)} | ${escapeHtml(i.created_at)}</div>
      <div style="margin-top:6px;display:flex;gap:6px;">
        <button class="btn-ghost" onclick="loadFromHistory('${i.id}');event.stopPropagation();">打开</button>
        <button class="btn-danger" onclick="deleteHistory('${i.id}');event.stopPropagation();">删除</button>
      </div>
    </div>
  `).join('');
}

async function refreshFavorites() {
  const res = await fetch('/api/favorites');
  const data = await res.json();
  const box = document.getElementById('favoriteList');
  if (!data.items.length) {
    box.innerHTML = '<div class="muted">暂无</div>';
    return;
  }
  box.innerHTML = data.items.map(i => `
    <div class="history-item">
      <div><b>${escapeHtml(i.job_input)}</b></div>
      <div class="muted">${escapeHtml(i.created_at)}</div>
      <div style="margin-top:6px;display:flex;gap:6px;">
        <button class="btn-ghost" onclick="loadFromHistory('${i.history_id}');">打开</button>
        <button class="btn-danger" onclick="unfavorite('${i.history_id}');">取消收藏</button>
      </div>
    </div>
  `).join('');
}

async function run() {
  const jobInput = document.getElementById('jobInput').value.trim();
  if (!jobInput) return;
  setStatus('正在生成报告...');
  const res = await fetch('/api/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({job_input: jobInput, save_history: true})
  });
  const payload = await res.json();
  currentHistoryId = payload.history_id;
  render(payload.report);
  setStatus(`生成完成，history_id=${currentHistoryId}`);
  await refreshHistory();
}

async function loadFromHistory(id) {
  const res = await fetch(`/api/history/${id}`);
  if (!res.ok) return;
  const item = await res.json();
  currentHistoryId = id;
  render(item.report);
  setStatus(`已加载历史报告 ${id}`);
}

async function deleteHistory(id) {
  await fetch(`/api/history/${id}`, {method: 'DELETE'});
  if (currentHistoryId === id) {
    currentHistoryId = null;
    setStatus('当前报告已被删除');
  }
  await refreshHistory();
  await refreshFavorites();
}

async function favoriteCurrent() {
  if (!currentHistoryId) {
    setStatus('请先生成或打开一份报告');
    return;
  }
  const res = await fetch('/api/favorites', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({history_id: currentHistoryId})
  });
  if (res.ok) {
    setStatus('已收藏当前报告');
    await refreshFavorites();
  }
}

async function unfavorite(id) {
  await fetch(`/api/favorites/${id}`, {method: 'DELETE'});
  await refreshFavorites();
}

function exportJson() {
  if (!currentHistoryId) {
    setStatus('请先生成或打开一份报告');
    return;
  }
  window.open(`/api/export/${currentHistoryId}.json`, '_blank');
}

function exportMarkdown() {
  if (!currentHistoryId) {
    setStatus('请先生成或打开一份报告');
    return;
  }
  window.open(`/api/export/${currentHistoryId}.md`, '_blank');
}

document.getElementById('runBtn').onclick = run;
document.getElementById('favBtn').onclick = favoriteCurrent;
document.getElementById('exportJsonBtn').onclick = exportJson;
document.getElementById('exportMdBtn').onclick = exportMarkdown;

loadSamples();
refreshHistory();
refreshFavorites();
</script>
</body>
</html>
"""
