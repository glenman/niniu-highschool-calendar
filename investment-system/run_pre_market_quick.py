#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开盘前操盘建议 - 快速版（跳过海外新闻）
用于测试和快速生成建议
"""

import json
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_collectors.news_fetcher import MultiSourceNewsFetcher
from data_collectors.stock_data_fetcher import StockDataFetcher
from models.knowledge_analyzer import KnowledgeAnalyzer


def generate_quick_advice():
    """快速生成开盘建议"""
    print("=" * 80)
    print(f"🎯 开盘前操盘建议（快速版）")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = "memory/investment/daily"
    
    # 1. 采集国内新闻
    print("\n【1/3】采集国内新闻...")
    news_fetcher = MultiSourceNewsFetcher()
    domestic_news = news_fetcher.fetch_all_news(max_per_source=10)
    
    # 2. 筛选股票
    print("\n【2/3】筛选优质股票...")
    stock_fetcher = StockDataFetcher()
    stock_list = stock_fetcher.get_stock_list(limit=2000)
    screened = stock_fetcher.screen_stocks(stock_list) if stock_list else []
    
    # 3. 生成建议
    print("\n【3/3】生成操盘建议...")
    
    report = []
    report.append("=" * 80)
    report.append(f"🎯 开盘前操盘建议 - {today}")
    report.append("=" * 80)
    report.append("")
    report.append(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"📊 适用时间: 今日9:30开盘前")
    report.append("")
    
    # 市场概况
    report.append("## 📊 市场概况")
    report.append("")
    report.append(f"- **新闻数量**: {len(domestic_news)}条")
    if screened:
        report.append(f"- **筛选股票**: {len(screened)}只")
    report.append("")
    
    # 关键新闻
    report.append("## 📰 关键新闻（前5条）")
    report.append("")
    for i, news in enumerate(domestic_news[:5], 1):
        report.append(f"{i}. [{news['source']}] {news['title'][:70]}")
    report.append("")
    
    # 推荐股票
    if screened:
        report.append("## 📈 推荐股票（TOP5）")
        report.append("")
        for i, stock in enumerate(screened[:5], 1):
            report.append(
                f"{i}. **{stock['代码']} {stock['名称']}** - "
                f"价格:{stock['最新价']:.2f} "
                f"PE:{stock['市盈率']:.1f} "
                f"涨跌:{stock['涨跌幅']:.2f}% "
                f"评分:{stock['评分']:.1f}"
            )
        report.append("")
    
    # 操作建议
    report.append("## 💡 操作建议")
    report.append("")
    report.append("### 仓位建议")
    report.append("")
    if len(screened) >= 5:
        report.append("- **建议仓位**: 60-70%")
        report.append("- **理由**: 市场信号积极")
    elif len(screened) >= 3:
        report.append("- **建议仓位**: 40-50%")
        report.append("- **理由**: 市场信号一般")
    else:
        report.append("- **建议仓位**: 20-30%")
        report.append("- **理由**: 市场信号偏弱")
    report.append("")
    
    report.append("### 操作策略")
    report.append("")
    report.append("1. **开盘观察** (9:30-10:00)")
    report.append("   - 观察集合竞价和开盘表现")
    report.append("   - 等待市场方向明确")
    report.append("")
    report.append("2. **建仓时机** (10:00-11:30)")
    report.append("   - 回调后分批建仓")
    report.append("   - 严格止损（-5%）")
    report.append("")
    report.append("3. **持仓管理**")
    report.append("   - 设置止盈（+8%-15%）")
    report.append("   - 不追高，不恐慌抛售")
    report.append("")
    
    # 风险提示
    report.append("## ⚠️ 风险提示")
    report.append("")
    report.append("- 本建议基于AI分析，仅供参考")
    report.append("- 市场有风险，投资需谨慎")
    report.append("- 请独立决策，控制风险")
    report.append("")
    
    report.append("---")
    report.append("")
    report.append("🦞 小龙虾AI投资助手")
    report.append("⚠️ 不构成投资建议")
    report.append("=" * 80)
    
    # 保存
    report_file = f"{output_dir}/pre_market_advice_{today}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"\n✅ 报告已保存: {report_file}")
    print("\n" + "=" * 80)
    print("\n".join(report))
    
    return report


if __name__ == '__main__':
    generate_quick_advice()
