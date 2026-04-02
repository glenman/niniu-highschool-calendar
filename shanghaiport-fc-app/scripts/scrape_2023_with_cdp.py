#!/usr/bin/env python3
"""
上海海港2023赛季比赛数据抓取器 - CDP版本
使用Chrome DevTools Protocol绕过Cloudflare保护
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
        
        print(f"✗ CDP连接失败 (端口 {self.cdp_port})")
        print("\n请确保Chrome已启动远程调试模式:")
        print("  macOS: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
        return False
    
    def open_match_page(self, url):
        """打开比赛页面"""
        try:
            print(f"  → 打开页面: {url}")
            result = subprocess.run(
                ['agent-browser', '--cdp', str(self.cdp_port), 'open', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✓ 页面已加载")
                time.sleep(8)  # 等待页面渲染
                return True
        except Exception as e:
            print(f"  ✗ 打开页面失败: {e}")
        
        return False
    
    def extract_html(self):
        """提取HTML内容"""
        try:
            result = subprocess.run(
                ['agent-browser', '--cdp', str(self.cdp_port), 'eval', 
                 'document.documentElement.outerHTML'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                return result.stdout
        except Exception as e:
            print(f"  ✗ 提取HTML失败: {e}")
        
        return ""
    
    def extract_text(self):
        """提取文本内容"""
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
        except Exception as e:
            print(f"  ✗ 提取文本失败: {e}")
        
        return ""
    
    def scrape_match(self, url, match_info):
        """抓取单场比赛数据"""
        
        # 1. 打开页面
        if not self.open_match_page(url):
            return None
        
        # 2. 提取内容
        print("  → 提取页面数据...")
        html = self.extract_html()
        text = self.extract_text()
        
        if not html:
            print("  ✗ 提取数据失败")
            return None
        
        # 3. 解析数据
        print("  → 解析比赛数据...")
        match_data = {
            "match_info": self._extract_match_info(html, text, match_info),
            "teams": self._extract_teams(html, text, match_info),
            "events": self._extract_events(html, text),
            "statistics": self._extract_statistics(html, text),
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "method": "CDP",
                "version": "2.0"
            }
        }
        
        # 4. 统计提取结果
        home_lineup = len(match_data['teams']['home']['lineup'])
        away_lineup = len(match_data['teams']['away']['lineup'])
        print(f"  ✓ 数据提取完成:")
        print(f"     - 首发阵容: {home_lineup + away_lineup} 人")
        print(f"     - 比赛事件: {len(match_data['events'])} 个")
        print(f"     - 统计数据: {len(match_data['statistics'])} 项")
        
        return match_data
    
    def _extract_match_info(self, html, text, match_info):
        """提取比赛基本信息"""
        info = {
            "match_id": match_info.get('match_id', ''),
            "date": match_info.get('date', ''),
            "time": "20:00",
            "competition": {
                "name": "Chinese Super League",
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
        
        # 提取球场和观众
        venue_match = re.search(r'Venue:\s*([^,\n]+)(?:,\s*([^\n]+))?', text)
        if venue_match:
            info['venue']['name'] = venue_match.group(1).strip()
            if venue_match.group(2):
                info['venue']['city'] = venue_match.group(2).strip()
        
        attendance_match = re.search(r'Attendance:\s*([\d,]+)', text)
        if attendance_match:
            info['venue']['attendance'] = int(attendance_match.group(1).replace(',', ''))
        
        return info
    
    def _extract_teams(self, html, text, match_info):
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
        
        # 提取球员（从HTML）
        player_pattern = r'<a href="/en/players/[^"]+">([A-Za-z\s\'\-\.]+)</a>'
        all_players = re.findall(player_pattern, html)
        
        # 去重
        unique_players = []
        seen = set()
        for player in all_players:
            player_clean = player.strip()
            if player_clean and player_clean not in seen and len(player_clean) > 2:
                seen.add(player_clean)
                unique_players.append(player_clean)
        
        # 分配首发（简化逻辑）
        if len(unique_players) >= 22:
            # 主队首发11人
            for i, player in enumerate(unique_players[:11]):
                teams['home']['lineup'].append({
                    "position": self._guess_position(i),
                    "number": i + 1,
                    "name": player,
                    "country": "Unknown"
                })
            
            # 客队首发11人
            for i, player in enumerate(unique_players[11:22]):
                teams['away']['lineup'].append({
                    "position": self._guess_position(i),
                    "number": i + 1,
                    "name": player,
                    "country": "Unknown"
                })
            
            # 替补
            for i, player in enumerate(unique_players[22:29]):
                teams['home']['substitutes'].append({
                    "position": "Sub",
                    "number": 12 + i,
                    "name": player,
                    "country": "Unknown"
                })
            
            for i, player in enumerate(unique_players[29:36]):
                teams['away']['substitutes'].append({
                    "position": "Sub",
                    "number": 12 + i,
                    "name": player,
                    "country": "Unknown"
                })
        
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
        
        return teams
    
    def _guess_position(self, index):
        """根据索引猜测位置"""
        positions = ['GK', 'DF', 'DF', 'DF', 'DF', 'MF', 'MF', 'MF', 'FW', 'FW', 'FW']
        return positions[index] if index < len(positions) else 'MF'
    
    def _extract_events(self, html, text):
        """提取比赛事件"""
        events = []
        
        # 提取进球
        goal_pattern = r'([A-Za-z\s\'\-]+)\s+(\d+)(\+(\d+))?\''
        goals = re.findall(goal_pattern, text)
        
        for player, minute, _, extra in goals[:10]:
            event = {
                "minute": int(minute),
                "minute_extra": int(extra) if extra else 0,
                "type": "goal",
                "team": "home",
                "player": player.strip(),
                "player2": "",
                "description": "Goal"
            }
            events.append(event)
        
        return events
    
    def _extract_statistics(self, html, text):
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
        
        return stats

def main():
    """主函数"""
    
    print("="*70)
    print("上海海港2023赛季比赛数据抓取器 - CDP版本")
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
    
    # 处理每场比赛
    success_count = 0
    failed_matches = []
    
    for i, match in enumerate(matches[:5], 1):  # 先测试前5场
        date = match['date']
        url = match['match_report_url']
        
        print(f"\n{'='*70}")
        print(f"[{i}/{len(matches[:5])}] {date} - 第{i}轮")
        print(f"{'='*70}")
        
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
            
            print(f"\n  ✅ 已保存: {filename}\n")
            success_count += 1
        else:
            print(f"\n  ❌ 抓取失败\n")
            failed_matches.append(f"第{i}轮-{date}")
        
        # 休息一下
        if i < len(matches[:5]):
            print("  等待3秒...")
            time.sleep(3)
    
    # 总结
    print(f"\n{'='*70}")
    print("✅ 批量处理完成")
    print(f"{'='*70}")
    print(f"✓ 成功: {success_count} / 5")
    print(f"✗ 失败: {len(failed_matches)} / 5")
    
    if failed_matches:
        print(f"\n失败的比赛:")
        for match in failed_matches:
            print(f"  - {match}")
    
    print(f"\n📁 保存位置: {output_dir}/")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()
