#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股投资分析系统 - 主运行脚本
每日自动执行：数据采集 + 分析 + 报告生成
"""

import sys
import os
from datetime import datetime

# 添加系统路径
sys.path.append(os.path.dirname(__file__))

from data_collectors.stock_data_fetcher import StockDataFetcher
from models.daily_report import DailyReportGenerator


def main():
    """主函数 - 自我学习与知识积累"""
    print("=" * 80)
    print(f"🦞 投资知识系统 - 每日学习任务")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    try:
        # 步骤1：新闻采集
        print("【步骤1/5】多源新闻采集")
        print("-" * 80)
        from data_collectors.news_fetcher import MultiSourceNewsFetcher
        news_fetcher = MultiSourceNewsFetcher()
        news = news_fetcher.fetch_all_news(max_per_source=20)
        print()
        
        # 步骤2：知识分析与归档
        print("【步骤2/5】智能知识分析")
        print("-" * 80)
        from models.knowledge_analyzer import KnowledgeAnalyzer
        knowledge_analyzer = KnowledgeAnalyzer()
        categorized = knowledge_analyzer.analyze_and_archive(news)
        rotation = knowledge_analyzer.analyze_sector_rotation()
        print()
        
        # 步骤3：股票数据采集
        print("【步骤3/5】股票数据采集")
        print("-" * 80)
        fetcher = StockDataFetcher()
        stock_list = fetcher.get_stock_list(limit=3000)
        screened = fetcher.screen_stocks(stock_list) if stock_list else None
        north_fund = fetcher.get_north_fund()
        print()
        
        # 步骤4：保存筛选结果（用于趋势分析）
        print("【步骤4/5】更新股票数据库")
        print("-" * 80)
        if screened:
            today = datetime.now().strftime('%Y-%m-%d')
            csv_file = f"memory/investment/daily/screened_stocks_{today}.csv"
            import csv
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                if screened:
                    writer = csv.DictWriter(f, fieldnames=screened[0].keys())
                    writer.writeheader()
                    writer.writerows(screened)
            print(f"✅ 筛选结果已保存: {len(screened)}只股票")
        print()
        
        # 步骤5：自我学习总结（不生成报告）
        print("【步骤5/5】知识积累完成")
        print("-" * 80)
        today = datetime.now().strftime('%Y-%m-%d')
        learning_file = f"memory/investment/knowledge/daily_learning_{today}.md"
        
        with open(learning_file, 'w', encoding='utf-8') as f:
            f.write(f"# 投资学习记录 - {today}\n\n")
            
            f.write("## 📰 新闻学习\n\n")
            f.write(f"- **采集新闻数**: {len(news)}条\n")
            f.write(f"- **分类统计**:\n")
            for category, items in categorized.items():
                f.write(f"  - {category}: {len(items)}条\n")
            
            f.write("\n## 📊 市场观察\n\n")
            if north_fund:
                f.write(f"- **北向资金**: 净流入{north_fund.get('当日净流入', 0):.2f}亿元\n")
            if screened:
                f.write(f"- **筛选股票数**: {len(screened)}只\n")
                f.write(f"- **TOP3推荐**: \n")
                for i, stock in enumerate(screened[:3], 1):
                    f.write(f"  {i}. {stock['代码']} {stock['名称']} (评分:{stock['评分']:.1f})\n")
            
            if rotation and rotation.get('rising_sectors'):
                f.write("\n## 📈 板块轮动观察\n\n")
                f.write(f"- **热门板块**: {', '.join(set(rotation['rising_sectors'][:5]))}\n")
            
            f.write("\n## 🧠 知识积累\n\n")
            f.write("- ✅ 新闻已归档到知识库（按主题分类）\n")
            f.write("- ✅ 趋势指标已更新\n")
            f.write("- ✅ 板块轮动数据已记录\n")
        
        print(f"✅ 学习记录: {learning_file}")
        
        print()
        print("=" * 80)
        print("✅ 每日学习任务完成")
        print(f"📰 新闻: {len(news)}条 → 已归档")
        print(f"📊 股票: {len(screened) if screened else 0}只 → 已记录")
        print(f"🧠 知识库: 持续积累中")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 系统执行出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
