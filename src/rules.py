ROLE_PROFILES = {
    "business_analyst": {
        "aliases": ["商业分析", "商分", "数据分析", "商业分析师", "business analyst", "data analyst"],
        "direction": "商业分析/数据分析",
        "business_lines": ["增长分析", "交易转化", "供给运营", "用户生命周期"],
        "capabilities": ["SQL", "指标体系", "业务拆解", "异动分析", "AB测试", "项目量化复盘"],
        "focus_categories": ["SQL题", "指标与异动分析", "Case拆解", "项目深挖", "AB测试"],
        "query_tokens": ["SQL", "指标", "分析题", "case", "AB测试", "面试复盘"],
        "frameworks": ["SQL题", "异动分析题", "项目题", "AB测试题", "Case题"],
    },
    "strategy_product": {
        "aliases": ["策略产品", "策略pm", "策略", "growth pm", "strategy product"],
        "direction": "策略产品/增长策略",
        "business_lines": ["增长策略", "供需匹配", "商业化策略", "平台治理策略"],
        "capabilities": ["策略拆解", "增长逻辑", "业务分析", "实验设计", "跨团队推进"],
        "focus_categories": ["策略拆解", "增长Case", "供需匹配", "实验设计", "项目推进"],
        "query_tokens": ["策略题", "增长", "供需", "实验设计", "面经", "业务分析"],
        "frameworks": ["策略拆解题", "增长分析题", "实验设计题", "项目推进题"],
    },
    "ai_product": {
        "aliases": ["ai产品", "算法产品", "llm产品", "agent产品", "aigc产品", "ai pm"],
        "direction": "AI产品",
        "business_lines": ["智能助手", "内容生成", "搜索问答", "企业智能化"],
        "capabilities": ["场景抽象", "模型能力边界", "RAG/Agent设计", "评估与迭代", "安全与成本权衡"],
        "focus_categories": ["场景设计", "模型边界", "RAG/Agent", "评估方法", "产品策略"],
        "query_tokens": ["大模型", "RAG", "Agent", "评估", "Prompt", "面经"],
        "frameworks": ["场景设计题", "模型边界题", "RAG方案题", "评估题"],
    },
    "product_manager": {
        "aliases": ["产品经理", "pm", "产品岗", "product manager"],
        "direction": "产品经理",
        "business_lines": ["用户增长", "交易产品", "内容产品", "平台产品"],
        "capabilities": ["需求分析", "产品思维", "业务理解", "项目推进", "用户价值判断"],
        "focus_categories": ["需求分析", "产品设计", "业务场景", "项目推进", "用户价值"],
        "query_tokens": ["需求分析", "产品设计", "场景题", "项目经历", "面经"],
        "frameworks": ["需求分析题", "产品设计题", "项目推进题", "优先级题"],
    },
    "generic": {
        "aliases": [],
        "direction": "通用岗位",
        "business_lines": ["待识别"],
        "capabilities": ["岗位核心能力待补充"],
        "focus_categories": ["项目经历", "岗位能力", "业务理解"],
        "query_tokens": ["面经", "面试题", "复盘"],
        "frameworks": ["项目题"],
    },
}

COMPANY_TOKENS = [
    "美团",
    "快手",
    "字节",
    "阿里",
    "腾讯",
    "京东",
    "小红书",
    "拼多多",
    "滴滴",
    "百度",
]

ROUND_PATTERNS = {
    "一面": ["一面", "第一轮", "初面", "组面", "hr筛"],
    "二面": ["二面", "第二轮", "复面", "主管面"],
    "三面": ["三面", "第三轮", "总监面", "交叉面"],
    "HR面": ["hr面", "hrbp", "hr终面", "文化面"],
}

AD_PATTERNS = [
    "加v",
    "私我",
    "代投",
    "内推有偿",
    "课程",
    "训练营",
    "付费咨询",
    "广告",
    "推广",
]

LOW_INFO_PATTERNS = [
    "上岸了",
    "求好运",
    "太难了",
    "已过",
    "打卡",
]

QUESTION_HINTS = [
    "为什么",
    "怎么",
    "如何",
    "请你",
    "举例",
    "给你一个",
    "写SQL",
    "设计",
    "分析",
    "case",
    "ab测试",
    "指标",
]

DURATION_PATTERNS = ["分钟", "min", "mins"]
