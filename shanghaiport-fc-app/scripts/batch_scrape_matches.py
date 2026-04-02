#!/usr/bin/env python3
"""
批量抓取FBref比赛数据
"""

import json
import subprocess
import time
import os
from datetime import datetime

def scrape_match_data(url, match_index):
    """使用OpenClaw Browser抓取单场比赛数据"""

    print(f"\n{'='*60}")
    print(f"处理第 {match_index} 场比赛...")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        # 1. 打开页面
        print("  → 打开页面...")
        result = subprocess.run(
            ["openclaw", "browser", "open", url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "opened:" not in result.stdout:
            print(f"  ❌ 打开页面失败")
            return None

        tab_id = result.stdout.split("id: ")[-1].strip()
        print(f"  ✅ 页面已打开 (Tab ID: {tab_id[:20]}...)")

        # 2. 等待页面加载
        time.sleep(5)

        # 3. 抓取数据
        print("  → 抓取数据...")

        js_code = """
        (function() {
            const data = {
                title: document.title,
                scorebox: document.querySelector('.scorebox')?.innerText || '',
                stats: document.querySelector('#team_stats')?.innerText || '',
                events: document.querySelector('#events')?.innerText || ''
            };
            return JSON.stringify(data);
        })()
        """

        result = subprocess.run(
            ["openclaw", "browser", "evaluate", "--fn", js_code],
            capture_output=True,
            text=True,
            timeout=15
        )

        # 提取JSON数据
        output_lines = result.stdout.strip().split('\n')
        json_str = output_lines[-1] if output_lines else ""

        if not json_str or json_str == "{}":
            print(f"  ❌ 数据抓取失败")
            return None

        print(f"  ✅ 数据抓取成功")
        return json.loads(json_str)

    except subprocess.TimeoutExpired:
        print(f"  ⏰ 超时")
        return None
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None

def parse_match_data(raw_data, match_info):
    """解析原始数据并转换为标准格式"""

    try:
        # 解析比分
        scorebox = raw_data.get('scorebox', '')

        # 提取球队名称和比分
        lines = scorebox.split('\n')
        home_team = lines[0] if len(lines) > 0 else match_info['home']
        home_score = int(lines[1]) if len(lines) > 1 and lines[1].isdigit() else 0

        # 找到客队信息
        away_start = scorebox.find(match_info['away'])
        if away_start != -1:
            away_section = scorebox[away_start:].split('\n')
            away_team = away_section[0] if len(away_section) > 0 else match_info['away']
            away_score = int(away_section[1]) if len(away_section) > 1 and away_section[1].isdigit() else 0
        else:
            away_team = match_info['away']
            away_score = 0

        # 解析统计数据
        stats_text = raw_data.get('stats', '')
        stats = {}

        # 提取控球率
        if 'Possession' in stats_text:
            parts = stats_text.split('Possession')[1].split('\n')
            possession_values = [p.strip() for p in parts if '%' in p]
            if len(possession_values) >= 2:
                stats['possession'] = {
                    'home': int(possession_values[0].replace('%', '')),
                    'away': int(possession_values[1].replace('%', ''))
                }

        # 提取射门
        if 'Shots on Target' in stats_text:
            parts = stats_text.split('Shots on Target')[1].split('—')
            if len(parts) >= 2:
                home_shots = parts[0].strip().split()[-1]
                away_shots = parts[1].strip().split()[0]
                stats['shots_on_target'] = {
                    'home': int(home_shots) if home_shots.isdigit() else 0,
                    'away': int(away_shots) if away_shots.isdigit() else 0
                }

        # 解析事件（简化版）
        events_text = raw_data.get('events', '')
        events = []

        # 查找进球事件
        for line in events_text.split('\n'):
            if '·' in line and ('Goal' in line or '进球' in line or "'" in line):
                parts = line.split('·')
                if len(parts) >= 2:
                    minute_part = parts[0].strip()
                    player_part = parts[1].strip()

                    # 提取分钟数
                    minute_str = ''.join(filter(str.isdigit, minute_part.split()[0]))
                    if minute_str:
                        minute = int(minute_str)

                        # 判断是主队还是客队
                        team = 'home' if home_team in line or any(home_player in line for home_player in ['Wu Lei', 'Oscar', 'Wang']) else 'away'

                        events.append({
                            'minute': minute,
                            'type': 'goal',
                            'team': team,
                            'player': player_part,
                            'description': ''
                        })

        # 构建标准数据格式
        match_data = {
            "match_info": {
                "match_id": match_info['url'].split('/')[-2] if '/' in match_info['url'] else '',
                "date": match_info['date'],
                "time": "",  # 需要从页面提取
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": "2024",
                    "round": f"Matchweek {match_info['index']}"
                },
                "venue": {
                    "name": "",  # 需要从页面提取
                    "city": "",
                    "attendance": 0
                },
                "referee": {
                    "name": "",
                    "country": "China"
                }
            },
            "teams": {
                "home": {
                    "name": home_team,
                    "full_name": "",
                    "score": home_score,
                    "score_ht": 0,
                    "formation": "",
                    "coach": "",
                    "lineup": [],
                    "substitutes": [],
                    "substitutions": []
                },
                "away": {
                    "name": away_team,
                    "full_name": "",
                    "score": away_score,
                    "score_ht": 0,
                    "formation": "",
                    "coach": "",
                    "lineup": [],
                    "substitutes": [],
                    "substitutions": []
                }
            },
            "events": events,
            "statistics": stats,
            "player_stats": {
                "home": [],
                "away": []
            },
            "metadata": {
                "source": "FBref",
                "url": match_info['url'],
                "scraped_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

        return match_data

    except Exception as e:
        print(f"  ❌ 解析错误: {e}")
        return None

def main():
    """主函数"""

    # 读取比赛URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)

    print(f"📋 共有 {len(matches)} 场比赛需要处理")
    print(f"{'='*60}\n")

    # 创建输出目录
    output_dir = "data/match-reports"
    os.makedirs(output_dir, exist_ok=True)

    # 处理每场比赛
    success_count = 0
    failed_matches = []

    for i, match in enumerate(matches, 1):
        # 跳过已处理的第1场比赛
        if i == 1:
            print(f"⏭️  跳过第 {i} 场（已处理）")
            continue

        # 抓取数据
        raw_data = scrape_match_data(match['url'], i)

        if raw_data:
            # 解析数据
            match_data = parse_match_data(raw_data, match)

            if match_data:
                # 生成文件名：比赛日期-中超-第X轮.json
                filename = f"{match['date']}-中超-第{i}轮.json"
                filepath = os.path.join(output_dir, filename)

                # 保存JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(match_data, f, ensure_ascii=False, indent=2)

                print(f"  ✅ 已保存: {filename}")
                success_count += 1

                # 避免请求过快
                time.sleep(3)
            else:
                failed_matches.append(i)
        else:
            failed_matches.append(i)

    # 总结
    print(f"\n{'='*60}")
    print(f"✅ 处理完成")
    print(f"{'='*60}")
    print(f"成功: {success_count} / {len(matches) - 1}")
    print(f"失败: {len(failed_matches)}")

    if failed_matches:
        print(f"\n失败的比赛:")
        for idx in failed_matches:
            print(f"  - 第 {idx} 轮")

    print(f"\n📁 数据保存位置: {output_dir}/")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
