#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题识别与板块映射器
从新闻中识别热点主题，映射到相关板块，筛选相关股票
"""

import json
import re
from collections import defaultdict
from datetime import datetime


class ThemeSectorMapper:
    """主题识别与板块映射"""
    
    def __init__(self):
        # 主题关键词 -> 板块映射
        self.theme_keywords = {
            # 科技板块
            'AI': {
                'keywords': ['OpenAI', 'ChatGPT', '人工智能', 'AI', 'GPT', '深度学习', '机器学习'],
                'sector': '人工智能',
                'related_stocks': ['科大讯飞', '寒武纪', '云从科技', '商汤科技', '海光信息']
            },
            '芯片': {
                'keywords': ['芯片', '半导体', '中芯国际', '台积电', '晶圆', '集成电路'],
                'sector': '半导体',
                'related_stocks': ['中芯国际', '北方华创', '韦尔股份', '兆易创新', '紫光国微']
            },
            
            # 航天军工
            '航天': {
                'keywords': ['SpaceX', '火箭', '卫星', '航天', '载人', '绕月', '中科宇航', '星际荣耀'],
                'sector': '航天军工',
                'related_stocks': ['中航沈飞', '航天电子', '航天动力', '中国卫星', '中航光电']
            },
            '军工': {
                'keywords': ['军工', '国防', '武器', '无人机', '雷达'],
                'sector': '航天军工',
                'related_stocks': ['中航沈飞', '中直股份', '中航西飞', '洪都航空', '航天彩虹']
            },
            
            # 新能源
            '新能源': {
                'keywords': ['新能源', '光伏', '风电', '储能', '锂电池', '宁德时代'],
                'sector': '新能源',
                'related_stocks': ['宁德时代', '比亚迪', '隆基绿能', '通威股份', '阳光电源']
            },
            '电动车': {
                'keywords': ['电动车', '特斯拉', '蔚来', '理想', '小鹏', '新能源车'],
                'sector': '新能源汽车',
                'related_stocks': ['比亚迪', '宁德时代', '亿纬锂能', '恩捷股份', '天赐材料']
            },
            
            # 医药
            '医药': {
                'keywords': ['疫苗', '医药', '生物制药', '创新药', '仿制药'],
                'sector': '医药生物',
                'related_stocks': ['恒瑞医药', '药明康德', '智飞生物', '沃森生物', '复星医药']
            },
            
            # 机器人
            '机器人': {
                'keywords': ['机器人', '宇树科技', '优必选', '工业机器人', '服务机器人'],
                'sector': '机器人',
                'related_stocks': ['埃斯顿', '汇川技术', '机器人', '新时达', '拓斯达']
            },
            
            # 金融
            '金融': {
                'keywords': ['央行', '利率', '货币政策', '降息', '加息', '银行'],
                'sector': '金融',
                'related_stocks': ['招商银行', '宁波银行', '平安银行', '中信证券', '东方财富']
            }
        }
        
        # 板块到股票代码的映射（实际应用中应该从数据源获取）
        self.sector_stock_codes = {
            '人工智能': ['002230', '688256', '688327', '002049', '688041'],
            '半导体': ['688981', '002371', '603501', '603986', '002049'],
            '航天军工': ['600760', '600879', '600346', '600118', '002179'],
            '新能源': ['300750', '002594', '601012', '600438', '300274'],
            '新能源汽车': ['002594', '300750', '300014', '002812', '002709'],
            '医药生物': ['600276', '603259', '300122', '300142', '600196'],
            '机器人': ['002747', '300124', '300024', '002527', '300607']
        }
    
    def identify_themes(self, news_list):
        """从新闻中识别热点主题"""
        print("\n🔍 识别新闻中的热点主题...")
        
        theme_hits = defaultdict(lambda: {'count': 0, 'news': [], 'sector': '', 'related_stocks': []})
        
        for news in news_list:
            title = news.get('title', '')
            
            # 检查每个主题
            for theme_name, theme_info in self.theme_keywords.items():
                # 检查是否匹配关键词
                for keyword in theme_info['keywords']:
                    if keyword in title:
                        theme_hits[theme_name]['count'] += 1
                        theme_hits[theme_name]['news'].append(title)
                        theme_hits[theme_name]['sector'] = theme_info['sector']
                        theme_hits[theme_name]['related_stocks'] = theme_info['related_stocks']
                        break  # 一个新闻只计一次
        
        # 按热度排序
        hot_themes = sorted(
            [(name, data) for name, data in theme_hits.items()],
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        # 打印结果
        for theme, data in hot_themes[:5]:
            if data['count'] > 0:
                print(f"  ✅ {theme} ({data['sector']}): {data['count']}条新闻")
                print(f"     相关股票: {', '.join(data['related_stocks'][:3])}")
        
        return hot_themes
    
    def get_sector_recommendations(self, hot_themes, stock_list):
        """根据热点主题筛选相关股票"""
        print("\n📊 基于热点主题筛选股票...")
        
        recommendations = []
        
        # 获取热点板块（出现次数>=1）
        hot_sectors = []
        for theme, data in hot_themes:
            if data['count'] >= 1:
                hot_sectors.append({
                    'theme': theme,
                    'sector': data['sector'],
                    'count': data['count'],
                    'related_stocks': data['related_stocks']
                })
        
        print(f"  📈 热点板块: {', '.join([s['sector'] for s in hot_sectors])}")
        
        # 从股票列表中筛选相关股票
        if stock_list:
            for stock in stock_list:
                stock_name = stock.get('名称', '')
                stock_code = stock.get('代码', '')
                
                # 检查是否属于热点板块
                for sector_info in hot_sectors:
                    related_stocks = sector_info['related_stocks']
                    
                    # 如果股票名称匹配相关股票
                    if any(related in stock_name for related in related_stocks):
                        recommendation = {
                            **stock,
                            'theme': sector_info['theme'],
                            'sector': sector_info['sector'],
                            'theme_count': sector_info['count'],
                            'recommendation_reason': f"【{sector_info['theme']}】主题热点，相关{sector_info['count']}条新闻"
                        }
                        recommendations.append(recommendation)
                        break
        
        # 如果没有匹配到具体股票，返回板块龙头建议
        if not recommendations and hot_sectors:
            print("  ⚠️  未在股票池中找到相关个股，推荐板块龙头")
            for sector_info in hot_sectors[:3]:
                for stock_name in sector_info['related_stocks'][:2]:
                    recommendations.append({
                        '代码': '待查',
                        '名称': stock_name,
                        'theme': sector_info['theme'],
                        'sector': sector_info['sector'],
                        'theme_count': sector_info['count'],
                        'recommendation_reason': f"【{sector_info['theme']}】板块龙头，相关{sector_info['count']}条新闻"
                    })
        
        print(f"  ✅ 找到{len(recommendations)}只相关股票")
        
        return recommendations, hot_sectors
    
    def generate_theme_report(self, hot_themes, recommendations, hot_sectors):
        """生成主题分析报告"""
        report = []
        report.append("\n" + "=" * 80)
        report.append("📊 主题分析报告")
        report.append("=" * 80)
        
        # 热点主题
        report.append("\n🔥 今日热点主题:")
        for i, (theme, data) in enumerate(hot_themes[:5], 1):
            if data['count'] > 0:
                report.append(f"{i}. {theme} ({data['sector']}) - {data['count']}条新闻")
                if data['news']:
                    report.append(f"   示例: {data['news'][0][:50]}...")
        
        # 板块推荐
        report.append("\n📈 重点板块:")
        for sector_info in hot_sectors[:3]:
            report.append(f"- {sector_info['sector']} ({sector_info['theme']}主题)")
            report.append(f"  推荐关注: {', '.join(sector_info['related_stocks'][:3])}")
        
        # 个股推荐
        if recommendations:
            report.append("\n💡 个股推荐:")
            for i, stock in enumerate(recommendations[:10], 1):
                name = stock.get('名称', 'N/A')
                code = stock.get('代码', 'N/A')
                reason = stock.get('recommendation_reason', '')
                report.append(f"{i}. {code} {name}")
                report.append(f"   {reason}")
        
        return "\n".join(report)
    
    def get_sector_recommendations(self, hot_themes, stock_list):
        """根据热点主题推荐股票"""
        print("\n📊 基于热点主题筛选股票...")
        
        recommendations = []
        hot_sectors = []
        
        # 获取热点板块
        for theme, data in hot_themes[:5]:
            if data['count'] >= 1:
                hot_sectors.append({
                    'theme': theme,
                    'sector': data['sector'],
                    'count': data['count'],
                    'related_stocks': data['related_stocks']
                })
        
        print(f"  📈 热点板块: {', '.join([s['sector'] for s in hot_sectors])}")
        
        # 从股票列表中筛选相关股票
        if stock_list:
            for stock in stock_list:
                stock_name = stock.get('名称', '')
                stock_code = stock.get('代码', '')
                
                # 检查是否属于热点板块
                for sector_info in hot_sectors:
                    related_stocks = sector_info['related_stocks']
                    
                    # 如果股票名称匹配相关股票
                    if any(related in stock_name for related in related_stocks):
                        recommendation = {
                            **stock,
                            'theme': sector_info['theme'],
                            'sector': sector_info['sector'],
                            'theme_count': sector_info['count'],
                            'recommendation_reason': f"【{sector_info['theme']}】主题热点，相关{sector_info['count']}条新闻"
                        }
                        recommendations.append(recommendation)
                        print(f"    ✅ 匹配: {stock_code} {stock_name} ({sector_info['theme']})")
                        break
        
        # 如果没有匹配到具体股票，返回板块龙头建议
        if not recommendations and hot_sectors:
            print("  ⚠️  未在股票池中找到相关个股，推荐板块龙头")
            for sector_info in hot_sectors[:3]:
                for stock_name in sector_info['related_stocks'][:2]:
                    recommendations.append({
                        '代码': '待查',
                        '名称': stock_name,
                        'theme': sector_info['theme'],
                        'sector': sector_info['sector'],
                        'theme_count': sector_info['count'],
                        'recommendation_reason': f"【{sector_info['theme']}】板块龙头，相关{sector_info['count']}条新闻（请验证是否在股票池中）"
                    })
        
        print(f"  ✅ 找到{len(recommendations)}只相关股票")
        
        return recommendations, hot_sectors


def main():
    """测试"""
    # 模拟新闻数据
    test_news = [
        {'title': '史上最大IPO要来了！马斯克旗下SpaceX据悉已递交上市申请'},
        {'title': '1220亿美元！OpenAI完成硅谷史上最高融资，估值8520亿美元'},
        {'title': '美国载人绕月任务火箭发射升空'},
        {'title': '宇树科技、中科宇航被抽中现场检查'}
    ]
    
    mapper = ThemeSectorMapper()
    hot_themes = mapper.identify_themes(test_news)
    recommendations, hot_sectors = mapper.get_sector_recommendations(hot_themes, [])
    report = mapper.generate_theme_report(hot_themes, recommendations, hot_sectors)
    print(report)


if __name__ == '__main__':
    main()
