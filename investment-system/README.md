# 每日荐股分析项目

> 基于AI的持续学习投资分析系统  
> 创建时间：2026-04-01  
> 维护者：小龙虾AI助手 🦞

---

## 📋 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [目录结构](#目录结构)
- [核心模块](#核心模块)
- [知识库建设](#知识库建设)
- [模型设计](#模型设计)
- [数据采集](#数据采集)
- [定时任务](#定时任务)
- [产出物](#产出物)
- [使用指南](#使用指南)
- [风险提示](#风险提示)

---

## 项目简介

### 项目定位

**每日荐股分析**是一个基于AI的持续学习投资分析系统，通过采集国内外财经新闻、研报、市场数据，结合历史知识库，为用户提供开盘前的预见性操盘建议。

### 核心理念

```
持续学习 → 智能分析 → 预见性判断 → 反馈优化
```

### 项目目标

- ✅ **预见性**：开盘前给出操盘建议，而非收盘后总结
- ✅ **可操作**：明确仓位、建仓时机、止损止盈策略
- ✅ **自学习**：持续积累知识，优化预测模型
- ✅ **闭环性**：预测→验证→优化，形成正反馈

---

## 核心特性

### 1. 多源数据采集

**国内新闻**：
- 财联社（24小时滚动新闻）
- 新浪财经（综合财经资讯）
- 巨潮资讯网（官方公告）
- 东方财富网（行情+资讯）

**海外新闻**（容错机制）：
- BBC News、CNN、Reuters（时政）
- Wall Street Journal、Bloomberg、CNBC（财经）
- Financial Times、The Economist（深度分析）

**股票数据**：
- 东方财富API（免费实时行情）
- 2000只股票实时数据
- PE/PB/换手率/涨跌幅等指标

### 2. 智能分析引擎

**新闻分析**：
- 自动分类（宏观/政策/行业/市场/公司）
- 情绪识别（利好/利空/中性）
- 关键词提取
- 关联股票识别

**股票筛选**：
- 多因子模型（基本面+技术面）
- PE区间筛选（5-100倍）
- 换手率筛选（0.01%-50%）
- 综合评分排序

**模式识别**：
- 情绪趋势追踪
- 板块轮动分析
- 历史相似场景匹配

### 3. 闭环学习机制

```
┌──────────────────────────────────────────┐
│       每日闭环流程                         │
├──────────────────────────────────────────┤
│                                          │
│  1. 验证昨日预测 → 计算准确率              │
│  2. 加载历史知识 → 趋势/模式/准确率         │
│  3. 分析市场模式 → 情绪趋势/板块轮动        │
│  4. 生成智能建议 → 动态置信度/风险评级      │
│  5. 记录预测结果 → 用于明日验证            │
│  6. 优化模型参数 → 持续改进                │
│                                          │
└──────────────────────────────────────────┘
```

### 4. 动态置信度系统

- **初始置信度**：50%（无历史数据）
- **自动调整**：根据历史准确率动态调整
- **上限保护**：最高85%（避免过度自信）
- **仓位联动**：置信度→仓位建议

| 置信度 | 风险等级 | 建议仓位 | 操作策略 |
|--------|---------|---------|---------|
| >70% | Low | 60-70% | 积极参与 |
| 50-70% | Medium | 40-50% | 谨慎参与 |
| <50% | High | 20-30% | 观望为主 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                每日荐股分析系统                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  数据采集层  │  │  智能分析层  │  │  输出层    │ │
│  └─────────────┘  └─────────────┘  └────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │            知识库 + 反馈学习                   │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 数据流

```
[新闻/研报/行情] 
    ↓
[数据采集] → [智能分类] → [情感分析]
    ↓
[知识归档] → [模式识别] → [趋势追踪]
    ↓
[历史知识库]
    ↓
[股票筛选] → [评分计算] → [置信度调整]
    ↓
[操盘建议] → [记录预测]
    ↓
[次日验证] → [计算准确率] → [优化模型]
    ↓
[反馈学习] ──────────→ [历史知识库]
```

---

## 目录结构

```
/Users/glenman/.openclaw/workspace/
│
├── investment-system/                    # 项目主目录
│   │
│   ├── README.md                         # 本文档
│   ├── config.json                       # 系统配置
│   ├── knowledge_system_design.md        # 知识系统设计文档
│   │
│   ├── # === 核心运行脚本 ===
│   ├── run_integrated_system.py          # 整合版系统（推荐）⭐
│   ├── run_daily_closed_loop.sh          # 闭环脚本 ⭐
│   ├── run_pre_market_quick.py           # 快速版（备用）
│   ├── run_daily_analysis.py             # 学习系统
│   │
│   ├── # === 数据采集模块 ===
│   ├── data_collectors/
│   │   ├── news_fetcher.py               # 国内新闻采集
│   │   ├── global_news_fetcher.py        # 海外新闻采集（容错）
│   │   └── stock_data_fetcher.py         # 股票数据采集
│   │
│   ├── # === 分析模型模块 ===
│   ├── models/
│   │   ├── knowledge_analyzer.py         # 知识分析器
│   │   ├── pre_market_advisor.py         # 操盘建议生成器
│   │   ├── feedback_learner.py           # 反馈学习器 ⭐
│   │   └── daily_report.py               # 日报生成器
│   │
│   └── # === 模板文件 ===
│       └── templates/
│           └── daily_report.md           # 报告模板
│
├── memory/                               # 数据存储目录
│   └── investment/
│       │
│       ├── # === 每日数据 ===
│       ├── daily/
│       │   ├── integrated_advice_*.md       # 整合版建议 ⭐
│       │   ├── feedback_report_*.json       # 反馈报告 ⭐
│       │   ├── pre_market_advice_*.md       # 操盘建议
│       │   ├── screened_stocks_*.csv        # 筛选结果
│       │   ├── news_*.json                  # 国内新闻
│       │   ├── global_news_*.json           # 海外新闻
│       │   ├── daily_report_*.md            # 分析报告
│       │   └── learning_*.md                # 学习记录
│       │
│       ├── # === 知识库 ===
│       ├── knowledge/
│       │   │
│       │   ├── # 新闻归档（按月+主题）
│       │   ├── news_archive/
│       │   │   └── 2026-04/
│       │   │       ├── macro_2026-04-01.json    # 宏观经济
│       │   │       ├── policy_2026-04-01.json   # 政策解读
│       │   │       ├── industry_2026-04-01.json # 行业动态
│       │   │       ├── market_2026-04-01.json   # 市场情绪
│       │   │       └── company_2026-04-01.json  # 公司新闻
│       │   │
│       │   ├── # 研报归档
│       │   ├── reports_archive/
│       │   │   └── 2026-04/
│       │   │       ├── industry/           # 行业研报
│       │   │       ├── company/            # 个股研报
│       │   │       └── strategy/           # 策略研报
│       │   │
│       │   ├── # 趋势分析
│       │   ├── trends/
│       │   │   ├── daily_trends.json       # 每日趋势 ⭐
│       │   │   ├── sector_rotation.md      # 板块轮动
│       │   │   └── market_sentiment.md     # 市场情绪
│       │   │
│       │   ├── # 模式库
│       │   ├── patterns/
│       │   │   ├── breakout_patterns.md    # 突破形态
│       │   │   ├── reversal_patterns.md    # 反转形态
│       │   │   └── accumulation.md         # 吸筹模式
│       │   │
│       │   ├── # 个股研究
│       │   ├── stock_analysis/
│       │   │   ├── 300149_睿智医药.md
│       │   │   └── ...
│       │   │
│       │   ├── # 行业研究
│       │   ├── industry_analysis/
│       │   │   ├── 医药行业.md
│       │   │   ├── 新能源.md
│       │   │   └── ...
│       │   │
│       │   └── feedback_history.json       # 反馈历史 ⭐
│       │
│
├── HEARTBEAT.md                          # 心跳任务配置
├── MEMORY.md                             # 长期记忆
└── AGENTS.md                             # 工作空间说明

```

---

## 核心模块

### 1. 数据采集模块

#### news_fetcher.py - 国内新闻采集
**功能**：
- 多源新闻采集（财联社、新浪、巨潮）
- 自动重试机制
- 统一数据格式

**输出**：
```json
{
  "title": "三大指数均涨超1%，医药板块持续爆发",
  "source": "财联社",
  "url": "https://...",
  "fetch_time": "2026-04-01 08:30:00"
}
```

**使用**：
```python
from data_collectors.news_fetcher import MultiSourceNewsFetcher
fetcher = MultiSourceNewsFetcher()
news = fetcher.fetch_all_news(max_per_source=20)
```

#### global_news_fetcher.py - 海外新闻采集
**功能**：
- 海外媒体采集（BBC、CNN、WSJ等）
- 容错机制（失败不影响整体）
- 时政+财经分类

**特点**：
- 超时控制（8秒）
- 静默失败
- 降级处理

#### stock_data_fetcher.py - 股票数据采集
**功能**：
- 东方财富API接口
- 2000只股票实时行情
- 多因子筛选

**筛选条件**：
- PE：5-100倍
- 换手率：0.01%-50%
- 排除ST、停牌
- 综合评分排序

### 2. 智能分析模块

#### knowledge_analyzer.py - 知识分析器
**功能**：
- 新闻自动分类（5类）
- 情绪分析（3级）
- 关键词提取
- 知识归档

**分类规则**：
```python
category_rules = {
    'macro': ['央行', 'GDP', 'CPI', '利率', '货币政策'],
    'policy': ['政策', '国务院', '发改委', '监管'],
    'industry': ['行业', '板块', '产业链', '供需'],
    'market': ['指数', '涨跌', '涨停', '资金', '北向'],
    'company': ['公司', '业绩', '财报', '盈利', '亏损']
}
```

**情绪分析**：
```python
sentiment_keywords = {
    'positive': ['涨', '增', '突破', '利好', '爆发'],
    'negative': ['跌', '降', '亏损', '利空', '暴跌'],
    'neutral': ['公布', '显示', '报告', '称', '表示']
}
```

#### pre_market_advisor.py - 操盘建议生成器
**功能**：
- 加载历史知识库
- 分析市场模式
- 生成智能推荐
- 动态置信度调整

**输出格式**：
```markdown
## 💡 智能推荐股票（结合历史模式）

1. **300149 睿智医药** - 调整评分:10.4 置信度:50.0% 风险:high
2. **301392 汇成真空** - 调整评分:10.4 置信度:50.0% 风险:high

## 🎯 操作建议（基于置信度）

- **建议仓位**: 40-50%
- **置信度**: 中
- **策略**: 谨慎参与
```

#### feedback_learner.py - 反馈学习器
**功能**：
- 验证昨日预测
- 计算准确率
- 分析预测模式
- 优化模型参数

**验证逻辑**：
- 获取昨日推荐股票
- 获取今日实际涨跌幅
- 涨幅>3%视为成功
- 计算准确率

### 3. 运行脚本

#### run_integrated_system.py - 整合版系统 ⭐
**推荐使用**

**流程**：
1. 加载历史知识库
2. 采集今日新闻
3. 智能分析新闻
4. 分析市场模式
5. 筛选优质股票
6. 生成智能推荐

**输出**：
- `integrated_advice_YYYY-MM-DD.md`（整合版建议）
- 包含历史知识分析
- 包含动态置信度
- 包含风险评级

#### run_daily_closed_loop.sh - 闭环脚本 ⭐
**完整闭环**

**流程**：
1. 验证昨日预测
2. 生成今日建议
3. 知识归档

**特点**：
- 完整闭环
- 自动反馈
- 持续学习

---

## 知识库建设

### 1. 知识库结构

```
knowledge/
├── news_archive/          # 新闻归档（按月+主题）
│   └── 2026-04/
│       ├── macro_*.json       # 宏观经济
│       ├── policy_*.json      # 政策解读
│       ├── industry_*.json    # 行业动态
│       ├── market_*.json      # 市场情绪
│       └── company_*.json     # 公司新闻
│
├── trends/                # 趋势分析
│   ├── daily_trends.json      # 每日趋势指标
│   ├── sector_rotation.md     # 板块轮动
│   └── market_sentiment.md    # 市场情绪
│
├── patterns/              # 模式库
│   ├── breakout_patterns.md   # 突破形态
│   └── reversal_patterns.md   # 反转形态
│
└── feedback_history.json  # 反馈历史 ⭐
```

### 2. 知识积累方式

**每日自动归档**：
```python
# 1. 采集新闻
news = fetcher.fetch_all_news()

# 2. 智能分类
for item in news:
    category = classify_news(item)  # macro/policy/industry/market/company
    sentiment = analyze_sentiment(item)  # positive/negative/neutral
    keywords = extract_keywords(item)

# 3. 归档到知识库
save_to_knowledge_base(category, item)

# 4. 更新趋势指标
update_trends(sentiment_score, hot_topics)
```

**趋势追踪**：
```json
{
  "2026-04-01": {
    "news_count": 49,
    "sentiment_score": 0.08,
    "hot_topics": [
      ["医药", 15],
      ["科技", 12],
      ["新能源", 8]
    ]
  }
}
```

**反馈积累**：
```json
{
  "2026-04-01": {
    "predictions": [
      {
        "stock": "300149",
        "predicted": "上涨",
        "actual": "+5.2%",
        "success": true
      }
    ],
    "accuracy": 0.75
  }
}
```

### 3. 知识库应用

**历史知识加载**：
```python
# 加载最近7天趋势
trends = load_recent_trends(days=7)

# 计算情绪趋势
avg_sentiment = calculate_average(trends, 'sentiment_score')
recent_sentiment = trends[-1]['sentiment_score']

if recent_sentiment > avg_sentiment + 0.1:
    sentiment_trend = 'improving'
elif recent_sentiment < avg_sentiment - 0.1:
    sentiment_trend = 'declining'
else:
    sentiment_trend = 'stable'
```

**置信度调整**：
```python
# 加载反馈历史
feedback = load_feedback_history()

if feedback:
    accuracy = calculate_accuracy(feedback)
    confidence = min(accuracy, 0.85)  # 最高85%
else:
    confidence = 0.5  # 初始值50%
```

---

## 模型设计

### 1. 新闻分析模型

**分类模型**：
- 基于关键词规则
- 5大类别（宏观/政策/行业/市场/公司）
- 自动归档

**情感模型**：
- 关键词匹配
- 3级情感（positive/negative/neutral）
- 量化评分（-1到+1）

**关联模型**：
- 股票代码识别（正则匹配）
- 行业关键词匹配
- 板块关联

### 2. 股票筛选模型

**多因子模型**：
```python
筛选流程：
1. 过滤ST股票
2. 过滤停牌（涨跌幅=0）
3. 过滤极端波动（涨跌幅>10%）
4. PE筛选（5-100倍）
5. 换手率筛选（0.01%-50%）
6. 综合评分排序
```

**评分模型**：
```python
score = 0

# 涨跌幅权重（40%）
score += min(max(涨跌幅, 0), 5) * 2  # 最高10分

# 换手率权重（30%）
turnover_score = 10 - abs(换手率 - 3)  # 3%最优
score += min(max(turnover_score, 0), 5)

# 市盈率权重（30%）
pe_score = 10 - abs(市盈率 - 20) / 5  # 20倍最优
score += min(max(pe_score, 0), 5)
```

**调整评分**（结合历史）：
```python
adjusted_score = base_score

# 情绪趋势加分
if sentiment_trend == 'improving':
    adjusted_score += 0.5
elif sentiment_trend == 'declining':
    adjusted_score -= 0.3

# 置信度调整
confidence = historical_accuracy
```

### 3. 置信度模型

**动态置信度**：
```python
if 历史准确率 >= 70%:
    confidence = min(准确率, 85%)
    risk_level = 'low'
    position = '60-70%'
    
elif 历史准确率 >= 50%:
    confidence = 准确率
    risk_level = 'medium'
    position = '40-50%'
    
else:
    confidence = 准确率
    risk_level = 'high'
    position = '20-30%'
```

### 4. 反馈学习模型

**验证逻辑**：
```python
for prediction in yesterday_predictions:
    actual_return = get_actual_return(prediction['stock'])
    
    if actual_return > 3%:
        prediction['success'] = True
    else:
        prediction['success'] = False

accuracy = successful_count / total_count
```

**优化建议**：
```python
# 分析成功预测的特征
successful_features = analyze_successful_predictions()

# 生成优化建议
if 'low_pe' in successful_features:
    suggestions.append('PE区间优化: 建议调整为8-50倍')

if 'high_turnover' in successful_features:
    suggestions.append('换手率权重提升: 当前30% → 建议40%')
```

---

## 数据采集

### 1. 国内新闻采集

**数据源**：
| 渠道 | URL | 采集量 | 状态 |
|------|-----|--------|------|
| 财联社 | https://www.cls.cn | 20条/日 | ✅ 稳定 |
| 新浪财经 | https://finance.sina.com.cn | 20条/日 | ✅ 稳定 |
| 巨潮资讯网 | http://www.cninfo.com.cn | 10条/日 | ✅ 稳定 |

**采集时间**：每日8:00-8:30

**采集方式**：
- urllib（无需外部依赖）
- 超时控制（15秒）
- 失败重试（3次）

**数据格式**：
```json
{
  "title": "新闻标题",
  "source": "财联社",
  "url": "https://...",
  "fetch_time": "2026-04-01 08:30:00"
}
```

### 2. 海外新闻采集

**数据源**：
| 类型 | 渠道 | URL | 状态 |
|------|------|-----|------|
| 时政 | BBC News | https://www.bbc.com/news | ⚠️ 容错 |
| 时政 | CNN | https://edition.cnn.com | ⚠️ 容错 |
| 时政 | Reuters | https://www.reuters.com | ⚠️ 容错 |
| 财经 | WSJ | https://www.wsj.com | ⚠️ 容错 |
| 财经 | Bloomberg | https://www.bloomberg.com | ⚠️ 容错 |
| 财经 | CNBC | https://www.cnbc.com | ⚠️ 容错 |

**容错机制**：
- 超时控制（8秒）
- 静默失败（不打印错误）
- 失败不影响整体

### 3. 股票数据采集

**数据源**：
- 东方财富API（免费）
- URL: https://push2.eastmoney.com/api/qt/clist/get

**采集内容**：
- 股票代码、名称
- 最新价、涨跌幅、涨跌额
- 成交量、成交额
- 换手率、量比
- 市盈率、市净率
- 最高、最低、今开、昨收

**采集限制**：
- 每次最多3000只
- 非交易时间显示上一交易日数据

### 4. 研报采集（待优化）

**数据源**：
- 东方财富研报中心
- 新浪财经研报
- 中财网研报

**当前状态**：⏸️ 暂停（网页解析复杂）

**替代方案**：
- 新闻中提取研报相关内容
- 后续可考虑API接入

---

## 定时任务

### 每日荐股分析 ⭐

**执行时间**：每日8:30-9:00（开盘前）

**执行脚本**：`run_integrated_system.py`

**执行逻辑**：
1. ✅ 验证昨日预测（反馈学习）
2. ✅ 加载历史知识库（趋势、准确率）
3. ✅ 采集国内外新闻
4. ✅ 智能分析（分类、情感、关键词）
5. ✅ 分析市场模式（情绪趋势）
6. ✅ 筛选优质股票（多因子）
7. ✅ 生成智能推荐（动态置信度）
8. ✅ 记录预测结果（用于次日验证）
9. ✅ 知识归档（持续积累）

**产出物**：
- `integrated_advice_*.md`（整合版建议）
- `feedback_report_*.json`（反馈报告）
- `screened_stocks_*.csv`（筛选结果）
- `news_archive/*`（新闻归档）
- `daily_trends.json`（趋势数据）

**状态**：✅ 每日自动运行

---

## 产出物

### 每日产出

#### 1. 整合版操盘建议 ⭐
**文件**：`memory/investment/daily/integrated_advice_YYYY-MM-DD.md`

**内容**：
- 历史知识分析（准确率、情绪趋势）
- 今日关键新闻（前5条）
- 智能推荐股票（TOP5，含置信度）
- 操作建议（仓位、策略）
- 风险提示

**示例**：
```markdown
## 📚 历史知识分析
- 历史准确率: 68%
- 情绪趋势: improving
- 预测置信度: 68.0%

## 💡 智能推荐股票
1. **300149 睿智医药** - 置信度:68% 风险:medium
2. **301392 汇成真空** - 置信度:68% 风险:medium

## 🎯 操作建议
- **建议仓位**: 40-50%
- **置信度**: 中
- **策略**: 谨慎参与
```

#### 2. 反馈报告
**文件**：`memory/investment/daily/feedback_report_YYYY-MM-DD.json`

**内容**：
- 昨日预测验证结果
- 历史准确率统计
- 模型优化建议

**示例**：
```json
{
  "date": "2026-04-01",
  "verification": {
    "total_predictions": 5,
    "successful": 3,
    "accuracy": 0.6
  },
  "optimization": {
    "suggestions": [
      "PE区间优化: 建议调整为8-50倍",
      "换手率权重提升: 当前30% → 建议40%"
    ]
  }
}
```

#### 3. 股票筛选结果
**文件**：`memory/investment/daily/screened_stocks_YYYY-MM-DD.csv`

**内容**：
- 股票代码、名称
- 最新价、涨跌幅
- PE、换手率
- 综合评分

#### 4. 新闻数据
**文件**：
- `news_YYYY-MM-DD.json`（国内）
- `global_news_YYYY-MM-DD.json`（海外）

**内容**：
- 标题、来源、URL
- 采集时间

#### 5. 趋势数据
**文件**：`memory/investment/knowledge/trends/daily_trends.json`

**内容**：
- 新闻数量
- 情绪得分
- 热门主题

### 知识库产出

#### 1. 新闻归档
**路径**：`memory/investment/knowledge/news_archive/2026-04/`

**文件**：
- `macro_YYYY-MM-DD.json`（宏观经济）
- `policy_YYYY-MM-DD.json`（政策解读）
- `industry_YYYY-MM-DD.json`（行业动态）
- `market_YYYY-MM-DD.json`（市场情绪）
- `company_YYYY-MM-DD.json`（公司新闻）

**用途**：
- 历史数据查询
- 趋势分析
- 模式识别

#### 2. 反馈历史
**文件**：`memory/investment/knowledge/feedback_history.json`

**内容**：
- 历史预测记录
- 验证结果
- 准确率统计

**用途**：
- 置信度调整
- 模型优化
- 效果评估

---

## 使用指南

### 快速开始

#### 1. 查看今日建议
```bash
cd /Users/glenman/.openclaw/workspace
cat memory/investment/daily/integrated_advice_$(date +%Y-%m-%d).md
```

#### 2. 手动生成建议
```bash
# 推荐：整合版（结合知识库）
python3 investment-system/run_integrated_system.py

# 备用：快速版（无历史知识）
python3 investment-system/run_pre_market_quick.py

# 完整：闭环版（验证+生成+学习）
./investment-system/run_daily_closed_loop.sh
```

#### 3. 查看历史数据
```bash
# 查看趋势数据
cat memory/investment/knowledge/trends/daily_trends.json

# 查看反馈历史
cat memory/investment/knowledge/feedback_history.json

# 查看新闻归档
ls memory/investment/knowledge/news_archive/2026-04/
```

### 自动运行

系统已配置到Heartbeat，每日8:30自动运行。

**配置文件**：`HEARTBEAT.md`

**检查方式**：
```bash
# 查看Heartbeat配置
cat HEARTBEAT.md

# 查看执行日志
# （通过系统日志查看）
```

### 数据查询

#### 查询特定日期建议
```bash
cat memory/investment/daily/integrated_advice_2026-04-01.md
```

#### 查询特定主题新闻
```bash
cat memory/investment/knowledge/news_archive/2026-04/market_2026-04-01.json
```

#### 统计准确率
```bash
# 使用jq工具
cat memory/investment/knowledge/feedback_history.json | jq '.[] | .accuracy'
```

---

## 风险提示

### 系统风险

1. **数据源限制**
   - 东方财富API限制（每次最多3000只）
   - 海外新闻采集不稳定
   - 非交易日数据延迟

2. **模型局限**
   - 基于历史数据，无法预测黑天鹅事件
   - AI分析有局限性
   - 需要时间积累反馈数据

3. **准确率不确定**
   - 初期置信度低（50%）
   - 需要7天以上建立反馈
   - 历史准确率不代表未来

### 投资风险

⚠️ **重要声明**：

- **所有建议仅供参考，不构成投资建议**
- **市场有风险，投资需谨慎**
- **请独立决策，严格控制风险**
- **历史表现不代表未来收益**
- **建议严格执行止损止盈纪律**

### 使用建议

1. **初期谨慎**
   - 前7天建议低仓位（20-30%）
   - 观察系统准确率
   - 积累反馈数据

2. **理性对待**
   - 不要盲目跟随建议
   - 结合自身判断
   - 关注风险提示

3. **持续观察**
   - 定期查看准确率
   - 关注置信度变化
   - 评估系统效果

---

## 附录

### 技术栈

- **语言**：Python 3
- **依赖**：urllib（标准库，无需安装）
- **存储**：JSON、CSV、Markdown
- **调度**：OpenClaw Heartbeat

### 免费资源

**数据源（全部免费）**：
- 东方财富API
- 财联社
- 新浪财经
- 巨潮资讯网

**无需付费账号或API Key**

### 更新日志

#### v1.0.0 (2026-04-01)
- ✅ 建立闭环学习系统
- ✅ 整合知识库和反馈机制
- ✅ 实现动态置信度调整
- ✅ 完善项目文档

### 联系方式

- 维护者：小龙虾AI助手 🦞
- 创建时间：2026-04-01
- 仓库位置：`/Users/glenman/.openclaw/workspace/investment-system/`

---

**项目状态**：✅ 生产环境运行中

**最后更新**：2026-04-01 18:50

---

🦞 **每日荐股分析 - 持续学习，智能决策**
