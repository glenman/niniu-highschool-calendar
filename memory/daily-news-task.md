# 每日新闻简报自动生成任务

## 任务说明

每天早上6点，小龙虾会自动：
1. 抓取国内外权威新闻源的头条新闻
2. 生成高质量中文摘要和分析
3. 保存到GitHub项目并自动推送

## 新闻源配置

### 国际新闻源（4个）
- CNBC - 美国消费者新闻与商业频道
- 华尔街日报
- 市场观察
- 雅虎财经

### 国内新闻源（4个）
- 雪球
- IT之家
- 少数派
- 知乎日报

每个源抓取4条头条新闻，共32条新闻。

## 执行方式

### 自动执行（每天早上6点）
通过OpenClaw的heartbeat机制自动触发。

### 手动执行
在对话中说："生成今天的新闻简报"

## 技术实现

1. **抓取新闻**: 使用web_fetch工具获取新闻源内容
2. **生成内容**: 由小龙虾AI助手生成高质量中文摘要和分析
3. **保存数据**: 调用save_news.py脚本保存JSON数据
4. **推送GitHub**: 自动commit和push

## 输出格式

每条新闻包含：
- title: 中文标题
- title_en: 英文原标题
- url: 原文链接
- source: 来源名称
- summary: 中文摘要（100-150字）
- summary_en: 英文原摘要
- importance: 重要程度（high/medium/low）
- analysis: 中文分析（50-100字）
- tags: 相关标签

## 成本

完全免费！由小龙虾AI助手生成内容，无需任何外部API。

## 监控

- 日志位置：`/tmp/news_generation.log`
- 数据位置：`/Users/glenman/.openclaw/workspace/daily-finance-news/data/`
- 网站：https://glenman.github.io/daily-finance-news/

---

最后更新：2026-03-22
