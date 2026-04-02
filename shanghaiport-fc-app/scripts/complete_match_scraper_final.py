#!/usr/bin/env python3
"""
完整版 - 包含events和statistics的抓取
版本: 3.0 - 补充完整统计数据
"""

import json
import os
import subprocess
import time

def scrape_match_data(url: str, match_info: dict) -> dict:
    """从浏览器提取完整数据"""

    try:
        # 1. 打开页面
        result = subprocess.run(['openclaw', 'browser', 'open', url],
                              capture_output=True, text=True, timeout=30)
        if 'opened:' not in result.stdout:
            return None
        time.sleep(5)

        # 2. 提取完整JSON数据
        extract_js = """
        (() => {
          const result = {
            scores: [],
            formations: [],
            lineups: {home: [], away: []},
            bench: {home: [], away: []},
            events: [],
            statistics: {},
            player_stats: {home: [], away: []}
          };

          // 使用Unicode转义右单引号
          const timeRegex = /(\\d+\\+?\\d*)['\\u2019]/;

          // 比分
          document.querySelectorAll('.score').forEach(el => {
            const s = parseInt(el.textContent);
            if (!isNaN(s)) result.scores.push(s);
          });

          // 阵容
          document.querySelectorAll('.lineup').forEach((table, idx) => {
            const starters = [];
            const subs = [];
            let isBench = false;

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

            if (idx === 0) {
              result.lineups.home = starters;
              result.bench.home = subs;
              result.formations.push(table.querySelector('th')?.textContent || '');
            } else {
              result.lineups.away = starters;
              result.bench.away = subs;
              result.formations.push(table.querySelector('th')?.textContent || '');
            }
          });

          // 比赛事件
          const allDivs = document.querySelectorAll('div');
          
          allDivs.forEach(div => {
            if (div.className === 'event a' || div.className === 'event b') {
              const text = div.textContent;
              const match = text.match(timeRegex);
              const links = div.querySelectorAll('a[href*="/players/"]');
              
              if (!match || links.length === 0) return;
              
              const time = match[1];
              const player = links[0].textContent.trim();
              const team = div.className === 'event a' ? 'home' : 'away';
              
              // 确定事件类型
              const iconDiv = div.querySelector('div[class*="event_icon"]');
              let type = 'unknown';
              let assist = '';
              let playerOut = '';
              
              if (iconDiv) {
                const iconClass = iconDiv.className;
                if (iconClass.includes('own_goal')) type = 'own_goal';
                else if (iconClass.includes('goal')) type = 'goal';
                else if (iconClass.includes('yellow')) type = 'yellow_card';
                else if (iconClass.includes('red')) type = 'red_card';
                else if (iconClass.includes('substitute')) type = 'substitution';
              }
              
              // 提取助攻或被替换球员
              if (type === 'goal' && text.includes('Assist:') && links.length >= 2) {
                assist = links[1].textContent.trim();
              } else if (type === 'substitution' && links.length >= 2) {
                playerOut = links[1].textContent.trim();
              }
              
              result.events.push({
                time,
                type,
                player,
                assist,
                playerOut,
                team
              });
            }
          });

          // 统计数据 - 完整提取
          const bodyText = document.body.innerText;
          
          // 1. Possession
          const possMatch = bodyText.match(/Possession[\\s\\S]*?(\\d+)%[\\s]*(\\d+)%/);
          if (possMatch) {
            result.statistics.possession = {home: possMatch[1] + '%', away: possMatch[2] + '%'};
          }
          
          // 2. Shots on Target
          const shotsMatch = bodyText.match(/Shots on Target[\\s\\S]*?(\\d+) of (\\d+)[^\\d]*(\\d+)%[^\\d]*(\\d+)%[\\s\\S]*?(\\d+) of (\\d+)/);
          if (shotsMatch) {
            result.statistics.shots_on_target = {
              home: shotsMatch[1] + '/' + shotsMatch[2],
              away: shotsMatch[5] + '/' + shotsMatch[6]
            };
          }
          
          // 3. Saves
          const savesMatch = bodyText.match(/Saves[\\s\\S]*?(\\d+) of (\\d+)[^\\d]*(\\d+)%[^\\d]*(\\d+)%[\\s\\S]*?(\\d+) of (\\d+)/);
          if (savesMatch) {
            result.statistics.saves = {
              home: savesMatch[1] + '/' + savesMatch[2],
              away: savesMatch[5] + '/' + savesMatch[6]
            };
          }
          
          // 4. Fouls
          const foulsMatch = bodyText.match(/(\\d+)\\s+Fouls\\s+(\\d+)/);
          if (foulsMatch) {
            result.statistics.fouls = {home: foulsMatch[1], away: foulsMatch[2]};
          }
          
          // 5. Corners
          const cornersMatch = bodyText.match(/(\\d+)\\s+Corners\\s+(\\d+)/);
          if (cornersMatch) {
            result.statistics.corners = {home: cornersMatch[1], away: cornersMatch[2]};
          }
          
          // 6. Crosses
          const crossesMatch = bodyText.match(/(\\d+)\\s+Crosses\\s+(\\d+)/);
          if (crossesMatch) {
            result.statistics.crosses = {home: crossesMatch[1], away: crossesMatch[2]};
          }
          
          // 7. Interceptions
          const intMatch = bodyText.match(/(\\d+)\\s+Interceptions\\s+(\\d+)/);
          if (intMatch) {
            result.statistics.interceptions = {home: intMatch[1], away: intMatch[2]};
          }
          
          // 8. Offsides
          const offMatch = bodyText.match(/(\\d+)\\s+Offsides\\s+(\\d+)/);
          if (offMatch) {
            result.statistics.offsides = {home: offMatch[1], away: offMatch[2]};
          }

          return JSON.stringify(result);
        })()
        """

        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', extract_js],
            capture_output=True,
            text=True,
            timeout=15
        )

        # 3. 提取JSON
        lines = result.stdout.strip().split('\n')
        json_line = None
        for line in reversed(lines):
            if line.strip().startswith('"') and '{' in line:
                json_line = line.strip().strip('"').replace('\\"', '"')
                break

        if not json_line:
            return None

        extracted = json.loads(json_line)

        # 4. 构建完整数据
        match_data = {
            "match_info": {
                "match_id": url.split('/')[-2],
                "date": match_info['date'],
                "time": "20:00",
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": "2024",
                    "round": f"Matchweek {match_info['index']}"
                },
                "venue": {"name": "", "city": "", "attendance": 0},
                "referee": {"name": "待补充", "country": "China"}
            },
            "teams": {
                "home": {
                    "name": match_info['home'],
                    "full_name": "",
                    "score": extracted['scores'][0] if len(extracted['scores']) > 0 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][0].split('(')[1].replace(')', '') if len(extracted['formations']) > 0 and '(' in extracted['formations'][0] else "",
                    "coach": "",
                    "captain": "",
                    "lineup": extracted['lineups']['home'],
                    "substitutes": extracted['bench']['home'],
                    "substitutions": []
                },
                "away": {
                    "name": match_info['away'],
                    "full_name": "",
                    "score": extracted['scores'][1] if len(extracted['scores']) > 1 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][1].split('(')[1].replace(')', '') if len(extracted['formations']) > 1 and '(' in extracted['formations'][1] else "",
                    "coach": "",
                    "captain": "",
                    "lineup": extracted['lineups']['away'],
                    "substitutes": extracted['bench']['away'],
                    "substitutions": []
                }
            },
            "events": extracted['events'],
            "statistics": extracted['statistics'],
            "player_stats": extracted['player_stats'],
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "3.0"
            }
        }

        return match_data

    except Exception as e:
        print(f"    ❌ 错误: {e}")
        return None

def main():
    print("="*60)
    print("完整版 v3.0 - 包含events和完整statistics")
    print("="*60)

    with open('data/match_urls.json') as f:
        matches = json.load(f)

    output_dir = 'data/match-reports-template-format'
    os.makedirs(output_dir, exist_ok=True)

    success = 0
    for i, match in enumerate(matches[1:], 2):
        print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")

        data = scrape_match_data(match['url'], match)

        if data:
            filename = f"{output_dir}/{match['date']}-中超-第{i}轮-complete.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            hs = data['teams']['home']['score']
            as_ = data['teams']['away']['score']
            hl = len(data['teams']['home']['lineup'])
            al = len(data['teams']['away']['lineup'])
            events_count = len(data['events'])
            stats_count = len(data['statistics'])

            print(f"    ✅ {match['home']} {hs}-{as_} {match['away']}")
            print(f"       阵容:{hl}+{al} | 事件:{events_count} | 统计:{stats_count}项")
            success += 1
        else:
            print(f"    ❌ 失败")

        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"✅ 完成: {success}/29")

if __name__ == '__main__':
    main()
