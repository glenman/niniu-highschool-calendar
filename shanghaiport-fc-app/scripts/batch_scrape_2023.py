#!/usr/bin/env python3
"""
上海海港2023赛季完整数据批量抓取器
使用CDP提取FBref全部30场比赛数据
"""

import json
import os
import subprocess
import time
from datetime import datetime

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
        time.sleep(8)

        # 2. 提取数据
        js_code = """(() => {
  const data = {
    scores: [],
    formations: [],
    players: {home: {starters: [], subs: []}, away: {starters: [], subs: []}},
    events: [],
    stats: {},
    manager: [],
    captain: [],
    venue: {name: '', city: '', attendance: 0},
    referee: ''
  };
  
  // 比分
  document.querySelectorAll('.score').forEach(el => {
    const s = parseInt(el.textContent);
    if (!isNaN(s)) data.scores.push(s);
  });
  
  // 阵容表
  const tables = document.querySelectorAll('table');
  let tableCount = 0;
  
  tables.forEach(table => {
    const text = table.textContent;
    if (text.includes('Bench') && text.includes('(') && text.includes(')')) {
      const header = table.querySelector('th');
      if (header) {
        data.formations.push(header.textContent.trim());
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
        data.players.home.starters = starters;
        data.players.home.subs = subs;
      } else {
        data.players.away.starters = starters;
        data.players.away.subs = subs;
      }
      tableCount++;
    }
  });
  
  // 教练和队长
  const body = document.body.innerHTML;
  const managerMatch = body.match(/Manager:\\s*([^<\\n]+)/g);
  if (managerMatch) {
    managerMatch.forEach(m => {
      const name = m.replace('Manager:', '').trim();
      if (name) data.manager.push(name);
    });
  }
  
  const captainMatch = body.match(/Captain:\\s*([^<\\n]+)/g);
  if (captainMatch) {
    captainMatch.forEach(m => {
      const name = m.replace('Captain:', '').trim();
      if (name) data.captain.push(name);
    });
  }
  
  // 球场信息
  const bodyText = document.body.innerText;
  const venueMatch = bodyText.match(/Venue:\\s*([^,\\n]+)/);
  if (venueMatch) data.venue.name = venueMatch[1].trim();
  
  const attendMatch = bodyText.match(/Attendance:\\s*([\\d,]+)/);
  if (attendMatch) data.venue.attendance = parseInt(attendMatch[1].replace(',', ''));
  
  const refMatch = bodyText.match(/Referee:\\s*([^,\\n]+)/);
  if (refMatch) data.referee = refMatch[1].trim();
  
  // 统计数据
  const possMatch = bodyText.match(/Possession[\\s\\S]*?(\\d+)%[\\s]*(\\d+)%/);
  if (possMatch) data.stats.possession = {home: parseInt(possMatch[1]), away: parseInt(possMatch[2])};
  
  const sotMatch = bodyText.match(/Shots on Target[\\s\\S]*?(\\d+) of (\\d+).*?(\\d+) of (\\d+)/);
  if (sotMatch) {
    data.stats.shots_on_target = {home: parseInt(sotMatch[1]), away: parseInt(sotMatch[3])};
    data.stats.shots = {home: parseInt(sotMatch[2]), away: parseInt(sotMatch[4])};
  }
  
  const savesMatch = bodyText.match(/Saves[\\s\\S]*?(\\d+) of (\\d+).*?(\\d+) of (\\d+)/);
  if (savesMatch) data.stats.saves = {home: parseInt(savesMatch[1]), away: parseInt(savesMatch[3])};
  
  const foulsMatch = bodyText.match(/(\\d+)\\s+Fouls\\s+(\\d+)/);
  if (foulsMatch) data.stats.fouls = {home: parseInt(foulsMatch[1]), away: parseInt(foulsMatch[2])};
  
  const cornersMatch = bodyText.match(/(\\d+)\\s+Corners\\s+(\\d+)/);
  if (cornersMatch) data.stats.corners = {home: parseInt(cornersMatch[1]), away: parseInt(cornersMatch[2])};
  
  const crossesMatch = bodyText.match(/(\\d+)\\s+Crosses\\s+(\\d+)/);
  if (crossesMatch) data.stats.crosses = {home: parseInt(crossesMatch[1]), away: parseInt(crossesMatch[2])};
  
  const intMatch = bodyText.match(/(\\d+)\\s+Interceptions\\s+(\\d+)/);
  if (intMatch) data.stats.interceptions = {home: parseInt(intMatch[1]), away: parseInt(intMatch[2])};
  
  const offMatch = bodyText.match(/(\\d+)\\s+Offsides?\\s+(\\d+)/);
  if (offMatch) data.stats.offsides = {home: parseInt(offMatch[1]), away: parseInt(offMatch[2])};
  
  // 黄牌红牌
  data.stats.yellow_cards = {home: 0, away: 0};
  data.stats.red_cards = {home: 0, away: 0};
  
  return JSON.stringify(data);
})()"""

        result = subprocess.run(
            ['agent-browser', '--cdp', '9222', 'eval', js_code],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode != 0:
            return None
        
        # 解析数据
        output = result.stdout.strip()
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1].replace('\\"', '"')
        
        extracted = json.loads(output)
        
        # 3. 构建完整数据结构
        match_data = {
            "match_info": {
                "match_id": match_info['match_id'],
                "date": match_info['date'],
                "time": "20:00",
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": "2023",
                    "round": f"Matchweek {match_info['round']}"
                },
                "venue": extracted.get('venue', {}),
                "referee": {
                    "name": extracted.get('referee', ''),
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
                    "coach": extracted['manager'][0] if len(extracted.get('manager', [])) > 0 else "",
                    "captain": extracted['captain'][0] if len(extracted.get('captain', [])) > 0 else "",
                    "lineup": extracted['players']['home']['starters'],
                    "substitutes": extracted['players']['home']['subs'],
                    "substitutions": []
                },
                "away": {
                    "name": extracted['formations'][1].split('(')[0].strip() if len(extracted['formations']) > 1 else "",
                    "full_name": "",
                    "score": extracted['scores'][1] if len(extracted['scores']) > 1 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][1].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 1 and '(' in extracted['formations'][1] else "",
                    "coach": extracted['manager'][1] if len(extracted.get('manager', [])) > 1 else "",
                    "captain": extracted['captain'][1] if len(extracted.get('captain', [])) > 1 else "",
                    "lineup": extracted['players']['away']['starters'],
                    "substitutes": extracted['players']['away']['subs'],
                    "substitutions": []
                }
            },
            "events": extracted.get('events', []),
            "statistics": extracted.get('stats', {}),
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "3.0-cdp"
            }
        }
        
        return match_data
        
    except Exception as e:
        print(f"      ❌ 错误: {e}")
        return None

def main():
    print("="*70)
    print("上海海港2023赛季完整数据批量抓取")
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
    failed_matches = []
    
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match['match_report_url']
        
        print(f"[{i}/30] {date} - 第{i}轮")
        
        match_data = scrape_match(url, {
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
            
            # 显示结果
            home = match_data['teams']['home']
            away = match_data['teams']['away']
            hs = home['score']
            as_ = away['score']
            hl = len(home['lineup'])
            al = len(away['lineup'])
            stats_count = len(match_data['statistics'])
            
            print(f"      ✅ {home['name']} {hs}-{as_} {away['name']}")
            print(f"         球员: {hl}+{al} | 统计: {stats_count}项")
            success_count += 1
        else:
            print(f"      ❌ 失败")
            failed_matches.append(f"第{i}轮-{date}")
        
        # 休息一下
        if i < len(matches):
            time.sleep(3)
    
    # 总结
    print(f"\n{'='*70}")
    print("✅ 批量处理完成")
    print(f"{'='*70}")
    print(f"✓ 成功: {success_count} / 30")
    print(f"✗ 失败: {len(failed_matches)} / 30")
    
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
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
