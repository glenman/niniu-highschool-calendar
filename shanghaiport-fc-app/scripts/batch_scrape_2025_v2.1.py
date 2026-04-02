#!/usr/bin/env python3
"""
上海海港2025赛季完整数据批量抓取器 v2.1
从FBref页面提取实际matchweek值，而非使用循环变量
"""

import json
import os
import subprocess
import time
from datetime import datetime
import re

def scrape_match(url: str, match_info: dict) -> tuple:
    """抓取单场比赛数据，返回(data, actual_matchweek)"""
    
    try:
        # 1. 打开页面
        result = subprocess.run(
            ['agent-browser', '--cdp', '9222', 'open', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None, None
        time.sleep(10)

        # 2. 提取完整数据（包含matchweek）
        extract_js = r"""(() => {
  const result = {
    scores: [],
    formations: [],
    lineups: {home: [], away: []},
    bench: {home: [], away: []},
    events: [],
    statistics: {},
    venue: {},
    matchweek: null
  };

  // 提取matchweek（关键！）
  const bodyText = document.body.innerText;
  const matchweekMatch = bodyText.match(/Matchweek\s+(\d+)/i);
  if (matchweekMatch) {
    result.matchweek = matchweekMatch[1];
  }

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

  // Events提取
  const eventDivs = document.querySelectorAll('.event');
  
  const yellowCards = {home: 0, away: 0};
  const redCards = {home: 0, away: 0};
  
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
      
      if (text.includes('Yellow Card')) {
        if (className.includes('event a')) yellowCards.away++;
        else yellowCards.home++;
      }
      
      if (text.includes('Red Card')) {
        if (className.includes('event a')) redCards.away++;
        else redCards.home++;
      }
    }
  });

  // 统计数据
  const possMatch = bodyText.match(/Possession[\s\S]*?(\d+)%[\s]*(\d+)%/);
  if (possMatch) result.statistics.possession = {home: possMatch[1] + '%', away: possMatch[2] + '%'};
  
  const shotsMatch = bodyText.match(/Shots on Target[\s\S]*?(\d+)\s+of\s+(\d+)\s*[—–-]\s*(\d+)%[\s\S]*?(\d+)%\s*[—–-]\s*(\d+)\s+of\s+(\d+)/);
  if (shotsMatch) {
    result.statistics.shots_on_target = {home: shotsMatch[1], away: shotsMatch[5]};
    result.statistics.shots = {home: shotsMatch[2], away: shotsMatch[6]};
    result.statistics.shots_accuracy = {home: shotsMatch[3] + '%', away: shotsMatch[4] + '%'};
  }
  
  const savesMatch = bodyText.match(/Saves[\s\S]*?(\d+)\s+of\s+(\d+)\s*[—–-]\s*(\d+)%[\s\S]*?(\d+)%\s*[—–-]\s*(\d+)\s+of\s+(\d+)/);
  if (savesMatch) {
    result.statistics.saves = {
      home: savesMatch[1] + ' of ' + savesMatch[2] + '-' + savesMatch[3] + '%',
      away: savesMatch[5] + ' of ' + savesMatch[6] + '-' + savesMatch[4] + '%'
    };
  }
  
  const foulsMatch = bodyText.match(/(\d+)\s+Fouls\s+(\d+)/);
  if (foulsMatch) result.statistics.fouls = {home: foulsMatch[1], away: foulsMatch[2]};
  
  const cornersMatch = bodyText.match(/(\d+)\s+Corners\s+(\d+)/);
  if (cornersMatch) result.statistics.corners = {home: cornersMatch[1], away: cornersMatch[2]};

  const crossesMatch = bodyText.match(/(\d+)\s+Crosses\s+(\d+)/);
  if (crossesMatch) result.statistics.crosses = {home: crossesMatch[1], away: crossesMatch[2]};
  
  const intMatch = bodyText.match(/(\d+)\s+Interceptions\s+(\d+)/);
  if (intMatch) result.statistics.interceptions = {home: intMatch[1], away: intMatch[2]};
  
  const offMatch = bodyText.match(/(\d+)\s+Offsides?\s+(\d+)/);
  if (offMatch) result.statistics.offsides = {home: offMatch[1], away: offMatch[2]};
  
  result.statistics.yellow_cards = yellowCards;
  result.statistics.red_cards = redCards;

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
            return None, None

        output = result.stdout.strip()
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1].replace('\"', '"')
        
        extracted = json.loads(output)
        
        # 获取实际的matchweek（关键！）
        actual_matchweek = extracted.get('matchweek', str(match_info.get('round', 1)))
        
        # 在Python中解析events
        events = []
        for raw in extracted['events']:
            text = raw['text']
            className = raw['className']
            players = raw['players']
            
            time_match = re.search(r"(\d+)(?:\+(\d+))?(?:['\u2019´])", text)
            if not time_match:
                continue
            
            minute = int(time_match.group(1))
            extra = int(time_match.group(2)) if time_match.group(2) else 0
            
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

        date = match_info['date']
        match_data = {
            "match_info": {
                "match_id": url.split('/')[-2],
                "date": date,
                "time": "20:00",
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": "2025",
                    "round": f"Matchweek {actual_matchweek}"
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
            "events": events,
            "statistics": extracted['statistics'],
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "9.1-correct-matchweek"
            }
        }

        return match_data, actual_matchweek
        
    except Exception as e:
        print(f"      ❌ 错误: {e}")
        return None, None

def main():
    print("="*70)
    print("上海海港2025赛季完整数据批量抓取器 v2.1")
    print("从FBref页面提取实际matchweek值")
    print("="*70)
    print()
    
    # 读取比赛URL列表
    with open('data/2025-match_urls.json', 'r', encoding='utf-8') as f:
        url_data = json.load(f)
    
    matches = url_data['match_urls']
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'data/match-reports-2025'
    os.makedirs(output_dir, exist_ok=True)
    
    # 清空旧文件
    old_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    if old_files:
        print(f"🗑️  清空旧文件: {len(old_files)}个\n")
        for f in old_files:
            os.remove(os.path.join(output_dir, f))
    
    # 批量处理
    success_count = 0
    total_events = 0
    failed_matches = []
    matchweek_log = []
    
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match['match_report_url']
        
        print(f"[{i}/30] {date}")
        
        match_data, actual_round = scrape_match(url, {
            'date': date,
            'round': i
        })
        
        if match_data:
            # 使用实际的matchweek保存文件
            filename = f"{date}-中超-第{actual_round}轮.json"
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
            print(f"         第{actual_round}轮 | 事件: {events_count}个")
            
            matchweek_log.append({
                'date': date,
                'round': actual_round,
                'teams': f"{home['name']} vs {away['name']}"
            })
            
            success_count += 1
        else:
            print(f"      ❌ 失败")
            failed_matches.append(f"{date}")
        
        # 休息一下
        if i < len(matches):
            time.sleep(3)
    
    # 总结
    print(f"\n{'='*70}")
    print("✅ 批量处理完成")
    print(f"{'='*70}")
    print(f"✓ 成功: {success_count} / 30")
    print(f"✓ 事件总数: {total_events}个")
    
    if failed_matches:
        print(f"\n失败的比赛:")
        for match in failed_matches:
            print(f"  - {match}")
    
    # 保存matchweek日志
    log_file = 'data/2025-matchweek_log.json'
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(matchweek_log, f, ensure_ascii=False, indent=2)
    print(f"\n📄 Matchweek日志: {log_file}")
    
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
