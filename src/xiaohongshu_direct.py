"""
小红书搜索 - 使用 Playwright 直接访问。
设计目标：小红书能力不可用时，不影响主流程（返回空结果并由上层回退）。
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from playwright.async_api import async_playwright  # type: ignore
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    async_playwright = None  # type: ignore
    PLAYWRIGHT_AVAILABLE = False


DEFAULT_COOKIES_PATH = Path(__file__).resolve().parent.parent / "cookies" / "cookies.json"
COOKIES_PATH = Path(os.getenv("XHS_COOKIES_PATH", str(DEFAULT_COOKIES_PATH)))
COOKIES_JSON_ENV = "XHS_COOKIES_JSON"


def _load_cookies() -> tuple[List[Dict[str, Any]], str, str]:
    """
    加载 cookies。
    优先级：环境变量 XHS_COOKIES_JSON > 文件 XHS_COOKIES_PATH。
    """
    raw_json = os.getenv(COOKIES_JSON_ENV, "").strip()
    if raw_json:
        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed, list):
                cookies = [c for c in parsed if isinstance(c, dict)]
                return cookies, "env", ""
            return [], "env", "XHS_COOKIES_JSON 不是数组格式"
        except Exception as exc:
            return [], "env", f"XHS_COOKIES_JSON 解析失败: {exc}"

    try:
        if COOKIES_PATH.exists():
            with COOKIES_PATH.open("r", encoding="utf-8") as f:
                parsed = json.load(f)
            if isinstance(parsed, list):
                cookies = [c for c in parsed if isinstance(c, dict)]
                return cookies, "file", ""
            return [], "file", f"cookies 文件格式错误: {COOKIES_PATH}"
        return [], "file", f"cookies 文件不存在: {COOKIES_PATH}"
    except Exception as exc:
        return [], "file", str(exc)


async def search_xiaohongshu(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """使用 Playwright 搜索小红书，失败时返回空列表。"""
    if not PLAYWRIGHT_AVAILABLE:
        print("[XHS] Playwright 未安装，跳过实时搜索")
        return []

    cookies, cookies_source, cookie_error = _load_cookies()
    print(f"[XHS] cookies loaded: {len(cookies)} from {cookies_source}")
    if cookie_error:
        print(f"[XHS] cookies 提示: {cookie_error}")

    results: List[Dict[str, Any]] = []
    try:
        async with async_playwright() as p:  # type: ignore[misc]
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            )

            if cookies:
                try:
                    await context.add_cookies(cookies)
                except Exception as exc:
                    print(f"[XHS] cookies 注入失败: {exc}")

            page = await context.new_page()
            try:
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
                await page.goto(search_url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(4000)

                js = """() => {
                    const notes = [];
                    const selectors = [
                      'section.note-item',
                      'div.note-item',
                      'a[href*="/explore/"]',
                      '[class*="feeds-page"] a',
                      '[class*="note-item"]'
                    ];
                    for (const selector of selectors) {
                      document.querySelectorAll(selector).forEach(item => {
                        if (notes.length >= 20) return;
                        const link = item.tagName === 'A' ? item : item.querySelector('a[href*="/explore/"]');
                        if (!link) return;
                        const href = link.getAttribute('href');
                        if (!href || !href.includes('/explore/')) return;
                        const noteId = href.match(/\\/explore\\/([a-z0-9]+)/i)?.[1];
                        if (notes.some(n => n.noteId === noteId)) return;
                        const titleEl = item.querySelector('.title, h3, h4, [class*="title"]') || link;
                        const title = titleEl.innerText?.trim() || '';
                        if (title.length < 5) return;
                        if (/课程|培训|辅导|加群|私信|资料包|免费领|代购|广告/.test(title)) return;
                        const authorEl = item.querySelector('.author, [class*="author"]');
                        const likeEl = item.querySelector('.like, [class*="count"]');
                        notes.push({
                          title: title.substring(0, 100),
                          url: href.startsWith('http') ? href : 'https://www.xiaohongshu.com' + href,
                          author: authorEl ? authorEl.innerText.trim() : '',
                          likes: likeEl ? likeEl.innerText.trim() : '',
                          noteId: noteId || '',
                          content: ''
                        });
                      });
                    }
                    return notes;
                }"""
                raw = await page.evaluate(js)
                results = raw[: max(1, min(limit, 20))] if isinstance(raw, list) else []

                for note in results[: min(3, len(results))]:
                    note_id = note.get("noteId", "")
                    if note_id:
                        detail = await get_note_detail(page, note_id)
                        if detail:
                            note["content"] = detail.get("content", "")[:1000]
                            if detail.get("title"):
                                note["title"] = detail["title"]
            except Exception as exc:
                print(f"[XHS] 搜索异常: {exc}")
            finally:
                await browser.close()
    except Exception as exc:
        print(f"[XHS] Playwright 启动失败: {exc}")
        return []

    return results


async def get_note_detail(page, note_id: str) -> Optional[Dict[str, str]]:
    """获取笔记详情。"""
    try:
        url = f"https://www.xiaohongshu.com/explore/{note_id}"
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1500)

        return await page.evaluate(
            """() => {
            const title = document.querySelector('h1, .title, [class*="title"]')?.innerText?.trim() || '';
            const content = document.querySelector('.content, .desc, [class*="content"], [class*="desc"], article')?.innerText?.trim() || '';
            return { title, content };
        }"""
        )
    except Exception:
        return None


def transform_posts_for_platform(raw_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """转换为平台统一格式。"""
    return [
        {
            "title": post.get("title", ""),
            "content": post.get("content", ""),
            "source": "xiaohongshu",
            "url": post.get("url", ""),
            "author": post.get("author", ""),
            "metrics": {"likes": post.get("likes", "")},
        }
        for post in raw_posts
    ]


async def check_status() -> Dict[str, Any]:
    """检查小红书能力状态，始终返回结构化结果。"""
    cookies, cookies_source, cookie_error = _load_cookies()
    cookies_loaded = len(cookies) > 0
    cookies_count = len(cookies)
    has_web_session = any(c.get("name") == "web_session" for c in cookies)

    return {
        "playwright_available": PLAYWRIGHT_AVAILABLE,
        "cookies_loaded": cookies_loaded,
        "cookies_count": cookies_count,
        "has_web_session": has_web_session,
        "cookies_source": cookies_source,
        "cookies_path": str(COOKIES_PATH),
        "error": cookie_error,
    }
