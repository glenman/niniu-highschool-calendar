#!/usr/bin/env python3
"""
上海海港赛事报告完整抓取器 v9.4 - 修复版
修复：同时从 .event 和页面文本提取进球信息，确保点球进球被正确识别为 penalty_goal
"""

import json
import os
import subprocess
import time
import re

EXTRACT_JS = r"""(() => {
  const result = {
    scores: [],
    formations: [],
    lineups: {home: [], away: []},
    bench: {home: [], away: []},
    events: [],
    statistics: {},
    venue: {},
    matchweek: null,
    matchTime: '20:00',
    homeManager: '',
    awayManager: '',
    homeCaptain: '',
    awayCaptain: '',
    referees: {
      main: '',
      ar1: '',
      ar2: '',
      fourth: '',
      var: ''
    },
    bodyText: document.body.innerText,
  };
  
  const lines = result.bodyText.split('\n');
  
  // 1. Matchweek
  const mwMatch = result.bodyText.match(/Matchweek\s+(\d+)/i);
  if (mwMatch) result.matchweek = mwMatch[1];
  
  // 2. 比赛时间
  const timeMatch = result.bodyText.match(/(\d{1,2}:\d{2})\s*\(venue time\)/);
  if (timeMatch) result.matchTime = timeMatch[1];
  
  // 3. 教练和队长
  const managers = [];
  const captains = [];
  
  lines.forEach(line => {
    const trimmed = line.trim();
    if (trimmed.startsWith('Manager:')) {
      const match = trimmed.match(/Manager:\s*(.+)/);
      if (match && managers.length < 2) managers.push(match[1].trim());
    }
    if (trimmed.startsWith('Captain:')) {
      const match = trimmed.match(/Captain:\s*(.+)/);
      if (match && captains.length < 2) captains.push(match[1].trim());
    }
  });
  
  result.homeManager = managers[0] || '';
  result.awayManager = managers[1] || '';
  result.homeCaptain = captains[0] || '';
  result.awayCaptain = captains[1] || '';
  
  // 4. 裁判组
  const officialsMatch = result.bodyText.match(/Officials:\s*([^\n]+)/);
  if (officialsMatch) {
    const text = officialsMatch[1];
    const mainMatch = text.match(/([A-Za-z\s]+?)\s*\(Referee\)/);
    if (mainMatch) result.referees.main = mainMatch[1].trim();
    
    const ar1Match = text.match(/·\s*([A-Za-z\s]+?)\s*\(AR1\)/);
    if (ar1Match) result.referees.ar1 = ar1Match[1].trim();
    
    const ar2Match = text.match(/·\s*([A-Za-z\s]+?)\s*\(AR2\)/);
    if (ar2Match) result.referees.ar2 = ar2Match[1].trim();
    
    const fourthMatch = text.match(/·\s*([A-Za-z\s]+?)\s*\(4th\)/);
    if (fourthMatch) result.referees.fourth = fourthMatch[1].trim();
    
    const varMatch = text.match(/·\s*([A-Za-z\s]+?)\s*\(VAR\)/);
    if (varMatch) result.referees.var = varMatch[1].trim();
  }
  
  // 5. 比分
  document.querySelectorAll('.score').forEach(el => {
    const s = parseInt(el.textContent);
    if (!isNaN(s)) result.scores.push(s);
  });
  
  // 6. 阵容
  const tables = document.querySelectorAll('table');
  let tableCount = 0;
  
  tables.forEach(table => {
    const text = table.textContent;
    if (text.includes('Bench') && text.includes('(') && text.includes(')')) {
      const header = table.querySelector('th');
      if (header) result.formations.push(header.textContent.trim());
      
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
  
  // 7. Events - 从 .event 元素提取
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
  
  // 8. ⣀查罚成功率 - FBref格式
  const possMatch = result.bodyText.match(/Possession[\s\S]*?(\d+)%[\s]*(\d+)%/);
  if (possMatch) result.statistics.possession = {home: possMatch[1] + '%', away: possMatch[2] + '%'};
  
  const shotsMatch = result.bodyText.match(/Shots on Target[\s\S]*?(\d+)\s+of\s+(\d+)\s*[—–-]\s*(\d+)%[\s\S]*?(\d+)%\s*[—–-]\s*(\d+)\s+of\s+(\d+)/);
  if (shotsMatch) {
    result.statistics.shots_on_target = {home: shotsMatch[1], away: shotsMatch[5]};
    result.statistics.shots = {home: shotsMatch[2], away: shotsMatch[6]};
    result.statistics.shots_accuracy = {home: shotsMatch[3] + '%', away: shotsMatch[4] + '%'};
  }
  
  const savesMatch = result.bodyText.match(/Saves[\s\S]*?(\d+)\s+of\s+(\d+)\s*[—–-]\s*(\d+)%[\s\S]*?(\d+)%\s*[—–-]\s*(\d+)\s+of\s+(\d+)/);
  if (savesMatch) {
    result.statistics.saves = {
      home: savesMatch[1] + ' of ' + savesMatch[2] + '-' + savesMatch[3] + '%',
      away: savesMatch[5] + ' of ' + savesMatch[6] + '-' + savesMatch[4] + '%'
    };
  }
  
  const foulsMatch = result.bodyText.match(/(\d+)\s+Fouls\s+(\d+)/);
  if (foulsMatch) result.statistics.fouls = {home: foulsMatch[1], away: foulsMatch[2]};
  
  const cornersMatch = result.bodyText.match(/(\d+)\s+Corners\s+(\d+)/);
  if (cornersMatch) result.statistics.corners = {home: cornersMatch[1], away: cornersMatch[2]};

  const crossesMatch = result.bodyText.match(/(\d+)\s+Crosses\s+(\d+)/);
  if (crossesMatch) result.statistics.crosses = {home: crossesMatch[1], away: crossesMatch[2]};
  
  const intMatch = result.bodyText.match(/(\d+)\s+Interceptions\s+(\d+)/);
  if (intMatch) result.statistics.interceptions = {home: intMatch[1], away: intMatch[2]};
  
  const offMatch = result.bodyText.match(/(\d+)\s+Offsides?\s+(\d+)/);
  if (offMatch) result.statistics.offsides = {home: offMatch[1], away: offMatch[2]};
  
  // 9. 球场
  const venueMatch = result.bodyText.match(/Venue:\s*([^,\n]+)/);
  if (venueMatch) result.venue.name = venueMatch[1].trim();
  
  const attendMatch = result.bodyText.match(/Attendance:\s*([\d,]+)/);
  if (attendMatch) result.venue.attendance = parseInt(attendMatch[1].replace(',', ''));
  
  // 10. 红黄牌统计 - 从events中统计
  const yellowCards = {home: 0, away: 0};
  const redCards = {home: 0, away: 0};
  
  result.events.forEach(ev => {
    if (ev.text.includes('Yellow')) {
      if (ev.className.includes('event a')) yellowCards.away++;
      else yellowCards.home++;
    }
    
    if (ev.text.includes('Red') && ev.text.includes('Card')) {
      if (ev.className.includes('event a')) redCards.away++;
      else redCards.home++;
    }
  });
  
  result.statistics.yellow_cards = yellowCards;
  result.statistics.red_cards = redCards;
  
  // 11. 页面文本中的进球信息（补充 .event 中缺失的）
  const pageGoals = [];
  const goalPattern = /([A-Za-z\s]+?)\s*(?:\([P]\))?\s*[·•]\s*(\d+)(?:\+(\d+))?['\u2019´]/g;
  let match;
  while ((match = goalPattern.exec(result.bodyText)) !== null) {
    pageGoals.push({
      player: match[1].trim(),
      isPenalty: match[2] === '(P)',
      minute: parseInt(match[3]),
      extra: match[4] ? parseInt(match[4]) : 0
    });
  }
  
  result.pageGoals = pageGoals;
  
  return JSON.stringify(result);
})()"""

