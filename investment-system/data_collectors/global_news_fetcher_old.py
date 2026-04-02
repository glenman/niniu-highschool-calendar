#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海外新闻采集器 - 时政+财经新闻
容错机制：失败不影响整体运行
"""

import urllib.request
import urllib.error
import json
import re
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class GlobalNewsFetcher:
    """海外新闻采集器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 配置代理（使用7900 HTTP/HTTPS端口）
        self.use_proxy = True
        self.proxy_port = 7900  # 改用7900端口（更快更稳定）
        
        # 时政新闻源（优化后）
        self.political_sources = {
            'bbc': {
                'name': 'BBC News',
                'url': 'https://www.bbc.com/news',
                'priority': 1,
                'region': 'UK',
                'use_proxy': True
            },
            'cnn': {
                'name': 'CNN',
                'url': 'https://edition.cnn.com',
                'priority': 1,
                'region': 'US',
                'use_proxy': False
            },
            'google_news': {
                'name': 'Google News',
                'url': 'https://news.google.com',
                'priority': 1,
                'region': 'Global',
                'use_proxy': True
            }
        }
        
        # 财经新闻源（优化后）
        self.financial_sources = {
            'cnbc': {
                'name': 'CNBC',
                'url': 'https://www.cnbc.com',
                'priority': 1,
                'region': 'US',
                'use_proxy': False
            },
            'google_finance': {
                'name': 'Google Finance',
                'url': 'https://www.google.com/finance',
                'priority': 1,
                'region': 'Global',
                'use_proxy': True
            }
        }
    
    def _fetch_page(self, url, use_proxy=False, proxy_port=None, timeout=12):
        """抓取网页（支持代理）"""
        try:
            if use_proxy and self.use_proxy:
                # 使用代理
                port = proxy_port or self.proxy_port
                proxy_handler = urllib.request.ProxyHandler({
                    'http': f'http://127.0.0.1:{port}',
                    'https': f'http://127.0.0.1:{port}'
                })
                opener = urllib.request.build_opener(proxy_handler)
                req = urllib.request.Request(url, headers=self.headers)
                with opener.open(req, timeout=timeout) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    return content
            else:
                # 直接访问
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    return content
        except urllib.error.HTTPError as e:
            return None
        except urllib.error.URLError as e:
            return None
        except Exception as e:
            return None
    
    def _extract_headlines(self, content, source_name):
        """提取标题（通用方法）"""
        if not content:
            return []
        
        try:
            # 简单提取标题（实际需要针对不同网站优化）
            titles = re.findall(r'<title>([^<]{20,200})</title>', content)
            
            # 提取a标签中的文本
            headlines = re.findall(r'<a[^>]*>([^<]{20,150})</a>', content)
            
            news_items = []
            for title in (titles + headlines)[:10]:
                if len(title.strip()) > 20:
                    news_items.append({
                        'title': title.strip(),
                        'source': source_name,
                        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'category': 'global'
                    })
            
            return news_items
        except Exception as e:
            print(f"    ⚠️ 解析失败: {e}")
            return []
    
    def fetch_political_news(self):
        """抓取时政新闻"""
        print("\n🌍 抓取海外时政新闻...")
        all_news = []
        success_count = 0
        fail_count = 0
        
        for source_id, source_info in self.political_sources.items():
            print(f"  📰 {source_info['name']}...", end='')
            use_proxy = source_info.get('use_proxy', False)
            proxy_port = source_info.get('proxy_port', self.proxy_port)
            content = self._fetch_page(source_info['url'], use_proxy=use_proxy, proxy_port=proxy_port)
            
            if content:
                headlines = self._extract_headlines(content, source_info['name'])
                if headlines:
                    print(f" ✅ {len(headlines)}条")
                    all_news.extend(headlines)
                    success_count += 1
                else:
                    print(" ⚠️ 无数据")
                    fail_count += 1
            else:
                print(" ❌ 失败")
                fail_count += 1
        
        print(f"  ✅ 时政新闻总计: {len(all_news)}条 (成功{success_count}/{success_count+fail_count})")
        return all_news
    
    def fetch_financial_news(self):
        """抓取财经新闻"""
        print("\n💰 抓取海外财经新闻...")
        all_news = []
        success_count = 0
        fail_count = 0
        
        for source_id, source_info in self.financial_sources.items():
            print(f"  📰 {source_info['name']}...", end='')
            use_proxy = source_info.get('use_proxy', False)
            proxy_port = source_info.get('proxy_port', self.proxy_port)
            content = self._fetch_page(source_info['url'], use_proxy=use_proxy, proxy_port=proxy_port)
            
            if content:
                headlines = self._extract_headlines(content, source_info['name'])
                if headlines:
                    print(f" ✅ {len(headlines)}条")
                    all_news.extend(headlines)
                    success_count += 1
                else:
                    print(" ⚠️ 无数据")
                    fail_count += 1
            else:
                print(" ❌ 失败")
                fail_count += 1
        
        print(f"  ✅ 财经新闻总计: {len(all_news)}条 (成功{success_count}/{success_count+fail_count})")
        return all_news
    
    def fetch_all_global_news(self):
        """抓取所有海外新闻"""
        print("\n" + "=" * 60)
        print("🌏 开始海外新闻采集")
        print("=" * 60)
        
        political_news = self.fetch_political_news()
        financial_news = self.fetch_financial_news()
        
        all_news = political_news + financial_news
        
        print("\n" + "-" * 60)
        print(f"✅ 海外新闻总计: {len(all_news)}条")
        
        return all_news


def main():
    """主函数"""
    fetcher = GlobalNewsFetcher()
    news = fetcher.fetch_all_global_news()
    
    # 保存
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = "memory/investment/daily"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/global_news_{today}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 海外新闻已保存到: {output_file}")
    
    # 显示示例
    if news:
        print("\n📰 海外新闻示例（前5条）:")
        for i, item in enumerate(news[:5], 1):
            print(f"{i}. [{item['source']}] {item['title'][:60]}...")
    
    return news


if __name__ == '__main__':
    main()
