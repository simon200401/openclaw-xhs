"""小红书数据源接入模块。"""
from typing import Any, Dict

# 从直接搜索模块导入所有功能
from .xiaohongshu_direct import (
    search_xiaohongshu,
    transform_posts_for_platform,
    check_status
)

async def check_mcp_status() -> Dict[str, Any]:
    """检查小红书连接状态"""
    status = await check_status()
    return {
        "success": True,
        "data": {
            "is_logged_in": status.get("has_web_session", False) and status.get("playwright_available", False),
            "username": "xiaohongshu",
            "cookies_count": status.get("cookies_count", 0),
            "playwright_available": status.get("playwright_available", False),
            "cookies_loaded": status.get("cookies_loaded", False),
            "cookies_source": status.get("cookies_source", "unknown"),
            "error": status.get("error", ""),
        }
    }

__all__ = [
    'search_xiaohongshu',
    'transform_posts_for_platform', 
    'check_mcp_status'
]