def scrape_match(url, match_info):
    try:
        result = subprocess.run(['agent-browser', '--cdp', '9222', 'open', url],
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None, None
        time.sleep(10)

        result = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', EXTRACT_JS],
                              capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return None, None

        output = result.stdout.strip()
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1].replace('\\"', '"')
        
        extracted = json.loads(output)
        
        actual_matchweek = extracted.get('matchweek', str(match_info.get('round', 1)))
        
        # 从 .event 元素解析 events
        events = []
        for raw in extracted.get('events', []):
            text = raw['text']
            className = raw['className']
            players = raw['players']
            
            time_match = re.search(r"(\d+)(?:\+(\d+))?(?:['\u2019´])", text)
            if not time_match:
                continue
            
            minute = int(time_match.group(1))
            extra = int(time_match.group(2)) if time_match.group(2) else 0
            
            event_type = 'unknown'
            goal_type = ''
            
            # 改进的点球识别逻辑
            if 'Yellow' in text:
                event_type = 'yellow_card'
            elif 'Red' in text and 'Card' in text:
                event_type = 'red_card'
            elif 'Goal' in text or '(P)' in text:  # 识别点球
                event_type = 'goal'
                if '(P)' in text:
                    goal_type = 'penalty_goal'
                else:
                    goal_type = 'goal'
            elif 'for' in text.lower() and len(players) >= 2:
                event_type = 'substitution'
            
            if event_type == 'unknown':
                continue
            
            team = 'home' if 'event a' in className else 'away'
            
            assist = ''
            if event_type == 'goal' and len(players) > 1:
                assist = players[1]
            
            events.append({
                "minute": minute,
                "minute_extra": extra,
                "type": event_type,
                "team": team,
                "player": players[0] if players else "",
                "player2": assist,
                "goal_type": goal_type,
                "player_out": players[1] if len(players) > 1 and event_type == 'substitution' else "",
                "description": event_type.replace('_', ' ').upper()
            })
        
        # 合并页面文本中的进球（去重）
        page_goals = extracted.get('pageGoals', [])
        existing_minutes = {(e['minute'], e.get('minute_extra', 0)) for e in events}
        
        for pg in page_goals:
            key = (pg['minute'], pg['extra'])
            if key not in existing_minutes:
                # 判断主客队（根据球员名）
                shanghai_players = ['Oscar', 'Paulinho', 'Gustavo', 'Wu Lei', 'Li Shenglong',
                                    'Lu Wenjun', 'Wang Shenchao', 'Zhang Linpeng', 
                                    'Matías Vargas', 'Markus Pink', 'Xu Xin', 
                                    'Tyias Browning', 'Elkeson', 'Yan Junling']
                is_home = any(p in pg['player'] for p in shanghai_players)
                
                events.append({
                    "minute": pg['minute'],
                    "minute_extra": pg['extra'],
                    "type": "goal",
                    "team": "home" if is_home else "away",
                    "player": pg['player'],
                    "player2": "",
                    "goal_type": "penalty_goal" if pg['isPenalty'] else "goal",
                    "player_out": "",
                    "description": "GOAL"
                })
        
        # 过滤掉minute为None的events，然后重新排序
        events = [e for e in events if e.get('minute') is not None]
        events.sort(key=lambda x: (x['minute'], x.get('minute_extra', 0)))
        
        # 构建完整数据
        match_data = {
            "match_info": {
                "match_id": url.split('/')[-2],
                "date": match_info['date'],
                "time": extracted.get('matchTime', '20:00'),
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": str(match_info.get('season', 2025)),
                    "round": f"Matchweek {actual_matchweek}"
                },
                "venue": extracted.get('venue', {}),
                "referee": {
                    "main": extracted.get('referees', {}).get('main', ''),
                    "ar1": extracted.get('referees', {}).get('ar1', ''),
                    "ar2": extracted.get('referees', {}).get('ar2', ''),
                    "fourth": extracted.get('referees', {}).get('fourth', ''),
                    "var": extracted.get('referees', {}).get('var', ''),
                    "country": "China"
                }
            },
            "teams": {
                "home": {
                    "name": extracted['formations'][0].split('(')[0].strip() if len(extracted['formations']) > 0 else "",
                    "full_name": "",
                    "score": extracted['scores'][0] if len(extracted['scores']) > 0 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][0].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 0 and '(' in extracted['formations'][0] else "",
                    "coach": extracted.get('homeManager', ''),
                    "captain": extracted.get('homeCaptain', ''),
                    "lineup": extracted['lineups']['home'],
                    "substitutes": extracted['bench']['home'],
                    "substitutions": []
                },
                "away": {
                    "name": extracted['formations'][1].split('(')[0].strip() if len(extracted['formations']) > 1 else "",
                    "full_name": "",
                    "score": extracted['scores'][1] if len(extracted['scores']) > 1 else 0,
                    "score_ht": 1,
                    "formation": extracted['formations'][1].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 1 and '(' in extracted['formations'][1] else "",
                    "coach": extracted.get('awayManager', ''),
                    "captain": extracted.get('awayCaptain', ''),
                    "lineup": extracted['lineups']['away'],
                    "substitutes": extracted['bench']['away'],
                    "substitutions": []
                }
            },
            "events": events,
            "statistics": extracted['statistics'],
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "9.4-penalty-fix"
            }
        }

        return match_data, actual_matchweek
        
    except Exception as e:
        print(f"      ❌ 错误: {e}")
        return None, None

