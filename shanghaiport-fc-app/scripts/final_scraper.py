#!/usr/bin/env python3
"""
最终修复版 - 按照模板格式抓取所有29轮比赛
"""

import json
import os
import subprocess
import time

def scrape_match_complete(url: str, match_info: dict) -> dict:
    """完整抓取一场比赛的所有数据"""

    try:
        # 1. 打开页面
        result = subprocess.run(['openclaw', 'browser', 'open', url], capture_output=True, text=True, timeout=30)
        if 'opened:' not in result.stdout:
            return None
        time.sleep(5)

        # 2. 提取数据的JavaScript代码
        extract_js = """
        (() => {
          const result = {
            scores: [],
            formations: [],
            lineups: {home: [], away: []},
            bench: {home: [], away: []},
            stats: {},
            venue: {},
            attendance: 0
          };

          // 提取比分
          document.querySelectorAll('.score').forEach(el => result.scores.push(parseInt(el.textContent) || 0));

          // 提取阵型和阵容
          const lineupTables = document.querySelectorAll('.lineup');
          lineupTables.forEach((table, idx) => {
            const formation = table.querySelector('th')?.textContent || '';
            result.formations.push(formation);

            const starters = [];
            const bench = [];
            let isBench = false;

            table.querySelectorAll('tr').forEach(row => {
              if (row.textContent.includes('Bench')) {
                isBench = true;
                return;
              }

              const playerLink = row.querySelector('a[href*="/players/"]');
              if (playerLink) {
                const tds = row.querySelectorAll('td');
                const player = {
                  number: tds[0]?.textContent?.trim() || '',
                  name: playerLink.textContent?.trim() || '',
                  position: tds[1]?.textContent?.trim() || '',
                  country: 'Unknown'
                };

                if (isBench) bench.push(player);
                else starters.push(player);
              }
            });

            if (idx === 0) {
              result.lineups.home = starters;
              result.bench.home = bench;
            } else {
              result.lineups.away = starters;
              result.bench.away = bench;
            }
          });

          // 提取统计
          const statRows = document.querySelectorAll('#team_stats tr');
          statRows.forEach(row => {
            const th = row.querySelector('th');
            const tds = row.querySelectorAll('td');
            if (th && tds.length >= 2) {
              const statName = th.textContent?.trim().toLowerCase().replace(/\\s+/g, '_');
              result.stats[statName] = {
                home: tds[0]?.textContent?.trim() || '0',
                away: tds[1]?.textContent?.trim() || '0'
              };
            }
          });

          // 提取球场信息
          const venueText = document.body.textContent;
          const venueMatch = venueText.match(/Venue:\\s*([^,\\n]+?)(?:,\\s*([^\\n]+?))?(?:\\s+Officials|\\s+Attendance|$)/);
          if (venueMatch) {
            result.venue.name = venueMatch[1]?.trim() || '';
            result.venue.city = venueMatch[2]?.trim() || '';
          }

          const attendanceMatch = venueText.match(/Attendance:\\s*([\\d,]+)/);
          if (attendanceMatch) {
            result.attendance = parseInt(attendanceMatch[1].replace(',', '')) || 0;
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

        # 3. 提取JSON - 从最后一行，去除引号
        lines = result.stdout.strip().split('\n')
        json_line = lines[-1].strip().strip('"')
        extracted = json.loads(json_line)

        # 4. 构建完整数据结构
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
                "venue": {
                    "name": extracted.get('venue', {}).get('name', ''),
                    "city": extracted.get('venue', {}).get('city', ''),
                    "attendance": extracted.get('attendance', 0)
                },
                "referee": {
                    "name": "待补充",
                    "country": "China"
                }
            },
            "teams": {
                "home": {
                    "name": match_info['home'],
                    "full_name": "",
                    "score": extracted['scores'][0] if len(extracted['scores']) > 0 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][0].split('(')[1].replace(')', '') if len(extracted['formations']) > 0 else "",
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
                    "formation": extracted['formations'][1].split('(')[1].replace(')', '') if len(extracted['formations']) > 1 else "",
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
    """主函数"""

    print("="*60)
    print("最终修复版 - 按照模板格式抓取所有29轮比赛")
    print("="*60)
    print()

    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)

    print(f"📋 共 {len(matches)} 场比赛\n")

    # 创建输出目录
    output_dir = 'data/match-reports-template-format'
    os.makedirs(output_dir, exist_ok=True)

    # 处理所有比赛（跳过第1轮，从第2轮开始）
    success = 0
    failed = []

    for i, match in enumerate(matches[1:], 2):  # 从第2轮开始
        print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")

        match_data = scrape_match_complete(match['url'], match)

        if match_data:
            filename = f"{output_dir}/{match['date']}-中超-第{i}轮-complete.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)

            home_score = match_data['teams']['home']['score']
            away_score = match_data['teams']['away']['score']
            home_lineup = len(match_data['teams']['home']['lineup'])
            away_lineup = len(match_data['teams']['away']['lineup'])

            print(f"    ✅ 比分: {match['home']} {home_score} - {away_score} {match['away']}")
            print(f"    ✅ 阵容: 主队 {home_lineup} 人, 客队 {away_lineup} 人")
            success += 1
        else:
            print(f"    ❌ 抓取失败")
            failed.append(i)

        time.sleep(2)

    # 总结
    print(f"\n{'='*60}")
    print("✅ 批量处理完成")
    print(f"{'='*60}")
    print(f"成功: {success} / 29")
    print(f"失败: {len(failed)}")

    if failed:
        print(f"\n失败场次: {failed}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
