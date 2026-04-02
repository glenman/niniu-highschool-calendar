#!/usr/bin/env python3
"""
完整版 - 使用CDP抓取
版本: 3.1 - 适配CDP
"""

import json
import os
import subprocess
import time

def scrape_match_data(url: str, match_info: dict) -> dict:
    """从浏览器提取完整数据"""

    try:
        # 1. 打开页面
        print(f"    → 打开页面...")
        result = subprocess.run(
            ['agent-browser', '--cdp', '9222', 'open', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        time.sleep(8)

        # 2. 提取完整JSON数据
        print(f"    → 提取数据...")
        extract_js = """
        (() => {
          const result = {
            scores: [],
            formations: [],
            lineups: {home: [], away: []},
            bench: {home: [], away: []},
            events: [],
            statistics: {},
            manager: [],
            captain: [],
            venue: {name: '', city: '', attendance: 0},
            referee: ''
          };

          // 比分
          document.querySelectorAll('.score').forEach(el => {
            const s = parseInt(el.textContent);
            if (!isNaN(s)) result.scores.push(s);
          });

          // 阵容表
          const lineupTables = document.querySelectorAll('table.lineup');
          let teamIdx = 0;
          
          lineupTables.forEach(table => {
            const starters = [];
            const subs = [];
            let isBench = false;
            
            // 获取阵型
            const header = table.querySelector('th');
            if (header) {
              result.formations.push(header.textContent.trim());
            }

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

            if (teamIdx === 0) {
              result.lineups.home = starters;
              result.bench.home = subs;
            } else {
              result.lineups.away = starters;
              result.bench.away = subs;
            }
            teamIdx++;
          });

          // 教练
          document.body.innerHTML.match(/Manager:\\s*([^<\\n]+)/g)?.forEach(m => {
            const name = m.replace('Manager:', '').trim();
            if (name) result.manager.push(name);
          });

          // 队长
          document.body.innerHTML.match(/Captain:\\s*([^<\\n]+)/g)?.forEach(m => {
            const name = m.replace('Captain:', '').trim();
            if (name) result.captain.push(name);
          });

          // 球场信息
          const venueMatch = document.body.innerText.match(/Venue:\\s*([^,\\n]+)/);
          if (venueMatch) result.venue.name = venueMatch[1].trim();
          
          const attendMatch = document.body.innerText.match(/Attendance:\\s*([\\d,]+)/);
          if (attendMatch) result.venue.attendance = parseInt(attendMatch[1].replace(',', ''));

          // 比赛事件
          const timeRegex = /(\\d+\\+?\\d*)['']/;
          const eventDivs = document.querySelectorAll('div.event');
          
          eventDivs.forEach(div => {
            const text = div.textContent;
            const match = text.match(timeRegex);
            const links = div.querySelectorAll('a[href*="/players/"]');
            
            if (!match || links.length === 0) return;
            
            const eventTime = match[1];
            const player = links[0].textContent.trim();
            const team = div.classList.contains('event_a') ? 'home' : 'away';
            
            let type = 'unknown';
            let assist = '';
            let playerOut = '';
            
            if (text.includes('Goal')) type = 'goal';
            else if (text.includes('Yellow Card')) type = 'yellow_card';
            else if (text.includes('Red Card')) type = 'red_card';
            else if (text.includes('Substitute')) type = 'substitution';
            
            if (type === 'goal' && text.includes('Assist:') && links.length >= 2) {
              assist = links[1].textContent.trim();
            } else if (type === 'substitution' && links.length >= 2) {
              playerOut = links[1].textContent.trim();
            }
            
            result.events.push({
              time: eventTime,
              type,
              player,
              assist,
              playerOut,
              team
            });
          });

          // 统计数据
          const bodyText = document.body.innerText;
          
          const possMatch = bodyText.match(/Possession[\\s\\S]*?(\\d+)%[\\s]*(\\d+)%/);
          if (possMatch) result.statistics.possession = {home: possMatch[1], away: possMatch[2]};
          
          const shotsMatch = bodyText.match(/Shots on Target[\\s\\S]*?(\\d+) of (\\d+).*?(\\d+) of (\\d+)/);
          if (shotsMatch) {
            result.statistics.shots_on_target = {home: shotsMatch[1], away: shotsMatch[3]};
            result.statistics.shots = {home: shotsMatch[2], away: shotsMatch[4]};
          }
          
          const savesMatch = bodyText.match(/Saves[\\s\\S]*?(\\d+) of (\\d+).*?(\\d+) of (\\d+)/);
          if (savesMatch) result.statistics.saves = {home: savesMatch[1], away: savesMatch[3]};
          
          const foulsMatch = bodyText.match(/(\\d+)\\s+Fouls\\s+(\\d+)/);
          if (foulsMatch) result.statistics.fouls = {home: foulsMatch[1], away: foulsMatch[2]};
          
          const cornersMatch = bodyText.match(/(\\d+)\\s+Corners\\s+(\\d+)/);
          if (cornersMatch) result.statistics.corners = {home: cornersMatch[1], away: cornersMatch[2]};
          
          const crossesMatch = bodyText.match(/(\\d+)\\s+Crosses\\s+(\\d+)/);
          if (crossesMatch) result.statistics.crosses = {home: crossesMatch[1], away: crossesMatch[2]};
          
          const intMatch = bodyText.match(/(\\d+)\\s+Interceptions\\s+(\\d+)/);
          if (intMatch) result.statistics.interceptions = {home: intMatch[1], away: intMatch[2]};
          
          const offMatch = bodyText.match(/(\\d+)\\s+Offsides?\\s+(\\d+)/);
          if (offMatch) result.statistics.offsides = {home: offMatch[1], away: offMatch[2]};

          return JSON.stringify(result);
        })()
        """

        result = subprocess.run(
            ['agent-browser', '--cdp', '9222', 'eval', extract_js],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0 or not result.stdout.strip():
            print(f"    ❌ 提取失败")
            return None

        # 解析结果 - agent-browser返回的是带引号的JSON字符串
        output = result.stdout.strip()
        if output.startswith('"') and output.endswith('"'):
            # 去掉外层引号
            output = output[1:-1]
            # 处理转义
            output = output.replace('\\"', '"').replace('\\n', '\n')
        
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
                    "round": f"Matchweek {match_info.get('round', 1)}"
                },
                "venue": extracted.get('venue', {}),
                "referee": {"name": extracted.get('referee', ''), "country": "China"}
            },
            "teams": {
                "home": {
                    "name": match_info.get('home', ''),
                    "full_name": "",
                    "score": extracted['scores'][0] if len(extracted['scores']) > 0 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][0].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 0 and '(' in extracted['formations'][0] else "",
                    "coach": extracted['manager'][0] if len(extracted.get('manager', [])) > 0 else "",
                    "captain": extracted['captain'][0] if len(extracted.get('captain', [])) > 0 else "",
                    "lineup": extracted['lineups'].get('home', []),
                    "substitutes": extracted['bench'].get('home', []),
                    "substitutions": []
                },
                "away": {
                    "name": match_info.get('away', ''),
                    "full_name": "",
                    "score": extracted['scores'][1] if len(extracted['scores']) > 1 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][1].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 1 and '(' in extracted['formations'][1] else "",
                    "coach": extracted['manager'][1] if len(extracted.get('manager', [])) > 1 else "",
                    "captain": extracted['captain'][1] if len(extracted.get('captain', [])) > 1 else "",
                    "lineup": extracted['lineups'].get('away', []),
                    "substitutes": extracted['bench'].get('away', []),
                    "substitutions": []
                }
            },
            "events": extracted.get('events', []),
            "statistics": extracted.get('statistics', {}),
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "3.1-cdp"
            }
        }

        return match_data

    except Exception as e:
        print(f"    ❌ 错误: {e}")
        return None

