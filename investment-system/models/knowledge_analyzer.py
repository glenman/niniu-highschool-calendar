# 智能知识分析器 - 新闻分类与趋势分析

import json
import os
from datetime import datetime
from collections import defaultdict
import re


class KnowledgeAnalyzer:
    """知识分析与积累系统"""
    
    def __init__(self):
        self.knowledge_base = "memory/investment/knowledge"
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.month = datetime.now().strftime('%Y-%m')
        
        # 关键词规则
        self.category_rules = {
            'macro': ['央行', 'GDP', 'CPI', '利率', '货币政策', '财政', '经济', '通胀'],
            'policy': ['政策', '国务院', '发改委', '监管', '改革', '规划', '意见'],
            'industry': ['行业', '板块', '产业链', '供需', '产能', '竞争'],
            'market': ['指数', '涨跌', '涨停', '跌停', '成交', '资金', '北向'],
            'company': ['公司', '业绩', '财报', '盈利', '亏损', '重组']
        }
        
        self.sentiment_keywords = {
            'positive': ['涨', '增', '突破', '利好', '爆发', '回暖', '增长', '盈利'],
            'negative': ['跌', '降', '亏损', '利空', '暴跌', '下滑', '风险'],
            'neutral': ['公布', '显示', '报告', '称', '表示']
        }
    
    def classify_news(self, news_item):
        """分类新闻"""
        title = news_item.get('title', '')
        
        # 主题分类
        category_scores = defaultdict(int)
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in title:
                    category_scores[category] += 1
        
        # 选择得分最高的分类
        if category_scores:
            category = max(category_scores.items(), key=lambda x: x[1])[0]
        else:
            category = 'market'  # 默认市场类
        
        # 情绪分析
        sentiment_scores = defaultdict(int)
        for sentiment, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                if keyword in title:
                    sentiment_scores[sentiment] += 1
        
        if sentiment_scores:
            sentiment = max(sentiment_scores.items(), key=lambda x: x[1])[0]
        else:
            sentiment = 'neutral'
        
        # 提取关联股票代码
        stock_codes = re.findall(r'\d{6}', title)
        
        return {
            'category': category,
            'sentiment': sentiment,
            'related_stocks': stock_codes,
            'keywords': self._extract_keywords(title)
        }
    
    def _extract_keywords(self, text, max_keywords=5):
        """提取关键词（简化版）"""
        # 常见停用词
        stop_words = {'的', '了', '在', '是', '有', '和', '等', '中', '为', '以', '及'}
        
        # 简单分词（按空格和标点）
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        
        # 过滤停用词
        keywords = [w for w in words if w not in stop_words and len(w) >= 2]
        
        return keywords[:max_keywords]
    
    def analyze_and_archive(self, news_list):
        """分析并归档新闻"""
        print(f"📚 开始分析{len(news_list)}条新闻...")
        
        # 按分类组织
        categorized_news = defaultdict(list)
        
        for news in news_list:
            analysis = self.classify_news(news)
            
            # 合并原始信息和分析结果
            enriched_news = {
                **news,
                **analysis,
                'archived_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            categorized_news[analysis['category']].append(enriched_news)
        
        # 保存到知识库
        self._save_to_knowledge_base(categorized_news)
        
        # 更新趋势指标
        self._update_trends(categorized_news)
        
        print(f"✅ 新闻已归档到知识库")
        
        return categorized_news
    
    def _save_to_knowledge_base(self, categorized_news):
        """保存到知识库"""
        # 创建月份目录
        month_dir = f"{self.knowledge_base}/news_archive/{self.month}"
        os.makedirs(month_dir, exist_ok=True)
        
        # 按分类保存
        for category, news_items in categorized_news.items():
            category_file = f"{month_dir}/{category}_{self.today}.json"
            
            # 读取已有数据
            existing = []
            if os.path.exists(category_file):
                with open(category_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            
            # 合并新数据
            existing.extend(news_items)
            
            # 保存
            with open(category_file, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            
            print(f"  📁 {category}: {len(news_items)}条")
    
    def _update_trends(self, categorized_news):
        """更新趋势指标"""
        trend_file = f"{self.knowledge_base}/trends/daily_trends.json"
        
        # 读取已有趋势数据
        trends = {}
        if os.path.exists(trend_file):
            with open(trend_file, 'r', encoding='utf-8') as f:
                trends = json.load(f)
        
        # 计算今日指标
        today_trend = {
            'date': self.today,
            'news_count': sum(len(items) for items in categorized_news.values()),
            'categories': {},
            'sentiment_score': 0,
            'hot_topics': []
        }
        
        # 各分类数量
        for category, items in categorized_news.items():
            today_trend['categories'][category] = len(items)
        
        # 情绪得分（positive=1, negative=-1, neutral=0）
        sentiment_sum = 0
        for items in categorized_news.values():
            for item in items:
                if item['sentiment'] == 'positive':
                    sentiment_sum += 1
                elif item['sentiment'] == 'negative':
                    sentiment_sum -= 1
        
        total = today_trend['news_count']
        today_trend['sentiment_score'] = sentiment_sum / max(total, 1)
        
        # 热门主题（关键词频率）
        keyword_freq = defaultdict(int)
        for items in categorized_news.values():
            for item in items:
                for keyword in item['keywords']:
                    keyword_freq[keyword] += 1
        
        today_trend['hot_topics'] = sorted(
            keyword_freq.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # 更新趋势文件
        trends[self.today] = today_trend
        
        with open(trend_file, 'w', encoding='utf-8') as f:
            json.dump(trends, f, ensure_ascii=False, indent=2)
        
        print(f"📊 趋势指标已更新: 情绪得分={today_trend['sentiment_score']:.2f}")
    
    def analyze_sector_rotation(self):
        """分析板块轮动"""
        trend_file = f"{self.knowledge_base}/trends/daily_trends.json"
        
        if not os.path.exists(trend_file):
            print("⚠️ 趋势数据不足，无法分析板块轮动")
            return None
        
        with open(trend_file, 'r', encoding='utf-8') as f:
            trends = json.load(f)
        
        # 分析最近7天的热门主题变化
        recent_dates = sorted(trends.keys())[-7:]
        
        rotation = {
            'rising_sectors': [],
            'falling_sectors': [],
            'persistent_sectors': []
        }
        
        # 简单分析（需要更复杂的逻辑）
        for date in recent_dates:
            if 'hot_topics' in trends[date]:
                for topic, freq in trends[date]['hot_topics'][:3]:
                    rotation['rising_sectors'].append(topic)
        
        return rotation


def main():
    """主函数"""
    # 读取今日新闻
    news_file = f"memory/investment/daily/news_{datetime.now().strftime('%Y-%m-%d')}.json"
    
    if not os.path.exists(news_file):
        print("❌ 今日新闻数据不存在，请先运行新闻采集")
        return
    
    with open(news_file, 'r', encoding='utf-8') as f:
        news_list = json.load(f)
    
    # 分析并归档
    analyzer = KnowledgeAnalyzer()
    categorized = analyzer.analyze_and_archive(news_list)
    
    # 分析板块轮动
    rotation = analyzer.analyze_sector_rotation()
    if rotation:
        print(f"\n📈 板块轮动分析:")
        print(f"  热门板块: {', '.join(set(rotation['rising_sectors'][:5]))}")


if __name__ == '__main__':
    main()
