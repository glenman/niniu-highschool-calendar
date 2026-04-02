#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开盘前操盘建议生成器 - 基于国内外新闻分析的预见性判断
"""

import json
import os
from datetime import datetime
from collections import defaultdict
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class PreMarketAdvisor:
    """开盘前操盘顾问"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.base_dir = "memory/investment/daily"
        
        # 事件影响权重
        self.impact_weights = {
            'war': -5,           # 战争
            'sanctions': -3,     # 制裁
            'trade_war': -4,     # 贸易战
            'rate_hike': -2,     # 加息
            'rate_cut': 3,       # 降息
            'stimulus': 4,       # 刺激政策
            'policy_support': 3, # 政策支持
            'earnings_beat': 2,  # 业绩超预期
            'earnings_miss': -2, # 业绩不及预期
            'ipo': -1,           # IPO
            'm_a': 1,            # 并购
        }
    
    def load_news_data(self):
        """加载国内外新闻数据"""
        # 国内新闻
        domestic_file = f"{self.base_dir}/news_{self.today}.json"
        domestic_news = []
        if os.path.exists(domestic_file):
            with open(domestic_file, 'r', encoding='utf-8') as f:
                domestic_news = json.load(f)
        
        # 海外新闻
        global_file = f"{self.base_dir}/global_news_{self.today}.json"
        global_news = []
        if os.path.exists(global_file):
            with open(global_file, 'r', encoding='utf-8') as f:
                global_news = json.load(f)
        
        return domestic_news, global_news
    
    def analyze_key_events(self, domestic_news, global_news):
        """分析关键事件"""
        events = {
            'domestic': [],
            'global': [],
            'impact_score': 0
        }
        
        # 分析国内新闻
        for news in domestic_news:
            title = news.get('title', '')
            
            # 识别关键事件
            if '政策' in title or '支持' in title:
                events['domestic'].append({
                    'type': 'policy_support',
                    'title': title[:80],
                    'impact': 'positive'
                })
                events['impact_score'] += 2
            
            if '利好' in title or '增长' in title:
                events['domestic'].append({
                    'type': 'positive',
                    'title': title[:80],
                    'impact': 'positive'
                })
                events['impact_score'] += 1
            
            if '利空' in title or '下滑' in title or '亏损' in title:
                events['domestic'].append({
                    'type': 'negative',
                    'title': title[:80],
                    'impact': 'negative'
                })
                events['impact_score'] -= 1
        
        # 分析海外新闻
        for news in global_news:
            title = news.get('title', '').lower()
            
            # 识别海外关键事件
            if any(k in title for k in ['war', 'conflict', 'attack']):
                events['global'].append({
                    'type': 'geopolitical_risk',
                    'title': news.get('title', '')[:80],
                    'impact': 'highly_negative'
                })
                events['impact_score'] -= 3
            
            if any(k in title for k in ['tariff', 'sanction', 'trade war']):
                events['global'].append({
                    'type': 'trade_risk',
                    'title': news.get('title', '')[:80],
                    'impact': 'negative'
                })
                events['impact_score'] -= 2
            
            if any(k in title for k in ['rate', 'fed', 'ecb']):
                events['global'].append({
                    'type': 'monetary_policy',
                    'title': news.get('title', '')[:80],
                    'impact': 'neutral'
                })
        
        return events
    
    def generate_market_outlook(self, events):
        """生成市场展望"""
        score = events['impact_score']
        
        if score >= 5:
            outlook = "强烈看多"
            confidence = "高"
            strategy = "积极布局，关注强势板块"
        elif score >= 2:
            outlook = "谨慎看多"
            confidence = "中"
            strategy = "逢低吸纳，控制仓位"
        elif score >= -2:
            outlook = "震荡整理"
            confidence = "中"
            strategy = "观望为主，轻仓试探"
        elif score >= -5:
            outlook = "谨慎看空"
            confidence = "中"
            strategy = "减仓避险，等待时机"
        else:
            outlook = "强烈看空"
            confidence = "高"
            strategy = "清仓观望，规避风险"
        
        return {
            'outlook': outlook,
            'confidence': confidence,
            'strategy': strategy,
            'score': score
        }
    
    def generate_sector_recommendations(self, events):
        """生成板块推荐"""
        recommendations = {
            'strong_buy': [],
            'buy': [],
            'hold': [],
            'avoid': []
        }
        
        # 基于事件分析板块
        for event in events['domestic'] + events['global']:
            title = event.get('title', '').lower()
            
            # 医药板块
            if '医药' in title or '医疗' in title:
                if event['impact'] == 'positive':
                    recommendations['strong_buy'].append('医药')
            
            # 科技板块
            if '科技' in title or '半导体' in title or '芯片' in title:
                if event['impact'] == 'positive':
                    recommendations['buy'].append('科技')
            
            # 新能源
            if '新能源' in title or '光伏' in title or '锂电' in title:
                if event['impact'] == 'positive':
                    recommendations['buy'].append('新能源')
            
            # 地缘政治风险
            if event.get('type') == 'geopolitical_risk':
                recommendations['avoid'].append('出口导向型')
                recommendations['hold'].append('避险资产（黄金）')
        
        # 去重
        for key in recommendations:
            recommendations[key] = list(set(recommendations[key]))
        
        return recommendations
    
    def generate_trading_advice(self):
        """生成开盘前操盘建议"""
        print("\n" + "=" * 60)
        print("🎯 生成开盘前操盘建议")
        print("=" * 60)
        
        # 1. 加载新闻数据
        print("\n【1/4】加载新闻数据...")
        domestic_news, global_news = self.load_news_data()
        print(f"  📰 国内新闻: {len(domestic_news)}条")
        print(f"  🌏 海外新闻: {len(global_news)}条")
        
        # 2. 分析关键事件
        print("\n【2/4】分析关键事件...")
        events = self.analyze_key_events(domestic_news, global_news)
        print(f"  ✅ 国内关键事件: {len(events['domestic'])}个")
        print(f"  ✅ 海外关键事件: {len(events['global'])}个")
        print(f"  📊 影响评分: {events['impact_score']}")
        
        # 3. 生成市场展望
        print("\n【3/4】生成市场展望...")
        outlook = self.generate_market_outlook(events)
        print(f"  📈 市场判断: {outlook['outlook']} (置信度: {outlook['confidence']})")
        print(f"  💡 操作策略: {outlook['strategy']}")
        
        # 4. 板块推荐
        print("\n【4/4】生成板块推荐...")
        sectors = self.generate_sector_recommendations(events)
        if sectors['strong_buy']:
            print(f"  ⭐ 强烈推荐: {', '.join(sectors['strong_buy'])}")
        if sectors['buy']:
            print(f"  ✅ 推荐关注: {', '.join(sectors['buy'])}")
        if sectors['avoid']:
            print(f"  ⚠️ 建议回避: {', '.join(sectors['avoid'])}")
        
        # 5. 生成完整建议
        advice = self._build_advice_report(
            domestic_news, global_news, 
            events, outlook, sectors
        )
        
        # 保存
        advice_file = f"{self.base_dir}/pre_market_advice_{self.today}.md"
        with open(advice_file, 'w', encoding='utf-8') as f:
            f.write(advice)
        
        print(f"\n✅ 操盘建议已生成: {advice_file}")
        print("\n" + "=" * 60)
        
        return advice
    
    def _build_advice_report(self, domestic_news, global_news, events, outlook, sectors):
        """构建完整建议报告"""
        report = []
        report.append("=" * 80)
        report.append(f"🎯 开盘前操盘建议 - {self.today}")
        report.append("=" * 80)
        report.append("")
        report.append(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📊 适用时间: 今日9:30开盘前")
        report.append("")
        
        # 核心判断
        report.append("## 📈 核心判断")
        report.append("")
        report.append(f"**市场展望**: {outlook['outlook']}")
        report.append(f"**置信度**: {outlook['confidence']}")
        report.append(f"**影响评分**: {outlook['score']} (范围-10到+10)")
        report.append(f"**操作策略**: {outlook['strategy']}")
        report.append("")
        
        # 关键事件
        report.append("## 🔍 关键事件分析")
        report.append("")
        
        if events['domestic']:
            report.append("### 国内关键事件")
            report.append("")
            for event in events['domestic'][:5]:
                report.append(f"- {event['title']}")
            report.append("")
        
        if events['global']:
            report.append("### 海外关键事件")
            report.append("")
            for event in events['global'][:5]:
                report.append(f"- {event['title']}")
            report.append("")
        
        # 板块推荐
        report.append("## 💡 板块操作建议")
        report.append("")
        
        if sectors['strong_buy']:
            report.append("### ⭐ 强烈推荐（可重仓）")
            report.append("")
            for sector in sectors['strong_buy']:
                report.append(f"- **{sector}**: 基本面+政策面双重利好")
            report.append("")
        
        if sectors['buy']:
            report.append("### ✅ 推荐关注（可配置）")
            report.append("")
            for sector in sectors['buy']:
                report.append(f"- {sector}")
            report.append("")
        
        if sectors['hold']:
            report.append("### 🔄 持有观望")
            report.append("")
            for sector in sectors['hold']:
                report.append(f"- {sector}")
            report.append("")
        
        if sectors['avoid']:
            report.append("### ⚠️ 建议回避")
            report.append("")
            for sector in sectors['avoid']:
                report.append(f"- {sector}")
            report.append("")
        
        # 风险提示
        report.append("## ⚠️ 风险提示")
        report.append("")
        report.append("- 本建议基于新闻分析，仅供参考")
        report.append("- 市场有风险，投资需谨慎")
        report.append("- 请结合自身风险承受能力操作")
        report.append("- 建议严格执行止损止盈")
        report.append("")
        
        # 免责声明
        report.append("---")
        report.append("")
        report.append("🦞 **小龙虾AI投资助手** - 预见性操盘建议")
        report.append("⚠️ 不构成投资建议，请独立决策")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """主函数"""
    advisor = PreMarketAdvisor()
    advice = advisor.generate_trading_advice()
    
    # 输出到控制台
    print("\n" + advice)
    
    return advice


if __name__ == '__main__':
    main()
