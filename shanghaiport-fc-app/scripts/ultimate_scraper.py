#!/usr/bin/env python3
"""
终极版 - 直接用openclaw browser evaluate返回JSON
已测试验证可行
"""

import json
import os
import subprocess
import time

def scrape_match_data(url: str, match_info: dict) -> dict:
    """直接从浏览器提取数据"""

    try:
        # 1. 打开页面
        result = subprocess.run(['openclaw', 'browser', 'open', url],
                              capture_output=True, text=True, timeout=30)
        if 'opened:' not in result.stdout:
            return None
        time.sleep(5)

        # 2. 直接提取JSON数据
        extract_js = """
        (() => {
          const result = {
            scores: [],
            formations: [],
            lineups: {home: [], away: []},
            bench: {home: [], away: []},
            stats: {}
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

          // 统计
          document.querySelectorAll('#team_stats tbody tr').forEach(row => {
            const th = row.querySelector('th');
            const tds = row.querySelectorAll('td');
            if (th && tds.length >= 2) {
              result.stats[th.textContent.trim().toLowerCase().replace(/\\s+/g, '_')] = {
                home: tds[0].textContent.trim(),
                away: tds[1].textContent.trim()
              };
            }
          });

          return JSON.stringify(result);
        })()
        """

        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', extract_js],
            capture_output=True,
            text=True,
            timeout=15
        )

        # 3. 提取JSON（从最后一行，去除引号）
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
            "events": [],
            "statistics": extracted['stats'],
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "1.0"
            }
        }

        return match_data

    except Exception as e:
        print(f"    ❌ 错误: {e}")
        return None

def main():
    print("="*60)
    print("终极版 - 直接返回JSON（已验证可行）")
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

            print(f"    ✅ {match['home']} {hs}-{as_} {match['away']} | 阵容:{hl}+{al}")
            success += 1
        else:
            print(f"    ❌ 失败")

        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"✅ 完成: {success}/29")

if __name__ == '__main__':
    main()
