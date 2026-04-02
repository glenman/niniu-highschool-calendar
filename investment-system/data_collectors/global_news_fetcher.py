#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海外新闻采集器 V2 - 基于测试结果优化
测试日期：2026-04-01
成功率：54% (7/13)
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
    """海外新闻采集器 - 优化版"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 配置代理（7898混合端口）
        self.use_proxy = True
        self.proxy_port = 7898
        
        # ========================================
        # 时政新闻源（基于2026-04-01测试结果）
        # ========================================
        # 测试成功：3/7 (43%)
        self.political_sources = {
            # ✅ 测试成功（0.74s，331KB）
            'bbc': {
                'name': 'BBC News',
                'url': 'https://www.bbc.com/news',
                'priority': 1,
                'region': 'UK',
                'use_proxy': True,
                'proxy_port': 7898
            },
            # ✅ 测试成功（1.24s，1.3MB）
            'ap': {
                'name': 'Associated Press',
                'url': 'https://apnews.com',
                'priority': 1,
                'region': 'US',
                'use_proxy': True,
                'proxy_port': 7898
            },
            # ✅ 测试成功（1.29s，400KB）
            'aljazeera': {
                'name': 'Al Jazeera',
                'url': 'https://www.aljazeera.com',
                'priority': 2,
                'region': 'Middle East',
                'use_proxy': True,
                'proxy_port': 7898
            },
            # ✅ 之前测试成功
            'google_news': {
                'name': 'Google News',
                'url': 'https://news.google.com',
                'priority': 1,
                'region': 'Global',
                'use_proxy': True,
                'proxy_port': 7898
            }
            # ❌ CNN: URLError
            # ❌ Reuters: 401
            # ❌ NY Times: URLError
            # ❌ The Guardian: URLError
        }
        
        # ========================================
        # 财经新闻源（基于2026-04-01测试结果）
        # ========================================
        # 测试成功：4/6 (67%)
        self.financial_sources = {
            # ✅ 测试成功（2.15s，360KB）
            'ft': {
                'name': 'Financial Times',
                'url': 'https://www.ft.com',
                'priority': 1,
                'region': 'UK',
                'use_proxy': True,
                'proxy_port': 7898
            },
            # ✅ 测试成功（2.42s，714KB）
            'economist': {
                'name': 'The Economist',
                'url': 'https://www.economist.com',
                'priority': 1,
                'region': 'UK',
                'use_proxy': True,
                'proxy_port': 7898
            },
            # ✅ 测试成功（2.73s，1.6MB）
            'cnbc': {
                'name': 'CNBC',
                'url': 'https://www.cnbc.com',
                'priority': 1,
                'region': 'US',
                'use_proxy': True,
                'proxy_port': 7898
            },
            # ✅ 测试成功（1.78s，743KB）
            'forbes': {
                'name': 'Forbes',
                'url': 'https://www.forbes.com',
                'priority': 2,
                'region': 'US',
                'use_proxy': True,
                'proxy_port': 7898
            }
            # ❌ WSJ: 401
            # ❌ Bloomberg: 403
        }
    
    def _fetch_page(self, url, use_proxy=False, proxy_port=None, timeout=12, max_retries=5):
        """抓取网页（支持代理 + 5次重试）"""
        port = proxy_port or self.proxy_port
        
        for attempt in range(max_retries):
            try:
                if use_proxy and self.use_proxy:
                    # 使用代理
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
                if attempt < max_retries - 1:
                    continue  # 重试
                return None
            except urllib.error.URLError as e:
                if attempt < max_retries - 1:
                    continue  # 重试
                return None
            except Exception as e:
                if attempt < max_retries - 1:
                    continue  # 重试
                return None
        
        return None
    
    def _extract_headlines(self, content, source_name):
        """提取标题"""
        if not content:
            return []
        
        try:
            titles = re.findall(r'<title>([^<]{20,200})</title>', content)
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
        except Exception:
            return []
    
    def fetch_political_news(self):
        """抓取时政新闻（用于内部分析，不直接发送）"""
        print("\n🌍 抓取海外时政新闻...")
        all_news = []
        success_count = 0
        fail_count = 0
        
        for source_id, source_info in self.political_sources.items():
            print(f"  📰 {source_info['name']}...", end='')
            use_proxy = source_info.get('use_proxy', False)
            proxy_port = source_info.get('proxy_port', self.proxy_port)
            # 重试5次
            content = self._fetch_page(source_info['url'], use_proxy=use_proxy, proxy_port=proxy_port, max_retries=5)
            
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
                print(" ❌ 失败（重试5次后）")
                fail_count += 1
        
        print(f"  ✅ 时政新闻总计: {len(all_news)}条 (成功{success_count}/{success_count+fail_count})")
        return all_news
    
    def fetch_financial_news(self):
        """抓取财经新闻（用于内部分析，不直接发送）"""
        print("\n💰 抓取海外财经新闻...")
        all_news = []
        success_count = 0
        fail_count = 0
        
        for source_id, source_info in self.financial_sources.items():
            print(f"  📰 {source_info['name']}...", end='')
            use_proxy = source_info.get('use_proxy', False)
            proxy_port = source_info.get('proxy_port', self.proxy_port)
            # 重试5次
            content = self._fetch_page(source_info['url'], use_proxy=use_proxy, proxy_port=proxy_port, max_retries=5)
            
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
                print(" ❌ 失败（重试5次后）")
                fail_count += 1
        
        print(f"  ✅ 财经新闻总计: {len(all_news)}条 (成功{success_count}/{success_count+fail_count})")
        return all_news
    
    def fetch_all_global_news(self):
        """抓取所有海外新闻（仅供内部学习分析使用）"""
        print("\n" + "=" * 60)
        print("🌏 开始海外新闻采集（用于内部分析）")
        print("=" * 60)
        
        political_news = self.fetch_political_news()
        financial_news = self.fetch_financial_news()
        
        all_news = political_news + financial_news
        
        print("\n" + "-" * 60)
        print(f"✅ 海外新闻总计: {len(all_news)}条")
        print("📊 新闻将用于：市场分析 + 情绪判断 + 荐股决策")
        
        return all_news


def main():
    """主函数 - 仅供内部调用，不直接展示给用户"""
    fetcher = GlobalNewsFetcher()
    news = fetcher.fetch_all_global_news()
    
    # 保存到知识库（供后续分析使用）
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = "memory/investment/daily"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/global_news_{today}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 新闻已归档到知识库: {output_file}")
    print("💡 系统将基于这些新闻进行内部分析，生成荐股建议")
    
    return news


if __name__ == '__main__':
    main()
