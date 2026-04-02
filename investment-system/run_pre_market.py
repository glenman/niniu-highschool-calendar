#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开盘前操盘建议系统 - 整合版
生成时间：每日8:30前
输出：预见性操盘建议
"""

import json
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_collectors.news_fetcher import MultiSourceNewsFetcher
from data_collectors.stock_data_fetcher import StockDataFetcher
from models.knowledge_analyzer import KnowledgeAnalyzer
from models.pre_market_advisor import PreMarketAdvisor


def run_pre_market_analysis():
    """运行开盘前分析"""
    print("=" * 80)
    print(f"🎯 开盘前操盘建议系统")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 目标: 9:30开盘前给出操盘建议")
    print("=" * 80)
    
    try:
        # 步骤1：采集国内新闻
        print("\n【步骤1/6】采集国内新闻")
        print("-" * 80)
        news_fetcher = MultiSourceNewsFetcher()
        domestic_news = news_fetcher.fetch_all_news(max_per_source=15)
        print()
        
        # 步骤2：尝试采集海外新闻（容错）
        print("\n【步骤2/6】采集海外新闻（可能部分失败）")
        print("-" * 80)
        try:
            from data_collectors.global_news_fetcher import GlobalNewsFetcher
            global_fetcher = GlobalNewsFetcher()
            # 只尝试优先级最高的3个源（减少超时）
            global_fetcher.political_sources = dict(
                list(global_fetcher.political_sources.items())[:3]
            )
            global_fetcher.financial_sources = dict(
                list(global_fetcher.financial_sources.items())[:3]
            )
            global_news = global_fetcher.fetch_all_global_news()
            
            # 保存海外新闻
            today = datetime.now().strftime('%Y-%m-%d')
            global_file = f"memory/investment/daily/global_news_{today}.json"
            with open(global_file, 'w', encoding='utf-8') as f:
                json.dump(global_news, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 海外新闻采集失败: {e}")
            print("✅ 将基于国内新闻继续分析")
            global_news = []
        print()
        
        # 步骤3：智能分析新闻
        print("\n【步骤3/6】智能分析新闻")
        print("-" * 80)
        analyzer = KnowledgeAnalyzer()
        categorized = analyzer.analyze_and_archive(domestic_news)
        print()
        
        # 步骤4：获取股票筛选结果
        print("\n【步骤4/6】筛选优质股票")
        print("-" * 80)
        stock_fetcher = StockDataFetcher()
        stock_list = stock_fetcher.get_stock_list(limit=2000)
        screened = stock_fetcher.screen_stocks(stock_list) if stock_list else []
        north_fund = stock_fetcher.get_north_fund()
        print()
        
        # 步骤5：生成开盘前建议
        print("\n【步骤5/6】生成开盘前操盘建议")
        print("-" * 80)
        advisor = PreMarketAdvisor()
        advice = advisor.generate_trading_advice()
        print()
        
        # 步骤6：保存完整报告
        print("\n【步骤6/6】保存操盘建议")
        print("-" * 80)
        today = datetime.now().strftime('%Y-%m-%d')
        output_dir = "memory/investment/daily"
        os.makedirs(output_dir, exist_ok=True)
        
        # 完整报告
        full_report = []
        full_report.append("=" * 80)
        full_report.append(f"🎯 开盘前操盘建议 - {today}")
        full_report.append("=" * 80)
        full_report.append("")
        full_report.append(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        full_report.append(f"📊 适用时间: 今日9:30开盘前")
        full_report.append("")
        
        # 市场概况
        full_report.append("## 📊 市场概况")
        full_report.append("")
        full_report.append(f"- **国内新闻**: {len(domestic_news)}条")
        full_report.append(f"- **海外新闻**: {len(global_news)}条")
        if north_fund:
            full_report.append(f"- **北向资金**: 净流入{north_fund.get('当日净流入', 0):.2f}亿元")
        if screened:
            full_report.append(f"- **筛选股票**: {len(screened)}只优质标的")
        full_report.append("")
        
        # 关键新闻摘要
        full_report.append("## 📰 关键新闻摘要")
        full_report.append("")
        full_report.append("### 国内重点")
        full_report.append("")
        for i, news in enumerate(domestic_news[:10], 1):
            full_report.append(f"{i}. [{news['source']}] {news['title'][:70]}")
        full_report.append("")
        
        if global_news:
            full_report.append("### 海外重点")
            full_report.append("")
            for i, news in enumerate(global_news[:5], 1):
                full_report.append(f"{i}. [{news['source']}] {news['title'][:70]}")
            full_report.append("")
        
        # 推荐股票
        if screened:
            full_report.append("## 📈 今日关注股票")
            full_report.append("")
            full_report.append("基于多因子模型筛选的优质标的：")
            full_report.append("")
            for i, stock in enumerate(screened[:5], 1):
                full_report.append(
                    f"{i}. **{stock['代码']} {stock['名称']}** - "
                    f"价格:{stock['最新价']:.2f} "
                    f"PE:{stock['市盈率']:.1f} "
                    f"涨跌:{stock['涨跌幅']:.2f}% "
                    f"评分:{stock['评分']:.1f}"
                )
            full_report.append("")
        
        # 操作建议
        full_report.append("## 💡 操作建议")
        full_report.append("")
        full_report.append("⚠️ **重要提示**: 以下建议基于新闻和技术分析，仅供参考")
        full_report.append("")
        full_report.append("### 仓位建议")
        full_report.append("")
        if len(screened) >= 5:
            full_report.append("- **建议仓位**: 60-70%")
            full_report.append("- **理由**: 市场信号积极，可选标的充足")
        elif len(screened) >= 3:
            full_report.append("- **建议仓位**: 40-50%")
            full_report.append("- **理由**: 市场信号一般，谨慎参与")
        else:
            full_report.append("- **建议仓位**: 20-30%")
            full_report.append("- **理由**: 市场信号偏弱，轻仓观望")
        full_report.append("")
        
        full_report.append("### 操作策略")
        full_report.append("")
        full_report.append("1. **开盘观察期** (9:30-10:00)")
        full_report.append("   - 观察集合竞价情况")
        full_report.append("   - 关注推荐股票的开盘表现")
        full_report.append("   - 等待市场方向明确")
        full_report.append("")
        full_report.append("2. **建仓时机** (10:00-11:30)")
        full_report.append("   - 等待回调后再介入")
        full_report.append("   - 分批建仓，控制成本")
        full_report.append("   - 严格执行止损（建议-5%）")
        full_report.append("")
        full_report.append("3. **持仓管理** (全天)")
        full_report.append("   - 盯盘关注资金流向")
        full_report.append("   - 设置止盈点（建议+8%-15%）")
        full_report.append("   - 不追高，不恐慌性抛售")
        full_report.append("")
        
        # 风险提示
        full_report.append("## ⚠️ 风险提示")
        full_report.append("")
        full_report.append("- 本建议基于AI分析，存在局限性")
        full_report.append("- 市场有风险，投资需谨慎")
        full_report.append("- 请结合自身风险承受能力")
        full_report.append("- 严格执行纪律，控制回撤")
        full_report.append("")
        
        # 免责声明
        full_report.append("---")
        full_report.append("")
        full_report.append("🦞 **小龙虾AI投资助手**")
        full_report.append("📅 生成时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        full_report.append("⚠️ **免责声明**: 不构成投资建议，请独立决策")
        full_report.append("=" * 80)
        
        # 保存
        report_file = f"{output_dir}/pre_market_advice_{today}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(full_report))
        
        print(f"✅ 完整报告已保存: {report_file}")
        
        # 显示预览
        print("\n" + "=" * 80)
        print("📄 操盘建议预览")
        print("=" * 80)
        print("\n".join(full_report[:50]))  # 显示前50行
        
        print("\n" + "=" * 80)
        print("✅ 开盘前操盘建议生成完成")
        print(f"📰 国内新闻: {len(domestic_news)}条")
        print(f"🌏 海外新闻: {len(global_news)}条")
        print(f"📊 推荐股票: {len(screened)}只")
        print(f"📄 完整报告: {report_file}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 系统执行出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    success = run_pre_market_analysis()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
