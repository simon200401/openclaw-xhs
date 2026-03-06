# 岗位定制化面试情报平台 (MVP)

这是一个围绕**具体岗位**提炼小红书面经的分析工具，不输出通用题库。

## 目标
- 输入岗位（如：`美团商业分析实习`）
- 自动完成岗位解析、关键词生成、内容筛选、问题提炼、轮次推断
- 输出结构化报告（6大模块）

## 已实现能力
- P0
  - 岗位解析：公司、岗位方向、岗位类型、可能业务线、核心能力
  - 搜索词生成：岗位词/公司词/面经词/轮次词/能力词/组合词
  - 内容筛选：剔除广告、低信息量、重复问题标准化
  - 高频问题提炼：岗位相关分类 + 频率等级 + 能力映射
  - 岗位定制化报告输出：固定6模块
- P1
  - 面试轮次推断：证据不足时标注“根据面经与岗位特征推测”
  - 答题框架速查：按岗位类型输出，不走通用模板
  - 准备建议：按优先级给可执行动作和产出物
  - 结果页优化：分析报告风格，移动端可读
- P2
  - 示例答案：按岗位相关题型给作答提纲与注意点
  - 收藏：支持收藏历史报告
  - 导出：支持 JSON / Markdown 导出
  - 历史记录：自动保存最近 50 条分析结果
  - 置信度展示：模块级分数 + 总体分 + 依据

## 运行
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
打开 `http://127.0.0.1:8000`

## 上线部署（Render）
1. 把本项目上传到 GitHub 仓库（Render 通过 Git 拉取部署）。
2. 在 Render 新建 `Blueprint`，选择仓库根目录的 `render.yaml`。
3. 点击部署，等待构建完成后访问分配的 `onrender.com` 域名。
4. 健康检查地址：`/healthz`

已提供部署文件：
- `render.yaml`
- `Dockerfile`
- `.dockerignore`

注意：
- 当前历史/收藏使用 `data/user_state.json` 本地文件存储；在云端免费实例重启或重建后可能丢失。
- 若需要持久化，建议下一步接入 SQLite/PostgreSQL。

## 测试
```bash
pytest -q
```

## API
- `POST /api/analyze`
  - 入参：
```json
{
  "job_input": "美团商业分析实习",
  "posts": [],
  "save_history": true
}
```
  - `posts` 为空时会用内置示例数据（`data/sample_xhs_posts.json`）
  - 返回 `report` 与 `history_id`
- `GET /api/history`：查询历史列表
- `GET /api/history/{history_id}`：读取历史详情
- `DELETE /api/history/{history_id}`：删除历史
- `GET /api/favorites`：查询收藏
- `POST /api/favorites`：新增收藏
- `DELETE /api/favorites/{history_id}`：取消收藏
- `GET /api/export/{history_id}.json`：导出 JSON
- `GET /api/export/{history_id}.md`：导出 Markdown

## 目录
- `app/main.py`：FastAPI + 报告页面
- `src/role_parser.py`：岗位解析
- `src/query_builder.py`：检索词生成
- `src/extractor.py`：内容抽取、筛选、去重、分类
- `src/report_generator.py`：轮次推断、框架、准备建议、报告拼装
- `src/exporter.py`：Markdown 导出
- `src/state_store.py`：历史与收藏本地存储
- `src/rules.py`：岗位自适应规则库
- `data/sample_xhs_posts.json`：示例面经数据
- `data/user_state.json`：本地历史与收藏数据
- `tests/test_pipeline.py`：岗位差异化与推断标注测试
- `tests/test_p2.py`：P2 功能测试
