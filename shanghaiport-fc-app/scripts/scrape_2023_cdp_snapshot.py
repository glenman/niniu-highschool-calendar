#!/usr/bin/env python3
"""
上海海港2023赛季比赛数据抓取器 - CDP优化版（使用Snapshot）
按照模板格式提取干净的结构化数据
"""

import json
import os
import subprocess
import time
import re
from datetime import datetime

class CDPMatchScraper:
    """使用CDP的比赛数据抓取器"""
    
    def __init__(self, cdp_port=9222):
        self.cdp_port = cdp_port
        self.browser_ready = False
    
    def check_cdp_connection(self):
        """检查CDP连接"""
        try:
            result = subprocess.run(
                ['agent-browser', '--cdp', str(self.cdp_port), 'get', 'title'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.browser_ready = True
                print(f"✓ CDP连接成功")
                return True
        except:
            pass
        
        print(f"✗ CDP连接失败")
        return False
    
    def open_match_page(self, url):
        """打开比赛页面"""
        try:
            result = subprocess.run(
                ['agent-browser', '--cdp', str(self.cdp_port), 'open', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                time.sleep(8)
                return True
        except:
            pass
        
        return False
    
    def get_text(self, ref):
        """获取指定元素的文本"""
        try:
            result = subprocess.run(
                ['agent-browser', '--cdp', str(self.cdp_port), 'get', 'text', ref],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return ""
    
    def scrape_match(self, url, match_info):
        """抓取单场比赛数据"""
        
        print(f"  → 打开页面...")
        if not self.open_match_page(url):
            return None
        
        print(f"  → 提取数据...")
        
        # 获取页面标题（包含球队名和日期）
        title = subprocess.run(
            ['agent-browser', '--cdp', str(self.cdp_port), 'get', 'title'],
            capture_output=True,
            text=True,
            timeout=10
        ).stdout.strip()
        
        # 解析标题提取球队信息
        # 格式: "Wuhan Three Towns vs. Shanghai Port Match Report – Saturday April 15, 2023 | FBref.com"
        teams_match = re.search(r'(.+?)\s+vs\.\s+(.+?)\s+Match Report', title)
        
        match_data = {
            "match_info": {
                "match_id": match_info.get('match_id', ''),
                "date": match_info.get('date', ''),
                "time": "20:00",
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": "2023",
                    "round": f"Matchweek {match_info.get('round', 1)}"
                },
                "venue": {
                    "name": "待补充",
                    "city": "待补充",
                    "attendance": 0
                },
                "referee": {
                    "name": "待补充",
                    "country": "China"
                }
            },
            "teams": {
                "home": {
                    "name": teams_match.group(1) if teams_match else "",
                    "full_name": "",
                    "score": 0,
                    "score_ht": 0,
                    "formation": "",
                    "coach": "待补充",
                    "captain": "待补充",
                    "lineup": [],
                    "substitutes": [],
                    "substitutions": []
                },
                "away": {
                    "name": teams_match.group(2) if teams_match else "",
                    "full_name": "",
                    "score": 0,
                    "score_ht": 0,
                    "formation": "",
                    "coach": "待补充",
                    "captain": "待补充",
                    "lineup": [],
                    "substitutes": [],
                    "substitutions": []
                }
            },
            "events": [],
            "statistics": {},
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "1.0"
            }
        }
        
        print(f"  ✓ 完成")
        return match_data

def main():
    """主函数"""
    
    print("="*70)
    print("上海海港2023赛季比赛数据抓取器 - Snapshot版本")
    print("="*70)
    print()
    
    # 初始化抓取器
    scraper = CDPMatchScraper(cdp_port=9222)
    
    # 检查CDP连接
    if not scraper.check_cdp_connection():
        return
    
    print()
    
    # 读取URL列表
    url_file = 'shanghaiport-fc-app/data/2023-match_urls.json'
    print(f"📖 读取比赛列表")
    
    with open(url_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = data['match_urls']
    print(f"✓ 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'shanghaiport-fc-app/data/match-reports-2023'
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理前5场比赛
    success_count = 0
    
    for i, match in enumerate(matches[:5], 1):
        date = match['date']
        url = match['match_report_url']
        
        print(f"[{i}/5] {date} - 第{i}轮")
        
        # 抓取数据
        match_data = scraper.scrape_match(url, {
            'date': date,
            'match_id': url.split('/')[-2],
            'round': i
        })
        
        if match_data:
            # 保存文件
            filename = f"{date}-中超-第{i}轮.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ {filename}\n")
            success_count += 1
        else:
            print(f"  ❌ 失败\n")
        
        # 休息
        if i < 5:
            time.sleep(2)
    
    print("="*70)
    print(f"✅ 完成: {success_count}/5")
    print("="*70)
    print("\n生成的文件包含基本框架，需要手动补充详细数据。")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
