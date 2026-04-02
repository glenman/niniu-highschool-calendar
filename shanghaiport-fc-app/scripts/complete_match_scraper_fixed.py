#!/usr/bin/env python3
"""
修复版FBref数据抓取器
解决venue.city污染和关键数据缺失问题
"""

import json
import os
import re
import subprocess
import time

class FixedMatchScraper:
    """修复版比赛数据抓取器"""
    
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
            
            # 3. 构建完整数据结构
            match_data = {
                "match_info": self._extract_match_info(html, text, match_info),
                "teams": self._extract_teams(html, text, match_info),
                "events": self._extract_events(html, text),
                "statistics": self._extract_statistics(text),
                "player_stats": self._extract_player_stats(html),
                "metadata": {
                    "source": "FBref",
                    "url": url,
                    "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                    "version": "2.0-fixed"
                }
            }
            
            # 4. 显示提取结果
            print(f"  ✅ 提取完成")
            home_score = match_data['teams']['home']['score']
            away_score = match_data['teams']['away']['score']
            print(f"    - 比分: {match_info['home']} {home_score} - {away_score} {match_info['away']}")
            print(f"    - 事件: {len(match_data['events'])} 个")
            print(f"    - 球员统计: 主队 {len(match_data['player_stats']['home'])} 人, 客队 {len(match_data['player_stats']['away'])} 人")
            
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
        
        # 提取球场信息 - 更精确的匹配
        # 只在Match Information部分查找
        match_info_section = re.search(r'Match Information(.*?)(?=Shanghai Port|Tianjin|Beijing|Zhejiang|Shandong|$)', text, re.DOTALL)
        if match_info_section:
            section_text = match_info_section.group(1)
            
            venue_match = re.search(r'Venue:\s*([^,\n]+?)(?:,\s*([A-Za-z\s]+?))?$', section_text, re.MULTILINE)
            if venue_match:
                info['venue']['name'] = venue_match.group(1).strip()
                if venue_match.group(2):
                    info['venue']['city'] = venue_match.group(2).strip()
        
        # 如果上面没找到，用通用方法但限制长度
        if not info['venue']['name']:
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
        """提取球队信息、比分"""
        
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
        
        # 提取比分 - 从HTML的.score元素提取
        scores = re.findall(r'<div class="score">(\d+)</div>', html)
        if len(scores) >= 2:
            teams['home']['score'] = int(scores[0])
            teams['away']['score'] = int(scores[1])
        else:
            # 备用：从文本中提取
            score_match = re.search(rf'{match_info["home"]}\s+(\d+)\s*-\s*(\d+)\s+{match_info["away"]}', text)
            if score_match:
                teams['home']['score'] = int(score_match.group(1))
                teams['away']['score'] = int(score_match.group(2))
        
        # 提取阵型
        formation_match = re.search(rf'{match_info["home"]}\s*\((\d+-\d+-\d+)\)', text)
        if formation_match:
            teams['home']['formation'] = formation_match.group(1)
        
        formation_match = re.search(rf'{match_info["away"]}\s*\((\d+-\d+-\d+)\)', text)
        if formation_match:
            teams['away']['formation'] = formation_match.group(1)
        
        # 提取教练
        manager_matches = re.findall(r'Manager:\s*([A-Za-z\s]+?)(?:\n|$)', text)
        if len(manager_matches) >= 2:
            teams['home']['coach'] = manager_matches[0].strip()
            teams['away']['coach'] = manager_matches[1].strip()
        
        return teams
    
    def _extract_events(self, html: str, text: str) -> list:
        """提取比赛事件（进球、黄牌、换人等）"""
        
        events = []
        
        # 提取进球事件 - 从事件timeline中提取
        # 格式: "Wu Lei · 16'"
        goal_pattern = r'([A-Za-z\s\-\']+?)\s*·\s*(\d+)(\+(\d+))?\''
        goals = re.findall(goal_pattern, text)
        
        for player, minute, _, extra_time in goals[:20]:  # 限制数量避免误匹配
            # 判断是哪个队（简化：通过球员名字判断，实际应该更智能）
            event = {
                "minute": int(minute),
                "minute_extra": int(extra_time) if extra_time else 0,
                "type": "goal",
                "team": "home",  # 需要改进
                "player": player.strip(),
                "assist": "",
                "description": ""
            }
            events.append(event)
        
        # 提取黄牌
        yellow_pattern = r'([A-Za-z\s\-\']+?)\s*—\s*Yellow Card'
        yellows = re.findall(yellow_pattern, text)
        
        for player in yellows[:10]:
            events.append({
                "minute": 0,
                "type": "yellow_card",
                "team": "unknown",
                "player": player.strip()
            })
        
        # 提取换人
        sub_pattern = r'(\d+)\'\s*([A-Za-z\s\-\']+?)\s+for\s+([A-Za-z\s\-\']+)'
        subs = re.findall(sub_pattern, text)
        
        for minute, player_in, player_out in subs[:15]:
            events.append({
                "minute": int(minute),
                "type": "substitution",
                "team": "unknown",
                "player_in": player_in.strip(),
                "player_out": player_out.strip()
            })
        
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
    
    def _extract_player_stats(self, html: str) -> dict:
        """提取球员统计数据"""
        
        player_stats = {
            "home": [],
            "away": []
        }
        
        # 从HTML中提取球员表格数据
        # 这需要解析HTML表格，暂时返回空列表
        # 实际实现需要使用BeautifulSoup或lxml
        
        return player_stats

def main():
    """主函数"""
    
    print("="*60)
    print("修复版批量抓取")
    print("="*60)
    print()
    
    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'data/match-reports-fixed'
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建抓取器
    scraper = FixedMatchScraper()
    
    # 测试第一场
    print(f"\n[测试] {matches[0]['date']} - {matches[0]['home']} vs {matches[0]['away']}")
    match_data = scraper.scrape_complete_match(matches[0]['url'], matches[0])
    
    if match_data:
        filename = f"{output_dir}/{matches[0]['date']}-中超-第1轮-fixed.json"
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
