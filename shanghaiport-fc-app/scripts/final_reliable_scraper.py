#!/usr/bin/env python3
"""
最可靠的方案：使用openclaw browser抓取HTML，然后用BeautifulSoup解析
"""

import json
import os
import subprocess
import time
from bs4 import BeautifulSoup
import re

def scrape_match_html(url: str) -> str:
    """抓取比赛页面的HTML"""
    try:
        # 打开页面
        subprocess.run(['openclaw', 'browser', 'open', url],
                      capture_output=True, text=True, timeout=30)
        time.sleep(5)

        # 获取HTML
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', 'document.documentElement.outerHTML'],
            capture_output=True, text=True, timeout=15
        )

        # 提取HTML（去除日志）
        lines = result.stdout.split('\n')
        html_lines = [line for line in lines if not line.startswith('[')
                     and not line.startswith('Config')
                     and not line.startswith('│')
                     and not line.startswith('├')
                     and not line.startswith('╯')
                     and not line.startswith('╮')]

        html = '\n'.join(html_lines)
        return html

    except Exception as e:
        print(f"    ❌ 错误: {e}")
        return ""

def parse_match_data(html: str, match_info: dict) -> dict:
    """解析HTML提取比赛数据"""

    soup = BeautifulSoup(html, 'html.parser')

    # 1. 提取比分
    scores = []
    for score_div in soup.find_all('div', class_='score'):
        score_text = score_div.get_text(strip=True)
        if score_text.isdigit():
            scores.append(int(score_text))

    # 2. 提取阵容
    def parse_lineup(table):
        """解析阵容表格"""
        lineup = []
        bench = []
        is_bench = False

        for row in table.find_all('tr'):
            if 'Bench' in row.get_text():
                is_bench = True
                continue

            player_link = row.find('a', href=lambda x: x and '/players/' in x)
            if player_link:
                tds = row.find_all('td')
                player = {
                    'number': tds[0].get_text(strip=True) if len(tds) > 0 else '',
                    'name': player_link.get_text(strip=True),
                    'position': tds[1].get_text(strip=True) if len(tds) > 1 else '',
                    'country': 'Unknown'
                }

                if is_bench:
                    bench.append(player)
                else:
                    lineup.append(player)

        return lineup, bench

    lineups = soup.find_all('table', class_='lineup')
    home_lineup, home_bench = parse_lineup(lineups[0]) if len(lineups) > 0 else ([], [])
    away_lineup, away_bench = parse_lineup(lineups[1]) if len(lineups) > 1 else ([], [])

    # 3. 提取阵型
    formations = []
    for lineup_table in lineups[:2]:
        th = lineup_table.find('th')
        if th:
            formation_text = th.get_text(strip=True)
            formation_match = re.search(r'\((\d+-\d+-\d+)\)', formation_text)
            if formation_match:
                formations.append(formation_match.group(1))

    # 4. 提取统计
    stats = {}
    team_stats = soup.find('div', id='team_stats')
    if team_stats:
        for row in team_stats.find_all('tr'):
            th = row.find('th')
            tds = row.find_all('td')
            if th and len(tds) >= 2:
                stat_name = th.get_text(strip=True).lower().replace(' ', '_')
                stats[stat_name] = {
                    'home': tds[0].get_text(strip=True),
                    'away': tds[1].get_text(strip=True)
                }

    # 5. 提取球场信息
    venue = {'name': '', 'city': ''}
    attendance = 0

    venue_div = soup.find('div', string=re.compile('Venue:'))
    if venue_div:
        venue_text = venue_div.get_text()
        venue_match = re.search(r'Venue:\s*([^,\n]+)(?:,\s*([^\n]+))?', venue_text)
        if venue_match:
            venue['name'] = venue_match.group(1).strip()
            if venue_match.group(2):
                venue['city'] = venue_match.group(2).strip()

    attendance_div = soup.find('div', string=re.compile('Attendance:'))
    if attendance_div:
        attendance_text = attendance_div.get_text()
        attendance_match = re.search(r'Attendance:\s*([\d,]+)', attendance_text)
        if attendance_match:
            attendance = int(attendance_match.group(1).replace(',', ''))

    # 6. 构建完整数据结构
    match_data = {
        "match_info": {
            "match_id": match_info['url'].split('/')[-2],
            "date": match_info['date'],
            "time": "20:00",
            "competition": {
                "name": "Chinese Football Association Super League",
                "season": "2024",
                "round": f"Matchweek {match_info['index']}"
            },
            "venue": {
                "name": venue['name'],
                "city": venue['city'],
                "attendance": attendance
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
                "score": scores[0] if len(scores) > 0 else 0,
                "score_ht": 0,
                "formation": formations[0] if len(formations) > 0 else "",
                "coach": "",
                "captain": "",
                "lineup": home_lineup,
                "substitutes": home_bench,
                "substitutions": []
            },
            "away": {
                "name": match_info['away'],
                "full_name": "",
                "score": scores[1] if len(scores) > 1 else 0,
                "score_ht": 0,
                "formation": formations[1] if len(formations) > 1 else "",
                "coach": "",
                "captain": "",
                "lineup": away_lineup,
                "substitutes": away_bench,
                "substitutions": []
            }
        },
        "events": [],
        "statistics": stats,
        "player_stats": {"home": [], "away": []},
        "metadata": {
            "source": "FBref",
            "url": match_info['url'],
            "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "version": "1.0"
        }
    }

    return match_data

def main():
    """主函数"""

    print("="*60)
    print("最可靠的方案 - 抓取并解析HTML")
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

        # 抓取HTML
        html = scrape_match_html(match['url'])

        if html:
            # 解析数据
            match_data = parse_match_data(html, match)

            if match_data:
                # 保存
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
                print(f"    ❌ 解析失败")
                failed.append(i)
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
