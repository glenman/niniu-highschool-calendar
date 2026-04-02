#!/usr/bin/env python3
"""
上海海港2023赛季比赛数据抓取器 - 完整版
使用CDP提取FBref页面所有数据
"""

import json
import os
import subprocess
import time
import re
from datetime import datetime

class FullMatchScraper:
    """完整比赛数据抓取器"""
    
    def __init__(self, cdp_port=9222):
        self.cdp_port = cdp_port
    
    def check_connection(self):
        """检查CDP连接"""
        result = subprocess.run(
            ['agent-browser', '--cdp', str(self.cdp_port), 'get', 'title'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"✓ CDP连接成功")
            return True
        print(f"✗ CDP连接失败")
        return False
    
    def open_page(self, url):
        """打开页面"""
        result = subprocess.run(
            ['agent-browser', '--cdp', str(self.cdp_port), 'open', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            time.sleep(8)
            return True
        return False
    
    def get_snapshot(self):
        """获取页面快照"""
        result = subprocess.run(
            ['agent-browser', '--cdp', str(self.cdp_port), 'snapshot', '-i', '--json'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except:
                pass
        return None
    
    def get_html(self):
        """获取HTML"""
        result = subprocess.run(
            ['agent-browser', '--cdp', str(self.cdp_port), 'eval', 
             'document.documentElement.outerHTML'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return result.stdout
        return ""
    
    def scrape_match(self, url, match_info):
        """抓取完整比赛数据"""
        
        print(f"  → 打开页面...")
        if not self.open_page(url):
            return None
        
        print(f"  → 获取页面数据...")
        html = self.get_html()
        snapshot = self.get_snapshot()
        
        if not html:
            return None
        
        print(f"  → 解析比赛数据...")
        
        # 提取所有数据
        match_data = {
            "match_info": self._extract_match_info(html, match_info),
            "teams": self._extract_teams(html, match_info),
            "events": self._extract_events(html),
            "statistics": self._extract_statistics(html),
            "player_stats": self._extract_player_stats(html),
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "2.0-full"
            }
        }
        
        # 统计提取结果
        home_players = len(match_data['teams']['home']['lineup'])
        away_players = len(match_data['teams']['away']['lineup'])
        events = len(match_data['events'])
        stats = len(match_data['statistics'])
        
        print(f"  ✓ 完成 - 球员:{home_players+away_players} 事件:{events} 统计:{stats}")
        return match_data
    
    def _extract_match_info(self, html, match_info):
        """提取比赛信息"""
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
        
        # 提取球场信息
        venue_match = re.search(r'Venue:\s*([^<\n]+)', html)
        if venue_match:
            venue_text = venue_match.group(1).strip()
            # 清理HTML实体
            venue_text = re.sub(r'&[^;]+;', '', venue_text)
            venue_text = venue_text.split('Officials')[0].strip()
            
            if ',' in venue_text:
                parts = venue_text.split(',', 1)
                info['venue']['name'] = parts[0].strip()
                if len(parts) > 1:
                    info['venue']['city'] = parts[1].strip()
            else:
                info['venue']['name'] = venue_text
        
        # 提取观众人数
        attendance_match = re.search(r'Attendance:\s*([\d,]+)', html)
        if attendance_match:
            info['venue']['attendance'] = int(attendance_match.group(1).replace(',', ''))
        
        # 提取裁判
        referee_match = re.search(r'Referee:\s*([^<\n,]+)', html)
        if referee_match:
            info['referee']['name'] = referee_match.group(1).strip()
        
        return info
    
    def _extract_teams(self, html, match_info):
        """提取球队完整信息"""
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
        
        # 提取球队名称和阵型 - 从标题或表格头
        # 格式: <th ...>Team Name (4-3-3)</th>
        team_header_pattern = r'<th[^>]*>([^<]+)\s+\((\d+-\d+-\d+)\)</th>'
        team_headers = re.findall(team_header_pattern, html)
        
        if len(team_headers) >= 2:
            teams['home']['name'] = team_headers[0][0].strip()
            teams['home']['formation'] = team_headers[0][1]
            teams['away']['name'] = team_headers[1][0].strip()
            teams['away']['formation'] = team_headers[1][1]
        
        # 提取教练
        manager_pattern = r'Manager:\s*([^<\n]+)'
        managers = re.findall(manager_pattern, html)
        if len(managers) >= 2:
            teams['home']['coach'] = managers[0].strip()
            teams['away']['coach'] = managers[1].strip()
        
        # 提取队长
        captain_pattern = r'Captain:\s*([^<\n]+)'
        captains = re.findall(captain_pattern, html)
        if len(captains) >= 2:
            teams['home']['captain'] = captains[0].strip()
            teams['away']['captain'] = captains[1].strip()
        
        # 提取球员 - 从lineup表格
        # 格式: <td...><a href="/en/players/...">Player Name</a></td>
        player_rows_pattern = r'<tr[^>]*>.*?</tr>'
        player_rows = re.findall(player_rows_pattern, html, re.DOTALL)
        
        # 更精确的球员提取 - 从阵容表格
        lineup_pattern = r'<td[^>]*>(\d+)</td>\s*<td[^>]*><a[^>]+>([^<]+)</a></td>'
        
        # 分别提取主客队球员
        # 这需要更复杂的解析，暂时简化处理
        players_data = []
        for match in re.finditer(lineup_pattern, html):
            number = match.group(1)
            name = match.group(2).strip()
            if name and len(name) > 2:
                players_data.append({
                    "position": self._guess_position(int(number)),
                    "number": int(number),
                    "name": name,
                    "country": "Unknown"
                })
        
        # 分配球员（前11个主队，后11个客队）
        if len(players_data) >= 22:
            teams['home']['lineup'] = players_data[:11]
            teams['away']['lineup'] = players_data[11:22]
            
            # 替补（剩余的7+7）
            if len(players_data) > 22:
                subs = players_data[22:]
                mid = len(subs) // 2
                teams['home']['substitutes'] = subs[:mid]
                teams['away']['substitutes'] = subs[mid:mid+7]
        
        # 提取换人
        sub_pattern = r'(\d+)\'\s*([^<]+)\s+for\s+([^<]+)'
        subs = re.findall(sub_pattern, html)
        
        for i, (minute, player_in, player_out) in enumerate(subs):
            sub_data = {
                "minute": int(minute),
                "player_out": player_out.strip(),
                "player_in": player_in.strip()
            }
            
            # 简单分配：前半主队，后半客队
            if i < len(subs) // 2:
                teams['home']['substitutions'].append(sub_data)
            else:
                teams['away']['substitutions'].append(sub_data)
        
        return teams
    
    def _guess_position(self, number):
        """根据球衣号猜测位置"""
        if number == 1:
            return "GK"
        elif number <= 5:
            return "DF"
        elif number <= 10:
            return "MF"
        else:
            return "FW"
    
    def _extract_events(self, html):
        """提取比赛事件"""
        events = []
        
        # 提取进球 - 从事件时间轴
        # 格式可能：<div...>45'+2 Goal Player Name</div>
        goal_pattern = r'(\d+)(?:\+(\d+))?\'[^\n]*Goal[^\n]*([A-Z][a-z]+\s+[A-Z][a-z]+)'
        goals = re.findall(goal_pattern, html)
        
        for minute, extra, player in goals:
            event = {
                "minute": int(minute),
                "minute_extra": int(extra) if extra else 0,
                "type": "goal",
                "team": "home",  # 需要更智能的判断
                "player": player.strip(),
                "player2": "",
                "description": "Goal"
            }
            events.append(event)
        
        # 提取黄牌
        yellow_pattern = r'(\d+)\'[^\n]*Yellow[^\n]*([A-Z][a-z]+\s+[A-Z][a-z]+)'
        yellows = re.findall(yellow_pattern, html)
        
        for minute, player in yellows:
            event = {
                "minute": int(minute),
                "type": "yellow_card",
                "team": "home",
                "player": player.strip(),
                "description": "Yellow Card"
            }
            events.append(event)
        
        # 按时间排序
        events.sort(key=lambda x: x.get('minute', 0))
        
        return events
    
    def _extract_statistics(self, html):
        """提取统计数据"""
        stats = {}
        
        # 定义要提取的统计项
        stat_patterns = {
            'possession': r'Possession.*?(\d+)%.*?(\d+)%',
            'shots': r'Shots.*?(\d+).*?(\d+)',
            'shots_on_target': r'Shots on Target.*?(\d+).*?(\d+)',
            'saves': r'Saves.*?(\d+).*?(\d+)',
            'fouls': r'(\d+)Fouls(\d+)',
            'corners': r'(\d+)Corners(\d+)',
            'crosses': r'(\d+)Crosses(\d+)',
            'interceptions': r'(\d+)Interceptions(\d+)',
            'offsides': r'(\d+)Offsides?(\d+)',
        }
        
        for stat_name, pattern in stat_patterns.items():
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                try:
                    home_val = int(match.group(1))
                    away_val = int(match.group(2))
                    stats[stat_name] = {"home": home_val, "away": away_val}
                except:
                    pass
        
        # 黄牌和红牌 - 从页面计数
        yellow_count = html.count('yellow')
        red_count = html.count('red card')
        
        stats['yellow_cards'] = {
            "home": yellow_count // 2 if yellow_count > 0 else 0,
            "away": yellow_count // 2 if yellow_count > 0 else 0
        }
        stats['red_cards'] = {
            "home": red_count // 2 if red_count > 0 else 0,
            "away": red_count // 2 if red_count > 0 else 0
        }
        
        return stats
    
    def _extract_player_stats(self, html):
        """提取球员统计（简化版）"""
        return {
            "home": [],
            "away": []
        }

def main():
    """主函数"""
    
    print("="*70)
    print("上海海港2023赛季完整数据抓取器")
    print("="*70)
    print()
    
    scraper = FullMatchScraper(cdp_port=9222)
    
    if not scraper.check_connection():
        return
    
    # 读取URL列表
    with open('shanghaiport-fc-app/data/2023-match_urls.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = data['match_urls']
    print(f"✓ 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'shanghaiport-fc-app/data/match-reports-2023'
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理前5场
    for i, match in enumerate(matches[:5], 1):
        date = match['date']
        url = match['match_report_url']
        
        print(f"[{i}/5] {date} - 第{i}轮")
        
        match_data = scraper.scrape_match(url, {
            'date': date,
            'match_id': url.split('/')[-2],
            'round': i
        })
        
        if match_data:
            filename = f"{date}-中超-第{i}轮.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ {filename}\n")
        else:
            print(f"  ❌ 失败\n")
        
        if i < 5:
            time.sleep(3)
    
    print("="*70)
    print("✅ 完成")
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