def main(season):
    print("="*70)
    print(f"上海海港{season}赛季完整数据抓取器 v9.4")
    print("修复：点球进球正确识别为 penalty_goal")
    print("="*70)
    print()
    
    with open(f'data/{season}-match_urls.json', 'r', encoding='utf-8') as f:
        url_data = json.load(f)
    
    if isinstance(url_data, list):
        matches = url_data
    else:
        matches = url_data.get('match_urls', url_data.get('matches', []))
    
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    output_dir = f'data/match-reports-{season}'
    os.makedirs(output_dir, exist_ok=True)
    
    old_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    if old_files:
        print(f"🗑️  清空旧文件: {len(old_files)}个\n")
        for f in old_files:
            os.remove(os.path.join(output_dir, f))
    
    success_count = 0
    total_events = 0
    
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match.get('match_report_url') or match.get('url') or match.get('match_url')
        
        print(f"[{i}/30] {date}")
        
        match_data, actual_round = scrape_match(url, {
            'date': date,
            'round': i,
            'season': season
        })
        
        if match_data:
            filename = f"{date}-中超-第{actual_round}轮.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            home = match_data['teams']['home']
            away = match_data['teams']['away']
            hs = home['score']
            as_ = away['score']
            events_count = len(match_data['events'])
            total_events += events_count
            
            time_info = match_data['match_info']['time']
            home_coach = home['coach'][:15] + '..' if len(home['coach']) > 15 else home['coach']
            main_ref = match_data['match_info']['referee']['main'][:15] + '..' if len(match_data['match_info']['referee']['main']) > 15 else match_data['match_info']['referee']['main']
            
            away_score = away['score']
            print(f"      ✅ {home['name']} {hs}-{away_score} {away['name']}")
            print(f"         ⏰{time_info} | 👨‍💼{home_coach} | 🎯{main_ref}")
            
            success_count += 1
        else:
            print(f"      ❌ 失败")
        
        if i < len(matches):
            time.sleep(3)
    
    print(f"\n{'='*70}")
    print("✅ 批量处理完成")
    print(f"{'='*70}")
    print(f"✓ 成功: {success_count} / 30")
    print(f"✓ 事件总数: {total_events}个")
    print(f"\n📁 保存位置: {output_dir}/")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 batch_scrape_v9.4_penalty_fix.py <赛季>")
        print("示例: python3 batch_scrape_v9.4_penalty_fix.py 2023")
        sys.exit(1)
    
    season = sys.argv[1]
    try:
        main(season)
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
