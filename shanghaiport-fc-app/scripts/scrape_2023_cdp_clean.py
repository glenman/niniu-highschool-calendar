#!/usr/bin/env python3
"""
上海海港2023赛季比赛数据抓取器 - CDP版本（优化版）
按照模板格式提取干净的数据
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
                print(f"✓ CDP连接成功 (端口 {self.cdp_port})")
                return True
        except:
            pass
        
        print(f"✗ CDP连接失败")
        print("\n请确保Chrome已启动远程调试模式:")
        print("  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
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
    
    def extract_text(self):
        """提取干净的文本内容"""
        try:
            result = subprocess.run(
                ['agent-browser', '--cdp', str(self.cdp_port), 'eval', 
                 'document.body.textContent'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                return result.stdout
        except:
            pass
        
        return ""
    
    def scrape_match(self, url, match_info):
        """抓取单场比赛数据"""
        
        print(f"  → 打开页面...")
        if not self.open_match_page(url):
            return None
        
        print(f"  → 提取数据...")
        text = self.extract_text()
        
        if not text:
            return None
        
        # 解析数据
        match_data = {
            "match_info": self._extract_match_info(text, match_info),
            "teams": self._extract_teams(text, match_info),
            "events": self._extract_events(text),
            "statistics": self._extract_statistics(text),
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
    
    def _extract_match_info(self, text, match_info):
        """提取比赛基本信息"""
        info = {
            "match_id": match_info.get('match_id', ''),
            "date": match_info.get('date', ''),
            "time": "20:00",
            "competition": {
                "name": "Chinese Football Association Super League",
                "season": "2023",
                "round": f"Matchweek {match_info.get('round', 1)}"
            },
            "venue": {
                "name": "",
                "city": "",
                "attendance": 0
            },
            "referee": {
                "name": "",
                "country": "China"
            }
        }
        
        # 提取球场（简化，避免HTML垃圾）
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'Venue:' in line:
                venue_text = line.replace('Venue:', '').strip()
                # 只保留球场名称，去除后面的垃圾
                venue_text = venue_text.split('Officials')[0].strip()
                venue_text = re.sub(r'\s+', ' ', venue_text)
                
                # 尝试分离城市
                if ',' in venue_text:
                    parts = venue_text.split(',')
                    info['venue']['name'] = parts[0].strip()
                    if len(parts) > 1:
                        info['venue']['city'] = parts[1].strip().split()[0]
                else:
                    info['venue']['name'] = venue_text
                break
        
        # 提取观众
        attendance_match = re.search(r'Attendance:\s*([\d,]+)', text)
        if attendance_match:
            info['venue']['attendance'] = int(attendance_match.group(1).replace(',', ''))
        
        # 提取裁判
        referee_match = re.search(r'Referee:\s*([^\n,·]+)', text)
        if referee_match:
            info['referee']['name'] = referee_match.group(1).strip()
        
        return info
    
    def _extract_teams(self, text, match_info):
        """提取球队信息"""
        teams = {
            "home": {
                "name": "",
                "full_name": "",
                "score": 0,
                "score_ht": 0,
                "formation": "",
                "coach": "",
                "captain": "",
                "lineup": [],
                "substitutes": [],
                "substitutions": []
            },
            "away": {
                "name": "",
                "full_name": "",
                "score": 0,
                "score_ht": 0,
                "formation": "",
                "coach": "",
                "captain": "",
                "lineup": [],
                "substitutes": [],
                "substitutions": []
            }
        }
        
        # 提取教练
        manager_matches = re.findall(r'Manager:\s*([^\n]+)', text)
        if len(manager_matches) >= 2:
            teams['home']['coach'] = manager_matches[0].strip()
            teams['away']['coach'] = manager_matches[1].strip()
        
        # 提取队长
        captain_matches = re.findall(r'Captain:\s*([^\n]+)', text)
        if len(captain_matches) >= 2:
            teams['home']['captain'] = captain_matches[0].strip()
            teams['away']['captain'] = captain_matches[1].strip()
        
        # 提取阵型
        formation_match = re.search(r'\((\d+-\d+-\d+)\)', text)
        if formation_match:
            teams['home']['formation'] = formation_match.group(1)
        
        return teams
    
    def _extract_events(self, text):
        """提取比赛事件"""
        events = []
        return events
    
    def _extract_statistics(self, text):
        """提取统计数据"""
        stats = {}
        
        # 控球率
        possession_match = re.search(r'Possession.*?(\d+)%.*?(\d+)%', text, re.DOTALL)
        if possession_match:
            stats['possession'] = {
                'home': int(possession_match.group(1)),
                'away': int(possession_match.group(2))
            }
        
        # 射门
        shots_match = re.search(r'Shots.*?(\d+).*?(\d+)', text, re.DOTALL)
        if shots_match:
            stats['shots'] = {
                'home': int(shots_match.group(1)),
                'away': int(shots_match.group(2))
            }
        
        # 射正
        sot_match = re.search(r'Shots on Target.*?(\d+).*?(\d+)', text, re.DOTALL)
        if sot_match:
            stats['shots_on_target'] = {
                'home': int(sot_match.group(1)),
                'away': int(sot_match.group(2))
            }
        
        # 扑救
        saves_match = re.search(r'Saves.*?(\d+).*?(\d+)', text, re.DOTALL)
        if saves_match:
            stats['saves'] = {
                'home': int(saves_match.group(1)),
                'away': int(saves_match.group(2))
            }
        
        # 犯规
        fouls_match = re.search(r'Fouls.*?(\d+).*?(\d+)', text, re.DOTALL)
        if fouls_match:
            stats['fouls'] = {
                'home': int(fouls_match.group(1)),
                'away': int(fouls_match.group(2))
            }
        
        # 角球
        corners_match = re.search(r'Corners.*?(\d+).*?(\d+)', text, re.DOTALL)
        if corners_match:
            stats['corners'] = {
                'home': int(corners_match.group(1)),
                'away': int(corners_match.group(2))
            }
        
        # 传中
        crosses_match = re.search(r'Crosses.*?(\d+).*?(\d+)', text, re.DOTALL)
        if crosses_match:
            stats['crosses'] = {
                'home': int(crosses_match.group(1)),
                'away': int(crosses_match.group(2))
            }
        
        # 拦截
        interceptions_match = re.search(r'Interceptions.*?(\d+).*?(\d+)', text, re.DOTALL)
        if interceptions_match:
            stats['interceptions'] = {
                'home': int(interceptions_match.group(1)),
                'away': int(interceptions_match.group(2))
            }
        
        # 越位
        offsides_match = re.search(r'Offsides.*?(\d+).*?(\d+)', text, re.DOTALL)
        if offsides_match:
            stats['offsides'] = {
                'home': int(offsides_match.group(1)),
                'away': int(offsides_match.group(2))
            }
        
        # 黄牌和红牌
        stats['yellow_cards'] = {'home': 0, 'away': 0}
        stats['red_cards'] = {'home': 0, 'away': 0}
        
        return stats

def main():
    """主函数"""
    
    print("="*70)
    print("上海海港2023赛季比赛数据抓取器 - CDP优化版")
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
    print(f"📖 读取比赛列表: {url_file}")
    
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
            time.sleep(3)
    
    print("="*70)
    print(f"✅ 完成: {success_count}/5")
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
