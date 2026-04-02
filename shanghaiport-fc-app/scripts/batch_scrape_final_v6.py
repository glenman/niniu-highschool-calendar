#!/usr/bin/env python3
"""
上海海港2023赛季完整数据抓取器 - 最终修复版
直接使用 .event 选择器提取events
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

        # 2. 提取events数据（直接使用 .event 选择器）
        extract_js = r"""(() => {
  const result = {
    scores: [],
    formations: [],
    lineups: {home: [], away: []},
    bench: {home: [], away: []},
    events: [],
    statistics: {},
    venue: {}
  };

  // 比分
  document.querySelectorAll('.score').forEach(el => {
    const s = parseInt(el.textContent);
    if (!isNaN(s)) result.scores.push(s);
  });

  // 阵容表
  const tables = document.querySelectorAll('table');
  let tableCount = 0;
  
  tables.forEach(table => {
    const text = table.textContent;
    if (text.includes('Bench') && text.includes('(') && text.includes(')')) {
      const header = table.querySelector('th');
      if (header) {
        result.formations.push(header.textContent.trim());
      }
      
      let isBench = false;
      const starters = [];
      const subs = [];
      
      table.querySelectorAll('tr').forEach(row => {
        if (row.textContent.includes('Bench')) {
          isBench = true;
          return;
        }
        
        const link = row.querySelector('a[href*="/players/"]');
        if (link) {
          const tds = row.querySelectorAll('td');
          const player = {
            number: tds[0]?.textContent?.trim() || '',
            name: link.textContent?.trim() || '',
            country: 'Unknown'
          };
          
          if (isBench) subs.push(player);
          else starters.push(player);
        }
      });
      
      if (tableCount === 0) {
        result.lineups.home = starters;
        result.bench.home = subs;
      } else {
        result.lineups.away = starters;
        result.bench.away = subs;
      }
      tableCount++;
    }
  });

  // ===== 关键：Events提取（直接使用 .event 选择器）=====
  const eventDivs = document.querySelectorAll('.event');
  
  eventDivs.forEach(div => {
    const text = div.textContent || '';
    const className = div.className || '';
    const links = div.querySelectorAll('a[href*="/players/"]');
    
    if (links.length === 0) return;
    
    const players = Array.from(links).map(l => l.textContent.trim());
    
    // 提取时间（使用右单引号'）
    const timeMatch = text.match(/(\d+)(?:\+(\d+))?'/);
    if (!timeMatch) return;
    
    const minute = parseInt(timeMatch[1]);
    const extra = parseInt(timeMatch[2]) || 0;
    
    // 判断事件类型
    let eventType = 'unknown';
    let assist = '';
    let playerOut = '';
    
    if (text.includes('Yellow Card')) {
      eventType = 'yellow_card';
    } else if (text.includes('Red Card')) {
      eventType = 'red_card';
    } else if (text.includes('Goal')) {
      eventType = 'goal';
      // 提取助攻
      if (text.includes('Assist') && players.length >= 2) {
        assist = players[1];
      }
    } else if (text.toLowerCase().includes('for') && players.length >= 2) {
      eventType = 'substitution';
      playerOut = players[1];
    }
    
    if (eventType === 'unknown') return;
    
    // 判断主客队
    const team = className.includes('event a') ? 'home' : 'away';
    
    result.events.push({
      minute: minute,
      minute_extra: extra,
      type: eventType,
      team: team,
      player: players[0] || '',
      player2: assist,
      player_out: playerOut,
      description: eventType.replace('_', ' ').toUpperCase()
    });
  });

  // 统计数据
  const bodyText = document.body.innerText;
  
  const possMatch = bodyText.match(/Possession[\s\S]*?(\d+)%[\s]*(\d+)%/);
  if (possMatch) result.statistics.possession = {home: possMatch[1] + '%', away: possMatch[2] + '%'};
  
  const shotsMatch = bodyText.match(/Shots on Target[\s\S]*?(\d+) of (\d+).*?(\d+) of (\d+)/);
  if (shotsMatch) {
    result.statistics.shots_on_target = {home: shotsMatch[1], away: shotsMatch[3]};
    result.statistics.shots = {home: shotsMatch[2], away: shotsMatch[4]};
  }
  
  const foulsMatch = bodyText.match(/(\d+)\s+Fouls\s+(\d+)/);
  if (foulsMatch) result.statistics.fouls = {home: foulsMatch[1], away: foulsMatch[2]};
  
  const cornersMatch = bodyText.match(/(\d+)\s+Corners\s+(\d+)/);
  if (cornersMatch) result.statistics.corners = {home: cornersMatch[1], away: cornersMatch[2]};

  // 球场信息
  const venueMatch = bodyText.match(/Venue:\s*([^,\n]+)/);
  if (venueMatch) result.venue.name = venueMatch[1].trim();
  
  const attendMatch = bodyText.match(/Attendance:\s*([\d,]+)/);
  if (attendMatch) result.venue.attendance = parseInt(attendMatch[1].replace(',', ''));

  return JSON.stringify(result);
})()"""

        result = subprocess.run(
            ['agent-browser', '--cdp', '9222', 'eval', extract_js],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode != 0:
            return None

        # 3. 解析数据
        output = result.stdout.strip()
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1].replace('\\"', '"')
        
        extracted = json.loads(output)

        # 4. 构建完整数据
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
                "venue": extracted.get('venue', {}),
                "referee": {"name": "", "country": "China"}
            },
            "teams": {
                "home": {
                    "name": extracted['formations'][0].split('(')[0].strip() if len(extracted['formations']) > 0 else "",
                    "full_name": "",
                    "score": extracted['scores'][0] if len(extracted['scores']) > 0 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][0].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 0 and '(' in extracted['formations'][0] else "",
                    "coach": "",
                    "captain": "",
                    "lineup": extracted['lineups']['home'],
                    "substitutes": extracted['bench']['home'],
                    "substitutions": []
                },
                "away": {
                    "name": extracted['formations'][1].split('(')[0].strip() if len(extracted['formations']) > 1 else "",
                    "full_name": "",
                    "score": extracted['scores'][1] if len(extracted['scores']) > 1 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][1].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 1 and '(' in extracted['formations'][1] else "",
                    "coach": "",
                    "captain": "",
                    "lineup": extracted['lineups']['away'],
                    "substitutes": extracted['bench']['away'],
                    "substitutions": []
                }
            },
            "events": extracted['events'],
            "statistics": extracted['statistics'],
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "6.0-final-with-events"
            }
        }

        return match_data
        
    except Exception as e:
        print(f"      ❌ 错误: {e}")
        return None

def main():
    print("="*70)
    print("上海海港2023赛季完整数据抓取器 - 最终修复版")
    print("="*70)
    print()
    
    # 读取比赛URL列表
    with open('data/2023-match_urls.json', 'r', encoding='utf-8') as f:
        url_data = json.load(f)
    
    matches = url_data['match_urls']
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'data/match-reports-2023'
    os.makedirs(output_dir, exist_ok=True)
    
    # 批量处理
    success_count = 0
    total_events = 0
    
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match['match_report_url']
        
        print(f"[{i}/30] {date} - 第{i}轮")
        
        match_data = scrape_match(url, {
            'date': date,
            'round': i
        })
        
        if match_data:
            # 保存文件
            filename = f"{date}-中超-第{i}轮.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            # 显示结果
            home = match_data['teams']['home']
            away = match_data['teams']['away']
            hs = home['score']
            as_ = away['score']
            events_count = len(match_data['events'])
            total_events += events_count
            
            print(f"      ✅ {home['name']} {hs}-{as_} {away['name']}")
            print(f"         事件: {events_count}个")
            
            success_count += 1
        else:
            print(f"      ❌ 失败")
        
        # 休息一下
        if i < len(matches):
            time.sleep(3)
    
    # 总结
    print(f"\n{'='*70}")
    print("✅ 批量处理完成")
    print(f"{'='*70}")
    print(f"✓ 成功: {success_count} / 30")
    print(f"✓ 事件总数: {total_events}个")
    print(f"\n📁 保存位置: {output_dir}/")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
