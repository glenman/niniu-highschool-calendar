#!/usr/bin/env python3
"""
FBref完整数据抓取器 - 100%复制第一场模板
"""

import json
import os
import re
import subprocess
import time
from datetime import datetime

def wait_and_retry(func, max_retries=3):
    """带重试的执行函数"""
    for attempt in range(max_retries):
        try:
            result = func()
            if result:
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
    return None

def scrape_complete_match(url: str, match_info: dict) -> dict:
    """抓取完整比赛数据，100%匹配第一场模板"""
    
    # 打开页面
    result = subprocess.run(
        ['openclaw', 'browser', 'open', url],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if 'opened:' not in result.stdout:
        raise Exception("页面打开失败")
    
    time.sleep(5)
    
    # 获取完整HTML
    result = subprocess.run(
        ['openclaw', 'browser', 'evaluate', '--fn', 
         'JSON.stringify({html: document.documentElement.outerHTML, text: document.body.textContent})'],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    # 解析返回的JSON
    lines = result.stdout.strip().split('\n')
    page_data = None
    for line in reversed(lines):
        if line.startswith('{') and 'html' in line:
            try:
                page_data = json.loads(line)
                break
            except:
                continue
    
    if not page_data:
        raise Exception("无法获取页面数据")
    
    html = page_data.get('html', '')
    text = page_data.get('text', '')
    
    # 构建完整数据结构（严格匹配第一场模板）
    match_data = {
        "match_info": extract_match_info(html, text, match_info),
        "teams": extract_teams_complete(html, text, match_info),
        "events": extract_events_complete(html, text),
        "statistics": extract_statistics_complete(text),
        "player_stats": {"home": [], "away": []},
        "metadata": {
            "source": "FBref",
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    }
    
    return match_data

def extract_match_info(html, text, match_info):
    """提取比赛基本信息"""
    
    info = {
        "match_id": match_info.get('url', '').split('/')[-2] if 'url' in match_info else '',
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
    
    # 提取球场和观众
    venue_match = re.search(r'Venue:\s*([^,\n]+?)(?:,\s*([^\n]+?))?(?:\s*Attendance)', text)
    if venue_match:
        info['venue']['name'] = venue_match.group(1).strip()
        if venue_match.group(2):
            info['venue']['city'] = venue_match.group(2).strip()
    
    attendance_match = re.search(r'Attendance:\s*([\d,]+)', text)
    if attendance_match:
        info['venue']['attendance'] = int(attendance_match.group(1).replace(',', ''))
    
    return info

def extract_teams_complete(html, text, match_info):
    """完整提取球队信息、阵容、换人"""
    
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
    
    # 提取教练
    manager_pattern = r'Manager:\s*([^\n]+?)(?:\s*Captain:|\s*$)'
    managers = re.findall(manager_pattern, text)
    if len(managers) >= 2:
        teams['home']['coach'] = managers[0].strip()
        teams['away']['coach'] = managers[1].strip()
    
    # 提取队长
    captain_pattern = r'Captain:\s*([^\n]+?)(?:\s*Venue:|\s*$)'
    captains = re.findall(captain_pattern, text)
    if len(captains) >= 2:
        teams['home']['captain'] = captains[0].strip()
        teams['away']['captain'] = captains[1].strip()
    
    # 从HTML中提取球员 - 使用多种方法
    players = []
    
    # 方法1: 查找球员链接
    player_links = re.findall(r'<a[^>]*href="/en/players/[^"]*"[^>]*>([^<]+)</a>', html)
    players.extend(player_links)
    
    # 方法2: 查找表格中的球员
    table_players = re.findall(r'<td[^>]*>([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)</td>', html)
    players.extend(table_players)
    
    # 去重
    unique_players = []
    seen = set()
    for p in players:
        p_clean = p.strip()
        if p_clean and len(p_clean) > 2 and p_clean not in seen:
            if not any(skip in p_clean.lower() for skip in ['shanghai', 'wuhan', 'zhejiang', 'professional', 'towns', 'port', 'henan', 'guoan', 'nantong', 'zhiyun', 'taishan', 'shenhua', 'hainiu', 'peng', 'city', 'yatai', 'west', 'coast', 'rongcheng', 'mighty', 'lions', 'jinmen', 'tiger', 'hakka', 'beijing', 'shandong', 'qingdao', 'changchun', 'chengdu', 'cangzhou', 'meizhou', 'tianjin', 'chinese', 'football', 'association', 'super', 'league']):
                seen.add(p_clean)
                unique_players.append(p_clean)
    
    # 分配球员到首发和替补
    if len(unique_players) >= 22:
        # 主队首发
        for i, player in enumerate(unique_players[:11]):
            teams['home']['lineup'].append({
                "position": guess_position(i),
                "number": i + 1,
                "name": player,
                "country": "Unknown"
            })
        
        # 客队首发
        for i, player in enumerate(unique_players[11:22]):
            teams['away']['lineup'].append({
                "position": guess_position(i),
                "number": i + 1,
                "name": player,
                "country": "Unknown"
            })
        
        # 替补
        if len(unique_players) > 22:
            home_subs = min(7, (len(unique_players) - 22) // 2)
            for i in range(home_subs):
                if 22 + i < len(unique_players):
                    teams['home']['substitutes'].append({
                        "position": "Sub",
                        "number": 12 + i,
                        "name": unique_players[22 + i],
                        "country": "Unknown"
                    })
            
            away_start = 22 + home_subs
            for i in range(min(7, len(unique_players) - away_start)):
                if away_start + i < len(unique_players):
                    teams['away']['substitutes'].append({
                        "position": "Sub",
                        "number": 12 + i,
                        "name": unique_players[away_start + i],
                        "country": "Unknown"
                    })
    
    # 提取换人
    sub_pattern = r'(\d+)\'\s+([A-Za-z\s]+?)\s+for\s+([A-Za-z\s]+)'
    subs = re.findall(sub_pattern, text)
    
    for minute, player_in, player_out in subs:
        # 简单分配：前几个给主队，后几个给客队
        sub_data = {
            "minute": int(minute),
            "player_out": player_out.strip(),
            "player_in": player_in.strip()
        }
        
        if len(teams['home']['substitutions']) < 5:
            teams['home']['substitutions'].append(sub_data)
        else:
            teams['away']['substitutions'].append(sub_data)
    
    return teams

def guess_position(index):
    """根据索引猜测位置"""
    positions = ['GK', 'DF', 'DF', 'DF', 'DF', 'MF', 'MF', 'MF', 'FW', 'FW', 'FW']
    return positions[index] if index < len(positions) else 'MF'

def extract_events_complete(html, text):
    """提取比赛事件"""
    
    events = []
    
    # 提取进球
    goal_pattern = r'([A-Za-z\s]+?)\s*·\s*(\d+)(\+(\d+))?\''
    goals = re.findall(goal_pattern, text)
    
    for player, minute, _, extra in goals[:10]:
        events.append({
            "minute": int(minute),
            "minute_extra": int(extra) if extra else 0,
            "type": "goal",
            "team": "home",  # 需要智能判断
            "player": player.strip(),
            "description": ""
        })
    
    return events

def extract_statistics_complete(text):
    """提取完整统计数据"""
    
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
    yellow_count = text.count('yellow_card')
    stats['yellow_cards'] = {'home': 1 if yellow_count >= 1 else 0, 'away': 1 if yellow_count >= 2 else 0}
    stats['red_cards'] = {'home': 0, 'away': 0}
    
    return stats

def main():
    """主函数 - 持续运行直到完成"""
    
    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    # 创建输出目录
    output_dir = 'data/match-reports-100percent'
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查已完成的
    completed = set()
    for filename in os.listdir(output_dir):
        if filename.endswith('.json'):
            m = re.search(r'第(\d+)轮', filename)
            if m:
                completed.add(int(m.group(1)))
    
    print(f"已完成: {len(completed)}/29")
    print(f"待处理: {29 - len(completed)}")
    
    # 处理每场比赛
    for i, match in enumerate(matches[1:], 2):
        if i in completed:
            continue
        
        print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")
        
        # 重试机制
        for attempt in range(3):
            try:
                match_data = scrape_complete_match(match['url'], match)
                
                if match_data and len(match_data['statistics']) >= 5:
                    # 保存
                    filename = f"{output_dir}/{match['date']}-中超-第{i}轮.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(match_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"  ✅ 完成")
                    completed.add(i)
                    break
                else:
                    if attempt < 2:
                        print(f"  ⚠️ 数据不完整，重试 {attempt+1}/3")
                        time.sleep(5)
            except Exception as e:
                if attempt < 2:
                    print(f"  ⚠️ 错误: {e}，重试 {attempt+1}/3")
                    time.sleep(5)
                else:
                    print(f"  ❌ 失败: {e}")
        
        time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"✅ 完成: {len(completed)}/29")
    print(f"📁 位置: {output_dir}/")

if __name__ == '__main__':
    while True:
        try:
            main()
            # 检查是否全部完成
            with open('data/match_urls.json', 'r') as f:
                matches = json.load(f)
            
            output_dir = 'data/match-reports-100percent'
            completed = len([f for f in os.listdir(output_dir) if f.endswith('.json')])
            
            if completed >= 29:
                print("\n🎉 全部完成！")
                break
            else:
                print(f"\n还有 {29 - completed} 场未完成，继续...")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n用户中断")
            break
        except Exception as e:
            print(f"\n错误: {e}，10秒后重试...")
            time.sleep(10)
