#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研报采集器 - 抓取免费研报列表
数据源：东方财富研报中心、新浪财经研报、中财网
"""

import urllib.request
import urllib.error
import json
import re
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class ReportFetcher:
    """研报采集器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.sources = {
            'eastmoney': {
                'name': '东方财富研报中心',
                'url': 'http://data.eastmoney.com/report/',
                'priority': 1
            },
            'sina': {
                'name': '新浪财经研报',
                'url': 'https://stock.finance.sina.com.cn/stock/go.php/vReportList/kind/search/index.phtml',
                'priority': 2
            },
            'cfi': {
                'name': '中财网研报',
                'url': 'http://www.cfi.net.cn',
                'priority': 3
            }
        }
    
    def _fetch_page(self, url):
        """抓取网页"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return content
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            return None
    
    def fetch_eastmoney_reports(self, max_reports=20):
        """抓取东方财富研报"""
        print("📊 抓取东方财富研报...")
        try:
            content = self._fetch_page(self.sources['eastmoney']['url'])
            if content:
                # 提取研报标题（简化版，实际需要更精确的解析）
                titles = re.findall(r'<a[^>]*>([^<]{15,100}研报[^<]*)</a>', content)
                reports = []
                
                for title in titles[:max_reports]:
                    # 尝试提取股票名称和评级
                    report = {
                        'title': title.strip(),
                        'source': '东方财富研报中心',
                        'url': self.sources['eastmoney']['url'],
                        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'stock': '',
                        'rating': ''
                    }
                    
                    # 尝试提取股票代码
                    code_match = re.search(r'(\d{6})', title)
                    if code_match:
                        report['stock'] = code_match.group(1)
                    
                    # 尝试提取评级
                    if '买入' in title:
                        report['rating'] = '买入'
                    elif '增持' in title:
                        report['rating'] = '增持'
                    elif '中性' in title:
                        report['rating'] = '中性'
                    
                    reports.append(report)
                
                print(f"  ✅ 抓取到{len(reports)}份研报")
                return reports
        except Exception as e:
            print(f"  ❌ 东方财富研报抓取失败: {e}")
        return []
    
    def fetch_sina_reports(self, max_reports=20):
        """抓取新浪财经研报"""
        print("📊 抓取新浪财经研报...")
        try:
            content = self._fetch_page(self.sources['sina']['url'])
            if content:
                titles = re.findall(r'<a[^>]*title="([^"]{15,100})"', content)
                reports = []
                
                for title in titles[:max_reports]:
                    report = {
                        'title': title.strip(),
                        'source': '新浪财经研报',
                        'url': self.sources['sina']['url'],
                        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'stock': '',
                        'rating': ''
                    }
                    
                    # 提取股票代码
                    code_match = re.search(r'(\d{6})', title)
                    if code_match:
                        report['stock'] = code_match.group(1)
                    
                    # 提取评级
                    if '买入' in title:
                        report['rating'] = '买入'
                    elif '增持' in title:
                        report['rating'] = '增持'
                    elif '推荐' in title:
                        report['rating'] = '推荐'
                    
                    reports.append(report)
                
                print(f"  ✅ 抓取到{len(reports)}份研报")
                return reports
        except Exception as e:
            print(f"  ❌ 新浪财经研报抓取失败: {e}")
        return []
    
    def fetch_all_reports(self, max_per_source=20):
        """抓取所有研报源"""
        print("\n" + "=" * 60)
        print("🦞 开始研报采集")
        print("=" * 60)
        
        all_reports = []
        
        # 东方财富研报
        eastmoney_reports = self.fetch_eastmoney_reports(max_per_source)
        all_reports.extend(eastmoney_reports)
        
        # 新浪财经研报
        sina_reports = self.fetch_sina_reports(max_per_source)
        all_reports.extend(sina_reports)
        
        print("\n" + "-" * 60)
        print(f"✅ 总计抓取{len(all_reports)}份研报")
        
        return all_reports


def main():
    """主函数"""
    fetcher = ReportFetcher()
    reports = fetcher.fetch_all_reports(max_per_source=20)
    
    # 保存
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = "memory/investment/daily"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/reports_{today}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    print(f"📁 研报已保存到: {output_file}")
    
    # 显示示例
    if reports:
        print("\n📊 研报示例（前5份）:")
        for i, item in enumerate(reports[:5], 1):
            print(f"{i}. [{item['source']}] {item['title'][:50]}...")
    
    return reports


if __name__ == '__main__':
    main()
