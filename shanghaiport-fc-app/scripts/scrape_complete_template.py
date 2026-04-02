#!/usr/bin/env python3
"""
按照模板格式完整抓取比赛数据
参考: templates/2024-03-01-中超-第1轮-complete.json
"""

import json
import os
import re
import subprocess
import time

class CompleteMatchScraper:
    """完整比赛数据抓取器"""

    def scrape_match(self, url: str, match_info: dict) -> dict:
        """抓取完整的比赛数据"""

        try:
            print(f"  → 打开页面...")
            result = subprocess.run(
                ['openclaw', 'browser', 'open', url],
                capture_output=True,
                text=True,
                timeout=30
            )

            if 'opened:' not in result.stdout:
                return None

            time.sleep(5)

            print(f"  → 提取页面数据...")
            # 获取HTML
            result_html = subprocess.run(
                ['openclaw', 'browser', 'evaluate', '--fn', 'document.documentElement.outerHTML'],
                capture_output=True,
                text=True,
                timeout=15
            )
            html = result_html.stdout

            # 获取文本
            result_text = subprocess.run(
                ['openclaw', 'browser', 'evaluate', '--fn', 'document.body.textContent'],
                capture_output=True,
                text=True,
                timeout=15
            )
            text = result_text.stdout

            # 构建完整数据
            match_data = {
                "match_info": self._extract_match_info(html, text, match_info),
                "teams": self._extract_teams(html, text, match_info),
                "events": self._extract_events(html, text),
                "statistics": self._extract_statistics(text),
                "player_stats": {"home": [], "away": []},
                "metadata": {
                    "source": "FBref",
                    "url": url,
                    "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "version": "1.0"
                }
            }

            print(f"  ✅ 提取完成")
            print(f"    - 首发阵容: 主队 {len(match_data['teams']['home']['lineup'])} 人, 客队 {len(match_data['teams']['away']['lineup'])} 人")
            print(f"    - 替补: 主队 {len(match_data['teams']['home']['substitutes'])} 人, 客队 {len(match_data['teams']['away']['substitutes'])} 人")
            print(f"    - 换人: 主队 {len(match_data['teams']['home']['substitutions'])} 次, 客队 {len(match_data['teams']['away']['substitutions'])} 次")
            print(f"    - 事件: {len(match_data['events'])} 个")
            print(f"    - 比分: {match_data['teams']['home']['name']} {match_data['teams']['home']['score']} - {match_data['teams']['away']['score']} {match_data['teams']['away']['name']}")

            return match_data

        except Exception as e:
            print(f"  ❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_match_info(self, html: str, text: str, match_info: dict) -> dict:
        """提取比赛基本信息"""

        info = {
            "match_id": match_info['url'].split('/')[-2] if 'url' in match_info else '',
            "date": match_info['date'],
            "time": "20:00",
            "competition": {
                "name": "Chinese Football Association Super League",
                "season": "2024",
                "round": f"Matchweek {match_info['index']}"
            },
            "venue": {
                "name": "",
                "city": "",
                "attendance": 0
            },
            "referee": {
                "name": "待补充",
                "country": "China"
            }
        }

        # 提取球场信息
        venue_match = re.search(r'Venue:\s*([A-Za-z\s\.]+?)(?:,\s*([A-Za-z\s]+?))?(?:\s*Officials|\s*$)', text)
        if venue_match:
            info['venue']['name'] = venue_match.group(1).strip()
            if venue_match.group(2) and len(venue_match.group(2)) < 50:
                info['venue']['city'] = venue_match.group(2).strip()

        # 提取观众人数
        attendance_match = re.search(r'Attendance:\s*([\d,]+)', text)
        if attendance_match:
            info['venue']['attendance'] = int(attendance_match.group(1).replace(',', ''))

        # 提取裁判
        referee_match = re.search(r'Referee:\s*([A-Za-z\s]+?)(?:\s*·|\s*$)', text)
        if referee_match:
            info['referee']['name'] = referee_match.group(1).strip()

        return info

    def _extract_teams(self, html: str, text: str, match_info: dict) -> dict:
        """提取球队信息、阵容、换人"""

        teams = {
            "home": {
                "name": match_info['home'],
                "full_name": "",
                "score": 0,
                "score_ht": 0,
                "formation": "",
                "coach": "",
                "captain": "",
                "lineup": [],
                "substitutes": [],
                "substitutions": []
            },
            "away": {
                "name": match_info['away'],
                "full_name": "",
                "score": 0,
                "score_ht": 0,
                "formation": "",
                "coach": "",
                "captain": "",
                "lineup": [],
                "substitutes": [],
                "substitutions": []
            }
        }

        # 提取比分
        scores = re.findall(r'<div class="score">(\d+)</div>', html)
        if len(scores) >= 2:
            teams['home']['score'] = int(scores[0])
            teams['away']['score'] = int(scores[1])

        # 提取阵型
        formation_match = re.search(rf'{match_info["home"]}\s*\((\d+-\d+-\d+)\)', text)
        if formation_match:
            teams['home']['formation'] = formation_match.group(1)

        formation_match = re.search(rf'{match_info["away"]}\s*\((\d+-\d+-\d+)\)', text)
        if formation_match:
            teams['away']['formation'] = formation_match.group(1)

        # 提取球员 - 从HTML表格中提取
        # 查找所有球员链接
        player_pattern = r'<a href="/en/players/[^"]+">([A-Za-z\s\'\-\.]+)</a>'
        all_players = re.findall(player_pattern, html)

        # 去重
        unique_players = []
        seen = set()
        for player in all_players:
            player_clean = player.strip()
            if player_clean and player_clean not in seen and len(player_clean) > 2:
                seen.add(player_clean)
                unique_players.append(player_clean)

        # 简单分配（需要改进）
        if len(unique_players) >= 22:
            # 主队首发
            for i, player in enumerate(unique_players[:11]):
                teams['home']['lineup'].append({
                    "position": self._guess_position(i),
                    "number": i + 1,
                    "name": player,
                    "country": "Unknown"
                })

            # 客队首发
            for i, player in enumerate(unique_players[11:22]):
                teams['away']['lineup'].append({
                    "position": self._guess_position(i),
                    "number": i + 1,
                    "name": player,
                    "country": "Unknown"
                })

            # 替补
            if len(unique_players) > 22:
                for i, player in enumerate(unique_players[22:29]):
                    teams['home']['substitutes'].append({
                        "position": "Sub",
                        "number": 12 + i,
                        "name": player,
                        "country": "Unknown"
                    })

                for i, player in enumerate(unique_players[29:36]):
                    teams['away']['substitutes'].append({
                        "position": "Sub",
                        "number": 12 + i,
                        "name": player,
                        "country": "Unknown"
                    })

        # 提取换人
        sub_pattern = r'(\d+)\'\s*([A-Za-z\s]+?)\s+for\s+([A-Za-z\s]+)'
        subs = re.findall(sub_pattern, text)

        for minute, player_in, player_out in subs[:10]:
            if len(teams['home']['substitutions']) < 5:
                teams['home']['substitutions'].append({
                    "minute": int(minute),
                    "player_out": player_out.strip(),
                    "player_in": player_in.strip()
                })
            else:
                teams['away']['substitutions'].append({
                    "minute": int(minute),
                    "player_out": player_out.strip(),
                    "player_in": player_in.strip()
                })

        return teams

    def _guess_position(self, index: int) -> str:
        """根据索引猜测位置"""
        positions = ['GK', 'DF', 'DF', 'DF', 'DF', 'MF', 'MF', 'MF', 'FW', 'FW', 'FW']
        return positions[index] if index < len(positions) else 'MF'

    def _extract_events(self, html: str, text: str) -> list:
        """提取比赛事件（进球等）"""

        events = []

        # 提取进球
        goal_pattern = r'([A-Za-z\s\-\']+?)\s*·\s*(\d+)(\+(\d+))?\''
        goals = re.findall(goal_pattern, text)

        for player, minute, _, extra_time in goals[:20]:
            event = {
                "minute": int(minute),
                "minute_extra": int(extra_time) if extra_time else 0,
                "type": "goal",
                "team": "home",  # 需要改进
                "player": player.strip(),
                "description": ""
            }
            events.append(event)

        return events

    def _extract_statistics(self, text: str) -> dict:
        """提取统计数据"""

        stats = {}

        # 控球率
        possession_match = re.search(r'Possession.*?(\d+)%.*?(\d+)%', text, re.DOTALL)
        if possession_match:
            stats['possession'] = {'home': int(possession_match.group(1)), 'away': int(possession_match.group(2))}

        # 射门
        shots_match = re.search(r'Shots on Target.*?(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)', text, re.DOTALL)
        if shots_match:
            stats['shots_on_target'] = {'home': int(shots_match.group(1)), 'away': int(shots_match.group(3))}
            stats['shots'] = {'home': int(shots_match.group(2)), 'away': int(shots_match.group(4))}

        # 扑救
        saves_match = re.search(r'Saves.*?(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)', text, re.DOTALL)
        if saves_match:
            stats['saves'] = {'home': int(saves_match.group(1)), 'away': int(saves_match.group(3))}

        # 犯规
        fouls_match = re.search(r'(\d+)Fouls(\d+)', text)
        if fouls_match:
            stats['fouls'] = {'home': int(fouls_match.group(1)), 'away': int(fouls_match.group(2))}

        # 角球
        corners_match = re.search(r'(\d+)Corners(\d+)', text)
        if corners_match:
            stats['corners'] = {'home': int(corners_match.group(1)), 'away': int(corners_match.group(2))}

        # 传中
        crosses_match = re.search(r'(\d+)Crosses(\d+)', text)
        if crosses_match:
            stats['crosses'] = {'home': int(crosses_match.group(1)), 'away': int(crosses_match.group(2))}

        # 拦截
        interceptions_match = re.search(r'(\d+)Interceptions(\d+)', text)
        if interceptions_match:
            stats['interceptions'] = {'home': int(interceptions_match.group(1)), 'away': int(interceptions_match.group(2))}

        # 越位
        offsides_match = re.search(r'(\d+)Offsides?(\d+)', text)
        if offsides_match:
            stats['offsides'] = {'home': int(offsides_match.group(1)), 'away': int(offsides_match.group(2))}

        # 黄牌和红牌
        stats['yellow_cards'] = {'home': 0, 'away': 0}
        stats['red_cards'] = {'home': 0, 'away': 0}

        return stats

def main():
    """主函数"""

    print("="*60)
    print("按照模板格式完整抓取比赛数据")
    print("="*60)
    print()

    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)

    print(f"📋 共 {len(matches)} 场比赛\n")

    # 创建输出目录
    output_dir = 'data/match-reports-template-format'
    os.makedirs(output_dir, exist_ok=True)

    # 创建抓取器
    scraper = CompleteMatchScraper()

    # 测试第2轮
    print(f"[测试] 第2轮: {matches[1]['date']} - {matches[1]['home']} vs {matches[1]['away']}")
    match_data = scraper.scrape_match(matches[1]['url'], matches[1])

    if match_data:
        filename = f"{output_dir}/{matches[1]['date']}-中超-第2轮-complete.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(match_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 测试成功！保存到: {filename}")
        print("\n请检查数据是否正确，然后可以批量处理所有比赛")
    else:
        print("\n❌ 测试失败")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