def main():
    print("="*70)
    print("完整版 v3.1 - 使用CDP抓取完整数据")
    print("="*70)
    print()

    # 读取URL列表
    with open('data/2023-match_urls.json') as f:
        data = json.load(f)
    
    matches = data['match_urls']

    output_dir = 'data/match-reports-2023'
    os.makedirs(output_dir, exist_ok=True)

    success = 0
    
    # 先处理前5场测试
    for i, match in enumerate(matches[:5], 1):
        url = match['match_report_url']
        date = match['date']
        
        print(f"\n[{i}/5] {date} - 第{i}轮")

        data = scrape_match_data(url, {
            'date': date,
            'round': i,
            'home': '',
            'away': ''
        })

        if data:
            filename = f"{output_dir}/{date}-中超-第{i}轮.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            hs = data['teams']['home']['score']
            as_ = data['teams']['away']['score']
            hl = len(data['teams']['home']['lineup'])
            al = len(data['teams']['away']['lineup'])
            events_count = len(data['events'])
            stats_count = len(data['statistics'])

            print(f"    ✅ 比分: {hs}-{as_}")
            print(f"       球员: {hl}+{al} | 事件: {events_count} | 统计: {stats_count}项")
            success += 1
        else:
            print(f"    ❌ 失败")

        time.sleep(2)

    print(f"\n{'='*70}")
    print(f"✅ 完成: {success}/5")

if __name__ == '__main__':
    main()
