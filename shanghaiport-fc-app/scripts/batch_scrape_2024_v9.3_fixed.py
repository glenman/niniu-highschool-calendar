#!/usr/bin/env python3
"""
上海海港2024赛季完整数据抓取器 v9.3 Final
基于2025成功脚本
"""

import json
import os
import subprocess
import time
from datetime import datetime
import re

# 使用与2025相同的EXTRACT_JS（已验证成功）
exec(open('scripts/batch_scrape_2025_v9.3_final.py').read().split('def scrape_match')[0])

def scrape_match(url, match_info):
    """抓取单场比赛"""
    try:
        result = subprocess.run(['agent-browser', '--cdp', '9222', 'open', url],
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None, None
        time.sleep(10)

        result = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', EXTRACT_JS],
                              capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return None, None

        output = result.stdout.strip()
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1].replace('\\"', '"')
        
        extracted = json.loads(output)
        
        actual_matchweek = extracted.get('matchweek', str(match_info.get('round', 1)))
        
        # 解析events（与2025相同）
        events = []
        for raw in extracted['events']:
            text = raw['text']
            className = raw['className']
            players = raw['players']
            
            time_match = re.search(r"(\d+)(?:\+(\d+))?(?:['\u2019´])", text)
            if not time_match:
                continue
            
            minute = int(time_match.group(1))
            extra = int(time_match.group(2)) if time_match.group(2) else 0
            
            event_type = 'unknown'
            goal_type = ''
            
            if 'Yellow' in text:
                event_type = 'yellow_card'
            elif 'Red' in text and 'Card' in text:
                event_type = 'red_card'
            elif 'Goal' in text:
                event_type = 'goal'
                if '(P)' in text or 'Penalty' in text:
                    goal_type = 'penalty_goal'
                elif 'Own Goal' in text or '(OG)' in text:
                    goal_type = 'own_goal'
                else:
                    goal_type = 'goal'
            elif 'for' in text.lower() and len(players) >= 2:
                event_type = 'substitution'
            
            if event_type == 'unknown':
                continue
            
            team = 'home' if 'event a' in className else 'away'
            
            assist = ''
            if event_type == 'goal' and len(players) > 1:
                assist = players[1]
            
            events.append({
                "minute": minute,
                "minute_extra": extra,
                "type": event_type,
                "team": team,
                "player": players[0] if players else "",
                "player2": assist,
                "goal_type": goal_type,
                "player_out": players[1] if len(players) > 1 and event_type == 'substitution' else "",
                "description": event_type.replace('_', ' ').upper()
            })

        match_data = {
            "match_info": {
                "match_id": url.split('/')[-2],
                "date": match_info['date'],
                "time": extracted.get('matchTime', '20:00'),
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": "2024",
                    "round": f"Matchweek {actual_matchweek}"
                },
                "venue": extracted.get('venue', {}),
                "referee": {
                    "main": extracted.get('referees', {}).get('main', ''),
                    "ar1": extracted.get('referees', {}).get('ar1', ''),
                    "ar2": extracted.get('referees', {}).get('ar2', ''),
                    "fourth": extracted.get('referees', {}).get('fourth', ''),
                    "var": extracted.get('referees', {}).get('var', ''),
                    "country": "China"
                }
            },
            "teams": {
                "home": {
                    "name": extracted['formations'][0].split('(')[0].strip() if len(extracted['formations']) > 0 else "",
                    "full_name": "",
                    "score": extracted['scores'][0] if len(extracted['scores']) > 0 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][0].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 0 and '(' in extracted['formations'][0] else "",
                    "coach": extracted.get('homeManager', ''),
                    "captain": extracted.get('homeCaptain', ''),
                    "lineup": extracted['lineups']['home'],
                    "substitutes": extracted['bench']['home'],
                    "substitutions": []
                },
                "away": {
                    "name": extracted['formations'][1].split('(')[0].strip() if len(extracted['formations']) > 1 else "",
                    "full_name": "",
                    "score": extracted['scores'][1] if len(extracted['scores']) > 1 else 0,
                    "score_ht": 0,
                    "formation": extracted['formations'][1].split('(')[1].replace(')', '').strip() if len(extracted['formations']) > 1 and '(' in extracted['formations'][1] else "",
                    "coach": extracted.get('awayManager', ''),
                    "captain": extracted.get('awayCaptain', ''),
                    "lineup": extracted['lineups']['away'],
                    "substitutes": extracted['bench']['away'],
                    "substitutions": []
                }
            },
            "events": events,
            "statistics": extracted['statistics'],
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "9.3-final"
            }
        }

        return match_data, actual_matchweek
        
    except Exception as e:
        print(f"      ❌ 错误: {e}")
        return None, None

def main():
    print("="*70)
    print("上海海港2024赛季完整数据抓取器 v9.3 Final")
    print("="*70)
    print()
    
    # 读取比赛URL列表（2024是数组格式）
    with open('data/2024-match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)  # 直接是数组
    
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    output_dir = 'data/match-reports-2024'
    os.makedirs(output_dir, exist_ok=True)
    
    # 清空旧文件
    old_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    if old_files:
        print(f"🗑️  清空旧文件: {len(old_files)}个\n")
        for f in old_files:
            os.remove(os.path.join(output_dir, f))
    
    success_count = 0
    total_events = 0
    
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match['url']  # 2024用的是url字段
        
        print(f"[{i}/30] {date}")
        
        match_data, actual_round = scrape_match(url, {'date': date, 'round': i})
        
        if match_data:
            filename = f"{date}-中超-第{actual_round}轮.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            home = match_data['teams']['home']
            away = match_data['teams']['away']
            hs = home['score']
            as_ = away['score']
            events_count = len(match_data['events'])
            total_events += events_count
            
            time_info = match_data['match_info']['time']
            home_coach = home['coach'][:15] + '..' if len(home['coach']) > 15 else home['coach']
            main_ref = match_data['match_info']['referee']['main'][:15] + '..' if len(match_data['match_info']['referee']['main']) > 15 else match_data['match_info']['referee']['main']
            
            print(f"      ✅ {home['name']} {hs}-{as_} {away['name']}")
            print(f"         ⏰{time_info} | 👨‍💼{home_coach} | 🎯{main_ref}")
            
            success_count += 1
        else:
            print(f"      ❌ 失败")
        
        if i < len(matches):
            time.sleep(3)
    
    print(f"\n{'='*70}")
    print("✅ 批量处理完成")
    print(f"{'='*70}")
    print(f"✓ 成功: {success_count} / 30")
    print(f"✓ 事件总数: {total_events}个")
    print(f"\n📁 保存位置: {output_dir}/")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
