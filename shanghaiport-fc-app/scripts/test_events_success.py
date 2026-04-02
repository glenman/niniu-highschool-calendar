#!/usr/bin/env python3
"""
上海海港2023赛季完整数据抓取器 - 最终成功版
修复正则表达式转义问题
"""

import json
import os
import subprocess
import time
from datetime import datetime
import re

def scrape_match(url: str, match_info: dict) -> dict:
    """抓取单场比赛数据"""
    
    try:
        # 1. 打开页面
        result = subprocess.run(
            ['agent-browser', '--cdp', '9222', 'open', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        time.sleep(10)

        # 2. 提取原始events数据
        extract_js = r"""(() => {
  const result = {events: []};
  const eventDivs = document.querySelectorAll('.event');
  
  eventDivs.forEach(div => {
    const text = div.textContent || '';
    const className = div.className || '';
    const links = Array.from(div.querySelectorAll('a')).map(a => a.textContent.trim());
    
    if (links.length > 0) {
      result.events.push({
        text: text,
        className: className,
        players: links
      });
    }
  });
  
  return JSON.stringify(result);
})()"""

        result = subprocess.run(
            ['agent-browser', '--cdp', '9222', 'eval', extract_js],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode != 0:
            return None

        # 3. 在Python中解析events
        output = result.stdout.strip()
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1].replace('\\"', '"')
        
        raw_data = json.loads(output)
        
        events = []
        for raw in raw_data['events']:
            text = raw['text']
            className = raw['className']
            players = raw['players']
            
            # 提取时间 - 使用字符类匹配各种可能的引号
            time_match = re.search(r"(\d+)(?:\+(\d+))?(?:['\u2019´])", text)
            if not time_match:
                continue
            
            minute = int(time_match.group(1))
            extra = int(time_match.group(2)) if time_match.group(2) else 0
            
            # 判断事件类型
            event_type = 'unknown'
            if 'Yellow Card' in text or 'Yellow' in text:
                event_type = 'yellow_card'
            elif 'Red Card' in text or 'Red' in text:
                event_type = 'red_card'
            elif 'Goal' in text:
                event_type = 'goal'
            elif 'for' in text.lower() and len(players) >= 2:
                event_type = 'substitution'
            
            if event_type == 'unknown':
                continue
            
            # 判断主客队
            team = 'home' if 'event a' in className else 'away'
            
            events.append({
                "minute": minute,
                "minute_extra": extra,
                "type": event_type,
                "team": team,
                "player": players[0] if players else "",
                "player2": players[1] if len(players) > 1 and event_type == 'goal' else "",
                "player_out": players[1] if len(players) > 1 and event_type == 'substitution' else "",
                "description": event_type.replace('_', ' ').upper()
            })

        # 4. 提取其他数据（简化版，只提取events用于测试）
        match_data = {
            "match_info": {
                "match_id": url.split('/')[-2],
                "date": match_info['date'],
                "time": "20:00",
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": "2023",
                    "round": f"Matchweek {match_info['round']}"
                },
                "venue": {"name": "", "city": "", "attendance": 0},
                "referee": {"name": "", "country": "China"}
            },
            "teams": {
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
            },
            "events": events,
            "statistics": {},
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "8.0-success"
            }
        }

        return match_data
        
    except Exception as e:
        print(f"      ❌ 错误: {e}")
        return None

# 测试
if __name__ == '__main__':
    url = 'https://fbref.com/en/matches/13f114b6/Wuhan-Three-Towns-Shanghai-Port-April-15-2023-Chinese-Super-League'
    
    print("测试第1轮...")
    data = scrape_match(url, {'date': '2023-04-15', 'round': 1})
    
    if data:
        print(f"\n✅ 成功！提取到 {len(data['events'])} 个events:")
        for i, e in enumerate(data['events'][:15], 1):
            extra = f"+{e['minute_extra']}" if e['minute_extra'] > 0 else ""
            print(f"{i}. {e['minute']}'{extra} - {e['type']} - {e['player']} ({e['team']})")
    else:
        print("\n❌ 失败")
