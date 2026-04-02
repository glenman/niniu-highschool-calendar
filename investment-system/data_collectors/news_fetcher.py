#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版新闻采集器 - 多源新闻抓取
数据源：财联社、新浪财经、东方财富、巨潮资讯网
"""

import urllib.request
import urllib.error
import json
import re
from datetime import datetime
from html.parser import HTMLParser
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class NewsParser(HTMLParser):
    """简单的HTML解析器"""
    
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_link = False
        self.titles = []
        self.current_title = ""
        self.current_href = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.in_link = True
            for attr in attrs:
                if attr[0] == 'href':
                    self.current_href = attr[1]
        elif tag in ['title', 'h1', 'h2', 'h3']:
            self.in_title = True
    
    def handle_data(self, data):
        if self.in_title or self.in_link:
            self.current_title += data.strip()
    
    def handle_endtag(self, tag):
        if tag == 'a':
            if self.current_title and len(self.current_title) > 10:
                self.titles.append({
                    'title': self.current_title,
                    'url': self.current_href
                })
            self.in_link = False
            self.current_title = ""
            self.current_href = ""
        elif tag in ['title', 'h1', 'h2', 'h3']:
            self.in_title = False


class MultiSourceNewsFetcher:
    """多源新闻采集器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.sources = {
            'cls': {
                'name': '财联社',
                'url': 'https://www.cls.cn',
                'priority': 1
            },
            'sina': {
                'name': '新浪财经',
                'url': 'https://finance.sina.com.cn',
                'priority': 2
            },
            'eastmoney': {
                'name': '东方财富',
                'url': 'https://www.eastmoney.com',
                'priority': 3
            },
            'cninfo': {
                'name': '巨潮资讯网',
                'url': 'http://www.cninfo.com.cn',
                'priority': 4
            }
        }
    
    def _fetch_page(self, url):
        """抓取网页内容"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return content
        except Exception as e:
            print(f"❌ 抓取失败 {url}: {e}")
            return None
    
    def fetch_cls_news(self, max_news=20):
        """抓取财联社新闻"""
        print("📰 抓取财联社新闻...")
        try:
            content = self._fetch_page(self.sources['cls']['url'])
            if content:
                # 简单提取标题（实际需要更精确的解析）
                titles = re.findall(r'<a[^>]*>([^<]{10,100})</a>', content)
                news_items = []
                
                for i, title in enumerate(titles[:max_news]):
                    if '财联社' in title or '电报' in title or len(title) > 15:
                        news_items.append({
                            'title': title.strip(),
                            'source': '财联社',
                            'url': self.sources['cls']['url'],
                            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                
                print(f"  ✅ 抓取到{len(news_items)}条")
                return news_items
        except Exception as e:
            print(f"  ❌ 财联社抓取失败: {e}")
        return []
    
    def fetch_sina_news(self, max_news=20):
        """抓取新浪财经新闻"""
        print("📰 抓取新浪财经新闻...")
        try:
            content = self._fetch_page(self.sources['sina']['url'])
            if content:
                titles = re.findall(r'<a[^>]*title="([^"]{10,100})"', content)
                news_items = []
                
                for title in titles[:max_news]:
                    news_items.append({
                        'title': title.strip(),
                        'source': '新浪财经',
                        'url': self.sources['sina']['url'],
                        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                print(f"  ✅ 抓取到{len(news_items)}条")
                return news_items
        except Exception as e:
            print(f"  ❌ 新浪财经抓取失败: {e}")
        return []
    
    def fetch_cninfo_announcements(self, max_news=20):
        """抓取巨潮资讯网公告"""
        print("📰 抓取巨潮资讯网公告...")
        try:
            content = self._fetch_page(self.sources['cninfo']['url'])
            if content:
                # 提取公告标题
                titles = re.findall(r'<a[^>]*>([^<]{10,100}公告[^<]*)</a>', content)
                news_items = []
                
                for title in titles[:max_news]:
                    news_items.append({
                        'title': title.strip(),
                        'source': '巨潮资讯网',
                        'url': self.sources['cninfo']['url'],
                        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                print(f"  ✅ 抓取到{len(news_items)}条")
                return news_items
        except Exception as e:
            print(f"  ❌ 巨潮资讯网抓取失败: {e}")
        return []
    
    def fetch_all_news(self, max_per_source=20):
        """抓取所有新闻源"""
        print("\n" + "=" * 60)
        print("🦞 开始多源新闻采集")
        print("=" * 60)
        
        all_news = []
        
        # 财联社
        cls_news = self.fetch_cls_news(max_per_source)
        all_news.extend(cls_news)
        
        # 新浪财经
        sina_news = self.fetch_sina_news(max_per_source)
        all_news.extend(sina_news)
        
        # 巨潮资讯网
        cninfo_news = self.fetch_cninfo_announcements(max_per_source)
        all_news.extend(cninfo_news)
        
        print("\n" + "-" * 60)
        print(f"✅ 总计抓取{len(all_news)}条新闻")
        
        return all_news


def main():
    """主函数"""
    fetcher = MultiSourceNewsFetcher()
    news = fetcher.fetch_all_news(max_per_source=20)
    
    # 保存到文件
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = "memory/investment/daily"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/news_{today}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    
    print(f"📁 新闻已保存到: {output_file}")
    
    # 显示示例
    if news:
        print("\n📰 新闻示例（前5条）:")
        for i, item in enumerate(news[:5], 1):
            print(f"{i}. [{item['source']}] {item['title'][:50]}...")
    
    return news


if __name__ == '__main__':
    main()
