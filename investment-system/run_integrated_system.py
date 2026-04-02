#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合版操盘建议系统 - 结合知识库、新闻主题和反馈学习
"""

import json
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_collectors.news_fetcher import MultiSourceNewsFetcher
from data_collectors.stock_data_fetcher import StockDataFetcher  # 修复：使用重命名后的主版本
from models.knowledge_analyzer import KnowledgeAnalyzer
from models.theme_sector_mapper import ThemeSectorMapper


class IntegratedPreMarketAdvisor:
    """整合版开盘前操盘顾问"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.base_dir = "memory/investment/daily"
        self.knowledge_dir = "memory/investment/knowledge"
        self.trends_file = f"{self.knowledge_dir}/trends/daily_trends.json"
        self.feedback_file = f"{self.knowledge_dir}/feedback_history.json"
        
    def load_historical_knowledge(self):
        """加载历史知识库"""
        print("\n📚 加载历史知识库...")
        
        knowledge = {
            'trends': {},
            'accuracy': {}
        }
        
        if os.path.exists(self.trends_file):
            with open(self.trends_file, 'r', encoding='utf-8') as f:
                trends = json.load(f)
            recent_dates = sorted(trends.keys())[-7:]
            for date in recent_dates:
                knowledge['trends'][date] = trends[date]
            print(f"  ✅ 加载{len(recent_dates)}天趋势数据")
        
        if os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                feedback = json.load(f)
            if feedback:
                total = len(feedback)
                successful = sum(1 for v in feedback.values() if v.get('success', False))
                knowledge['accuracy'] = {
                    'total': total,
                    'successful': successful,
                    'rate': successful / max(total, 1)
                }
                print(f"  ✅ 历史准确率: {knowledge['accuracy']['rate']:.1%}")
        
        return knowledge
    
    def analyze_market_patterns(self, knowledge):
        """分析市场模式"""
        print("\n🔍 分析市场模式...")
        
        patterns = {
            'sentiment_trend': 'stable',
            'prediction_confidence': 0.5
        }
        
        if knowledge['trends']:
            sentiments = []
            for date, trend in knowledge['trends'].items():
                if 'sentiment_score' in trend:
                    sentiments.append(trend['sentiment_score'])
            
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                recent_sentiment = sentiments[-1]
                
                if recent_sentiment > avg_sentiment + 0.1:
                    patterns['sentiment_trend'] = 'improving'
                elif recent_sentiment < avg_sentiment - 0.1:
                    patterns['sentiment_trend'] = 'declining'
                else:
                    patterns['sentiment_trend'] = 'stable'
                
                print(f"  ✅ 情绪趋势: {patterns['sentiment_trend']} (当前{recent_sentiment:.2f}, 均值{avg_sentiment:.2f})")
        
        if knowledge['accuracy']:
            patterns['prediction_confidence'] = min(knowledge['accuracy']['rate'], 0.85)
            print(f"  ✅ 预测置信度: {patterns['prediction_confidence']:.1%}")
        
        return patterns
    
    def generate_integrated_advice(self):
        """生成整合版操盘建议"""
        print("=" * 80)
        print(f"🎯 整合版开盘前操盘建议")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 结合知识库 + 主题分析 + 反馈学习")
        print("=" * 80)
        
        # 1. 加载历史知识
        knowledge = self.load_historical_knowledge()
        
        # 2. 采集今日新闻
        print("\n【步骤1/7】采集今日新闻...")
        news_fetcher = MultiSourceNewsFetcher()
        domestic_news = news_fetcher.fetch_all_news(max_per_source=10)
        
        # 3. 智能分析
        print("\n【步骤2/7】智能分析新闻...")
        analyzer = KnowledgeAnalyzer()
        categorized = analyzer.analyze_and_archive(domestic_news)
        
        # 4. 主题识别(核心新增)
        print("\n【步骤3/7】识别热点主题...")
        theme_mapper = ThemeSectorMapper()
        hot_themes = theme_mapper.identify_themes(domestic_news)
        
        # 5. 分析市场模式
        print("\n【步骤4/7】分析市场模式...")
        patterns = self.analyze_market_patterns(knowledge)
        
        # 6. 筛选股票(扩大到2000只)
        print("\n【步骤5/7】筛选优质股票(扩大股票池到2000只)...")
        stock_fetcher = StockDataFetcher()  # 使用修复后的版本
        stock_list = stock_fetcher.get_stock_list(limit=2000)
        
        # 如果v2获取失败,降级到100只
        if not stock_list:
            print("  ⚠️ 获取2000只失败，降级到100只...")
            stock_list = stock_fetcher.get_stock_list(limit=100)
        
        screened = stock_fetcher.screen_stocks(stock_list) if stock_list else []
        
        # 7. 基于主题推荐股票(核心新增)
        print("\n【步骤6/7】基于主题推荐股票...")
        theme_recommendations, hot_sectors = theme_mapper.get_sector_recommendations(hot_themes, stock_list)
        
        # 8. 合并推荐
        print("\n【步骤7/7】生成智能推荐...")
        # 主题推荐优先
        all_recommendations = theme_recommendations.copy()
        # 补充技术面筛选的股票
        for stock in screened[:10]:
            stock_name = stock.get('名称', '')
            # 避免重复
            if not any(rec.get('名称') == stock_name for rec in all_recommendations):
                all_recommendations.append({
                    **stock,
                    'theme': '技术面',
                    'sector': '综合',
                    'recommendation_reason': f"技术面评分:{stock.get('评分', 0):.1f}"
                })
        
        # 9. 生成报告
        report = self._build_integrated_report(
            knowledge, patterns, domestic_news, all_recommendations, hot_themes, hot_sectors
        )
        
        # 保存
        report_file = f"{self.base_dir}/integrated_advice_{self.today}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 整合版建议已生成: {report_file}")
        print("\n" + "=" * 80)
        print(report[:2500])
        
        return report
    
    def _build_integrated_report(self, knowledge, patterns, news, recommendations, hot_themes, hot_sectors):
        """构建整合版报告"""
        report = []
        report.append("=" * 80)
        report.append(f"🎯 整合版开盘前操盘建议 - {self.today}")
        report.append("=" * 80)
        report.append("")
        report.append(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📊 数据来源: 历史知识库 + 今日新闻 + 主题分析 + 反馈学习")
        report.append("")
        
        # 历史知识
        report.append("## 📚 岆史知识分析")
        report.append("")
        if knowledge['accuracy']:
            report.append(f"- **历史准确率**: {knowledge['accuracy']['rate']:.1%}")
            report.append(f"- **验证次数**: {knowledge['accuracy']['total']}次")
        report.append(f"- **情绪趋势**: {patterns['sentiment_trend']}")
        report.append(f"- **预测置信度**: {patterns['prediction_confidence']:.1%}")
        report.append("")
        
        # 今日新闻
        report.append("## 📰 今日关键新闻")
        report.append("")
        for i, item in enumerate(news[:5], 1):
            report.append(f"{i}. [{item['source']}] {item['title'][:70]}")
        report.append("")
        
        # 热点主题(核心部分)
        if hot_themes:
            report.append("## 🔥 热点主题分析")
            report.append("")
            theme_count = 0
            for theme, data in hot_themes:
                if data['count'] > 0 and theme_count < 5:
                    report.append(f"{theme_count+1}. **{theme}** ({data['sector']}) - {data['count']}条新闻")
                    report.append(f"   关注个股: {', '.join(data['related_stocks'][:3])}")
                    theme_count += 1
            report.append("")
        
        # 智能推荐
        if recommendations:
            report.append("## 💡 智能推荐股票(主题驱动+技术面)")
            report.append("")
            for i, rec in enumerate(recommendations[:10], 1):
                code = rec.get('代码', 'N/A')
                name = rec.get('名称', 'N/A')
                theme = rec.get('theme', '')
                reason = rec.get('recommendation_reason', '')
                
                if theme:
                    report.append(f"{i}. **{code} {name}**")
                    report.append(f"   【{theme}】{reason}")
                else:
                    report.append(f"{i}. **{code} {name}** - {reason}")
            report.append("")
        
        # 操作建议
        report.append("## 🎯 操作建议(基于置信度)")
        report.append("")
        confidence = patterns['prediction_confidence']
        
        if confidence >= 0.7:
            report.append("- **建议仓位**: 60-70%")
            report.append("- **置信度**: 高")
            report.append("- **策略**: 可积极参与，重点关注热点主题")
        elif confidence >= 0.5:
            report.append("- **建议仓位**: 40-50%")
            report.append("- **置信度**: 中")
            report.append("- **策略**: 谨慎参与，优先配置主题相关个股")
        else:
            report.append("- **建议仓位**: 20-30%")
            report.append("- **置信度**: 低")
            report.append("- **策略**: 观望为主，小仓位试探")
        report.append("")
        
        report.append("## ⚠️ 风险提示")
        report.append("")
        report.append("- 本建议基于AI分析和历史模式")
        report.append("- 主题投资有轮动风险，注意及时止盈")
        report.append("- 历史表现不代表未来收益")
        report.append("- 请独立决策，控制风险")
        report.append("")
        
        report.append("---")
        report.append("")
        report.append("🦞 整合版系统 - 主题驱动 + 持续学习")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """主函数"""
    advisor = IntegratedPreMarketAdvisor()
    advisor.generate_integrated_advice()


if __name__ == '__main__':
    main()
