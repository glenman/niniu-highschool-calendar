#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heartbeat 执行脚本 - 每日荐股分析
生成报告并发送内容到飞书群
"""

import json
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_collectors.news_fetcher import MultiSourceNewsFetcher
from data_collectors.stock_data_fetcher import StockDataFetcher
from models.knowledge_analyzer import KnowledgeAnalyzer


def run_and_send_report():
    """运行分析并发送报告到飞书群"""
    
    # 导入整合版系统
    from models.pre_market_advisor import PreMarketAdvisor
    
    print("=" * 80)
    print("🎯 每日荐股分析 - Heartbeat触发")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # 1. 生成报告
        advisor = PreMarketAdvisor()
        advice = advisor.generate_trading_advice()
        
        # 2. 读取生成的报告
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = f"memory/investment/daily/integrated_advice_{today}.md"
        
        if os.path.exists(report_file):
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # 3. 输出报告内容（会自动发送到飞书群）
            print("\n" + "=" * 80)
            print("📤 发送报告到飞书群")
            print("=" * 80)
            print(report_content)
            print("=" * 80)
            
            return report_content
        else:
            print("❌ 报告文件生成失败")
            return None
            
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    run_and_send_report()
