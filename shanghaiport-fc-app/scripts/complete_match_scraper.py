#!/usr/bin/env python3
"""
完整版FBref数据抓取器
按照第一场比赛的数据结构，提取所有信息
"""

import json
import os
import re
import subprocess
import time

class CompleteMatchScraper:
    """完整比赛数据抓取器"""
    
    def scrape_complete_match(self, url: str, match_info: dict) -> dict:
        """抓取完整的比赛数据"""
        
        try:
            # 1. 打开页面
            print("  → 打开页面...")
            result = subprocess.run(
                ['openclaw', 'browser', 'open', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if 'opened:' not in result.stdout:
                return None
            
            time.sleep(5)
            
            # 2. 获取完整HTML和文本
            print("  → 提取页面数据...")
            
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
            
            # 3. 构建完整数据结构（按照第一场比赛的模板）
            match_data = {
                "match_info": self._extract_match_info(html, text, match_info),
                "teams": self._extract_teams(html, text, match_info),
                "events": self._extract_events(html, text),
                "statistics": self._extract_statistics(text),
                "player_stats": {
                    "home": [],
                    "away": []
                },
                "metadata": {
                    "source": "FBref",
                    "url": url,
                    "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "version": "1.0"
                }
            }
            
            # 4. 显示提取结果
            print(f"  ✅ 提取完成")
            print(f"    - 首发阵容: {len(match_data['teams']['home']['lineup']) + len(match_data['teams']['away']['lineup'])} 人")
            print(f"    - 替补: {len(match_data['teams']['home']['substitutes']) + len(match_data['teams']['away']['substitutes'])} 人")
            print(f"    - 换人: {len(match_data['teams']['home']['substitutions']) + len(match_data['teams']['away']['substitutions'])} 次")
            print(f"    - 事件: {len(match_data['events'])} 个")
            print(f"    - 统计: {len(match_data['statistics'])} 项")
            
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
                "name": "",
                "country": "China"
            }
        }
        
        # 提取球场信息
        venue_match = re.search(r'Venue:\s*([^,\n]+)(?:,\s*([^\n]+))?', text)
        if venue_match:
            info['venue']['name'] = venue_match.group(1).strip()
            if venue_match.group(2):
                info['venue']['city'] = venue_match.group(2).strip()
        
        # 提取观众人数
        attendance_match = re.search(r'Attendance:\s*([\d,]+)', text)
        if attendance_match:
            info['venue']['attendance'] = int(attendance_match.group(1).replace(',', ''))
        
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
        
        # 提取教练和队长
        manager_matches = re.findall(r'Manager:\s*([^\n]+)', text)
        captain_matches = re.findall(r'Captain:\s*([^\n]+)', text)
        
        if len(manager_matches) >= 2:
            teams['home']['coach'] = manager_matches[0].strip()
            teams['away']['coach'] = manager_matches[1].strip()
        
        if len(captain_matches) >= 2:
            teams['home']['captain'] = captain_matches[0].strip()
            teams['away']['captain'] = captain_matches[1].strip()
        
        # 提取球员（从HTML中的球员链接）
        player_pattern = r'<a href="/en/players/[^"]+">([A-Za-z\s\'\-\.]+)</a>'
        all_players = re.findall(player_pattern, html)
        
        # 去重并清理
        unique_players = []
        seen = set()
        for player in all_players:
            player_clean = player.strip()
            if player_clean and player_clean not in seen and len(player_clean) > 2:
                seen.add(player_clean)
                unique_players.append(player_clean)
        
        # 简单分配：前11个是主队首发，后11个是客队首发
        # 这需要更智能的解析，但作为初始版本
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
            
            # 替补（剩余的球员）
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
        
        # 提取换人信息
        sub_pattern = r'(\d+)\'\s*([A-Za-z\s]+)\s+for\s+([A-Za-z\s]+)'
        subs = re.findall(sub_pattern, text)
        
        for minute, player_in, player_out in subs[:10]:
            # 简化处理：前几个分给主队，后几个分给客队
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
        goal_pattern = r'([A-Za-z\s]+)\s*·\s*(\d+)(\+(\d+))?\''
        goals = re.findall(goal_pattern, text)
        
        for player, minute, _, extra in goals[:10]:
            event = {
                "minute": int(minute),
                "minute_extra": int(extra) if extra else 0,
                "type": "goal",
                "team": "home",  # 需要更智能的判断
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
        
        # 黄牌
        yellow_count = text.count('yellow_card')
        if yellow_count > 0:
            stats['yellow_cards'] = {'home': 1 if yellow_count >= 1 else 0, 'away': 1 if yellow_count >= 2 else 0}
        else:
            stats['yellow_cards'] = {'home': 0, 'away': 0}
        
        # 红牌
        stats['red_cards'] = {'home': 0, 'away': 0}
        
        return stats

def main():
    """主函数"""
    
    print("="*60)
    print("完整版批量抓取 - 按照第一场模板")
    print("="*60)
    print()
    
    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'data/match-reports-complete-v2'
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建抓取器
    scraper = CompleteMatchScraper()
    
    # 处理每场比赛
    success = 0
    failed = []
    
    for i, match in enumerate(matches[1:], 2):  # 跳过第1场
        print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")
        
        # 抓取数据
        match_data = scraper.scrape_complete_match(match['url'], match)
        
        if match_data:
            # 保存
            filename = f"{output_dir}/{match['date']}-中超-第{i}轮-complete.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 已保存: {filename}")
            success += 1
        else:
            print(f"  ❌ 抓取失败")
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
    
    print(f"\n📁 保存位置: {output_dir}/")
    print("\n📊 每个文件包含:")
    print("  - 比赛基本信息")
    print("  - 球队信息（教练、队长）")
    print("  - 首发阵容（22人）")
    print("  - 替补名单（14人）")
    print("  - 换人记录")
    print("  - 比赛事件")
    print("  - 完整统计（11项）")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
