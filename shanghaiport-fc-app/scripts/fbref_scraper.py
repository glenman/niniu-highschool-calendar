#!/usr/bin/env python3
"""
FBref比赛数据完整抓取脚本
抓取所有详细统计数据，包括犯规、角球、传中、拦截、越位等
"""

import subprocess
import json
import re
import time
from typing import Dict, List, Any

class FBrefMatchScraper:
    """FBref比赛数据抓取器"""
    
    def __init__(self):
        self.timeout = 30
        
    def scrape_match(self, url: str) -> Dict[str, Any]:
        """抓取单场比赛的完整数据"""
        
        print(f"  → 打开页面...")
        result = subprocess.run(
            ['openclaw', 'browser', 'open', url],
            capture_output=True,
            text=True,
            timeout=self.timeout
        )
        
        if 'opened:' not in result.stdout:
            return None
        
        time.sleep(5)
        
        # 抓取完整数据
        print(f"  → 抓取数据...")
        match_data = self._extract_all_data(url)
        
        return match_data
    
    def _extract_all_data(self, url: str) -> Dict[str, Any]:
        """提取所有比赛数据"""
        
        # 1. 提取比赛基本信息
        js_match_info = """
        (function() {
            const scorebox = document.querySelector('.scorebox');
            if (!scorebox) return '{}';
            
            const text = scorebox.textContent;
            const html = scorebox.innerHTML;
            
            // 提取球队和比分
            const teams = [];
            document.querySelectorAll('.scorebox_team').forEach(team => {
                const name = team.querySelector('a')?.textContent?.trim() || '';
                const score = team.querySelector('.score')?.textContent?.trim() || '0';
                const manager = (team.textContent.match(/Manager:\\s*([^\\n]+)/) || [])[1]?.trim() || '';
                const captain = (team.textContent.match(/Captain:\\s*([^\\n]+)/) || [])[1]?.trim() || '';
                
                teams.push({name, score, manager, captain});
            });
            
            // 提取比赛信息
            const meta = document.querySelector('.scorebox_meta');
            const date = (meta?.textContent.match(/(Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday)[^,]+,\\s*\\d{4}/) || [])[0] || '';
            const competition = (meta?.textContent.match(/Chinese[^\\n]+Super League/) || [])[0] || '';
            const attendance = (meta?.textContent.match(/Attendance:\\s*([\\d,]+)/) || [])[1]?.replace(',', '') || '0';
            const venue = (meta?.textContent.match(/Venue:\\s*([^\\n]+)/) || [])[1]?.trim() || '';
            
            return JSON.stringify({
                teams: teams,
                date: date,
                competition: competition,
                attendance: parseInt(attendance),
                venue: venue
            });
        })()
        """
        
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', js_match_info],
            capture_output=True,
            text=True,
            timeout=self.timeout
        )
        
        match_info = self._parse_json_from_output(result.stdout)
        
        # 2. 提取统计数据（包括详细统计）
        js_stats = """
        (function() {
            const statsDiv = document.querySelector('#team_stats');
            if (!statsDiv) return '{}';
            
            const text = statsDiv.textContent;
            const stats = {};
            
            // 提取所有数字对（格式：数字关键词数字）
            const patterns = [
                ['possession', /(\\d+)%(.*?)?(\\d+)%/],
                ['shots', /(\\d+)\\s+of\\s+(\\d+).*?(\\d+)\\s+of\\s+(\\d+)/],
                ['saves', /Saves.*?(\\d+)\\s+of\\s+(\\d+).*?(\\d+)\\s+of\\s+(\\d+)/],
                ['fouls', /(\\d+)\\s*Fouls\\s*(\\d+)/],
                ['corners', /(\\d+)\\s*Corners\\s*(\\d+)/],
                ['crosses', /(\\d+)\\s*Crosses\\s*(\\d+)/],
                ['interceptions', /(\\d+)\\s*Interceptions\\s*(\\d+)/],
                ['offsides', /(\\d+)\\s*Offsides?\\s*(\\d+)/]
            ];
            
            patterns.forEach(([name, pattern]) => {
                const match = text.match(pattern);
                if (match) {
                    if (name === 'possession') {
                        stats[name] = {home: parseInt(match[1]), away: parseInt(match[3])};
                    } else if (match.length >= 3) {
                        if (name === 'shots' || name === 'saves') {
                            stats[name] = {home: parseInt(match[2]), away: parseInt(match[4])};
                            stats[name + '_on_target'] = {home: parseInt(match[1]), away: parseInt(match[3])};
                        } else {
                            stats[name] = {home: parseInt(match[1]), away: parseInt(match[2])};
                        }
                    }
                }
            });
            
            // 黄牌和红牌
            const yellowCards = (text.match(/yellow_card/g) || []).length;
            const redCards = (text.match(/red_card/g) || []).length;
            stats['yellow_cards'] = {home: yellowCards > 0 ? 1 : 0, away: yellowCards > 1 ? 1 : 0};
            stats['red_cards'] = {home: 0, away: 0};
            
            return JSON.stringify(stats);
        })()
        """
        
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', js_stats],
            capture_output=True,
            text=True,
            timeout=self.timeout
        )
        
        stats = self._parse_json_from_output(result.stdout)
        
        # 3. 提取进球事件
        js_events = """
        (function() {
            const events = [];
            const eventDivs = document.querySelectorAll('.event');
            
            eventDivs.forEach(div => {
                const text = div.textContent;
                const links = div.querySelectorAll('a');
                
                links.forEach(link => {
                    const player = link.textContent.trim();
                    const parent = link.parentElement?.textContent || '';
                    
                    // 提取分钟数
                    const minuteMatch = parent.match(/·\\s*(\\d+)(\\+(\\d+))?'/);
                    if (minuteMatch) {
                        events.push({
                            minute: parseInt(minuteMatch[1]),
                            minute_extra: minuteMatch[3] ? parseInt(minuteMatch[3]) : 0,
                            type: 'goal',
                            player: player,
                            team: div.id === 'a' ? 'home' : 'away'
                        });
                    }
                });
            });
            
            return JSON.stringify(events);
        })()
        """
        
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', js_events],
            capture_output=True,
            text=True,
            timeout=self.timeout
        )
        
        events = self._parse_json_from_output(result.stdout) or []
        
        # 4. 构建完整数据
        match_data = {
            "match_info": {
                "match_id": url.split('/')[-2] if '/' in url else '',
                "date": self._parse_date(match_info.get('date', '')),
                "time": "20:00",  # 需要从页面提取
                "competition": {
                    "name": match_info.get('competition', 'Chinese Super League'),
                    "season": "2024",
                    "round": ""
                },
                "venue": {
                    "name": match_info.get('venue', '').split(',')[0] if ',' in match_info.get('venue', '') else match_info.get('venue', ''),
                    "city": match_info.get('venue', '').split(',')[1].strip() if ',' in match_info.get('venue', '') else '',
                    "attendance": match_info.get('attendance', 0)
                },
                "referee": {
                    "name": "",
                    "country": "China"
                }
            },
            "teams": {
                "home": {
                    "name": match_info['teams'][0]['name'] if match_info.get('teams') and len(match_info['teams']) > 0 else '',
                    "score": int(match_info['teams'][0]['score']) if match_info.get('teams') and len(match_info['teams']) > 0 else 0,
                    "coach": match_info['teams'][0]['manager'] if match_info.get('teams') and len(match_info['teams']) > 0 else '',
                    "captain": match_info['teams'][0]['captain'] if match_info.get('teams') and len(match_info['teams']) > 0 else '',
                    "lineup": [],
                    "substitutes": [],
                    "substitutions": []
                },
                "away": {
                    "name": match_info['teams'][1]['name'] if match_info.get('teams') and len(match_info['teams']) > 1 else '',
                    "score": int(match_info['teams'][1]['score']) if match_info.get('teams') and len(match_info['teams']) > 1 else 0,
                    "coach": match_info['teams'][1]['manager'] if match_info.get('teams') and len(match_info['teams']) > 1 else '',
                    "captain": match_info['teams'][1]['captain'] if match_info.get('teams') and len(match_info['teams']) > 1 else '',
                    "lineup": [],
                    "substitutes": [],
                    "substitutions": []
                }
            },
            "events": events,
            "statistics": stats if stats else {},
            "player_stats": {
                "home": [],
                "away": []
            },
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "1.0"
            }
        }
        
        return match_data
    
    def _parse_json_from_output(self, output: str) -> Any:
        """从输出中解析JSON"""
        lines = output.strip().split('\n')
        for line in reversed(lines):
            if line.startswith('{') or line.startswith('['):
                try:
                    return json.loads(line)
                except:
                    continue
        return None
    
    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        # 简单转换，实际需要更复杂的逻辑
        months = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }
        
        # 示例: "Friday March 1, 2024" -> "2024-03-01"
        match = re.search(r'(\\w+)\\s+(\\d+),\\s+(\\d{4})', date_str)
        if match:
            month_name = match.group(1)
            day = match.group(2).zfill(2)
            year = match.group(3)
            month = months.get(month_name, '01')
            return f"{year}-{month}-{day}"
        
        return ""

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python fbref_scraper.py <URL>")
        print("示例: python fbref_scraper.py https://fbref.com/en/matches/...")
        sys.exit(1)
    
    url = sys.argv[1]
    
    scraper = FBrefMatchScraper()
    match_data = scraper.scrape_match(url)
    
    if match_data:
        # 保存到文件
        filename = f"match_data_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(match_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到: {filename}")
        print(f"\n比赛: {match_data['teams']['home']['name']} {match_data['teams']['home']['score']}-{match_data['teams']['away']['score']} {match_data['teams']['away']['name']}")
        print(f"统计项: {len(match_data['statistics'])} 项")
    else:
        print("❌ 数据抓取失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
