#!/usr/bin/env python3
"""
完整版 - 包含events和statistics的抓取
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

          // 比赛事件 - Match Summary部分
          const eventDivs = document.querySelectorAll('div[class*="event"]');
          document.querySelectorAll('div').forEach(div => {
            // 查找包含时间和比分的事件
            const timeText = div.textContent.match(/(\\d+\\+?\\d*)['']/);
            if (timeText) {
              const links = div.querySelectorAll('a[href*="/players/"]');
              if (links.length > 0) {
                const text = div.textContent;
                let eventType = 'unknown';
                let player = '';
                let assist = '';
                let team = 'unknown';

                // 判断事件类型
                if (text.includes('Own Goal')) {
                  eventType = 'own_goal';
                  player = links[0]?.textContent?.trim() || '';
                } else if (text.includes('Assist:')) {
                  eventType = 'goal';
                  player = links[0]?.textContent?.trim() || '';
                  assist = links[1]?.textContent?.trim() || '';
                } else if (text.includes('for')) {
                  eventType = 'substitution';
                  player = links[0]?.textContent?.trim() || '';
                } else if (text.includes('Yellow')) {
                  eventType = 'yellow_card';
                  player = links[0]?.textContent?.trim() || '';
                } else if (text.includes('Red')) {
                  eventType = 'red_card';
                  player = links[0]?.textContent?.trim() || '';
                } else if (links.length === 1 && !text.includes('for')) {
                  // 可能是进球或牌
                  eventType = 'goal';
                  player = links[0]?.textContent?.trim() || '';
                }

                if (player) {
                  result.events.push({
                    time: timeText[1],
                    type: eventType,
                    player: player,
                    assist: assist,
                    team: team
                  });
                }
              }
            }
          });

          // 统计数据 - Team Stats表格
          const statsTable = document.querySelector('#team_stats') || 
                            document.querySelector('table[id*="stats"]');
          if (statsTable) {
            statsTable.querySelectorAll('tbody tr').forEach(row => {
              const th = row.querySelector('th');
              const tds = row.querySelectorAll('td');
              if (th && tds.length >= 2) {
                const statName = th.textContent.trim().toLowerCase().replace(/\\s+/g, '_');
                result.statistics[statName] = {
                  home: tds[0].textContent.trim(),
                  away: tds[1].textContent.trim()
                };
              }
            });
          }

          // 备用：从页面文本提取统计
          if (Object.keys(result.statistics).length === 0) {
            const statTexts = ['Possession', 'Shots on Target', 'Saves', 'Fouls', 'Corners', 'Crosses', 'Interceptions', 'Offsides'];
            statTexts.forEach(stat => {
              const regex = new RegExp(stat + '.*?(\\d+).*?(\\d+)', 'i');
              const match = document.body.textContent.match(regex);
              if (match) {
                result.statistics[stat.toLowerCase().replace(/\\s+/g, '_')] = {
                  home: match[1],
                  away: match[2]
                };
              }
            });
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
                "version": "2.0"
            }
        }

        return match_data

    except Exception as e:
        print(f"    ❌ 错误: {e}")
        return None

def main():
    print("="*60)
    print("完整版 - 包含events和statistics")
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
            print(f"       阵容:{hl}+{al} | 事件:{events_count} | 统计:{stats_count}")
            success += 1
        else:
            print(f"    ❌ 失败")

        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"✅ 完成: {success}/29")

if __name__ == '__main__':
    main()
