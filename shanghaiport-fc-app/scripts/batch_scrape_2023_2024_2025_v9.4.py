#!/usr/bin/env python3
"""
上海海港赛事报告完整抓取器 v9.4
修复版：同时从.event和页面文本提取进球信息
"""

import json
import subprocess
import time
import re

# 使用与2025成功脚本相同的EXTRACT_JS（已验证成功）
exec(open('scripts/batch_scrape_2025_v9.3_final.py').read().split("def scrape_match")[0])[0]

def scrape_match(url, match_info):
    try:
        # 打开页面
        result = subprocess.run(['agent-browser', '--cdp', '9222', 'open', url],
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None, None
        time.sleep(10)

        # 提取数据
        result = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', EXTRACT_JS],
                              capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return None, None

        output = result.stdout.strip()
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1].replace('\\"', '"')
        
        extracted = json.loads(output)
        
        # 获取matchweek和比赛时间
        actual_matchweek = extracted.get('matchweek', str(match_info.get('round', 1)))
        
        # 从.event中提取进球
        event_goals = []
        for event in extracted.get('events', []):
            if 'Goal' in event.get('text', ''):
                time_match = re.search(r"(\d+)(?:\+(\d+))?(?:['\u2019´])", event['text'])
                if time_match:
                    links = event.get('players', [])
                    event_goals.append({
                        'minute': int(time_match.group(1)),
                        'minute_extra': int(time_match.group(2)) if time_match.group(2) else 0,
                        'text': event['text'],
                        'players': links
                    })
        
        # 从页面文本提取额外的进球
        body_text = extracted.get('bodyText', '')
        extra_goals = re.findall(
            r"([A-Za-z\s]+)\s*(?:\([P]\))?\s*[·•]\s*(\d+)(?:\+(\d+))?['\u2019´]",
            body_text
        )
        
        for goal_text in extra_goals:
            # 提取球员名
            player_match = re.search(r"^([A-Za-z\s]+)\s*\([A-Za-z\s]+(?:\s*\([P]\))?", goal_text)
            if player_match:
                player = player_match.group(1)
                
                # 提取时间
                time_match = re.search(r"(\d+)(?:\+(\d+))?['\u2019´]", goal_text)
                if time_match:
                    minute = int(time_match.group(1))
                    extra = int(time_match.group(2)) if time_match.group(2) else 0
                    
                    # 判断是否点球
                    is_penalty = '(P)' in goal_text
                    
                    # 检查是否已经在event_goals中
                    exists = any(
                        g['minute'] == minute and g.get('minute_extra', 0) == extra
                        for g in event_goals
                    )
                    
                    if not exists:
                        extra_goals.append({
                            'minute': minute,
                            'minute_extra': extra,
                            'player': player,
                            'is_penalty': is_penalty
                        })
        
        return event_goals, extra_goals, actual_matchweek

    except Exception as e:
        print(f"      ❌ 错误: {e}")
        return None, None

def main(season):
    print("="*70)
    print(f"上海海港{season}赛季完整数据抓取器 v9.4（修复点球提取问题）")
    print("="*70)
    
    # 读取比赛URL列表
    with open(f'data/{season}-match_urls.json', 'r', encoding='utf-8') as f:
        if season == '2023':
            matches = json.load(f)  # 2023是直接数组
        elif season == '2024':
            matches = json.load(f)  # 2024是直接数组
        else:
            url_data = json.load(f)
            matches = url_data.get('match_urls', [])
    
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = f'data/match-reports-{season}'
    os.makedirs(output_dir, exist_ok=True)
    
    # 清空旧文件
    old_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    if old_files:
        print(f"🗑️  清空旧文件: {len(old_files)}个\n")
        for f in old_files:
            os.remove(os.path.join(output_dir, f))
    
    # 批量处理
    success_count = 0
    total_events = 0
    
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match.get('match_report_url', match.get('url', match.get('match_url')
        
        print(f"[{i}/30] {date}")
        
        match_data, actual_round = scrape_match(url, {'date': date, 'round': i, 'season': int(season)})
        
        if match_data and actual_round:
            # 使用实际的matchweek保存文件
            filename = f"{date}-中超-第{actual_round}轮.json"
            filepath = os.path.join(output_dir, filename)
            
            # ... （后续处理events和保存逻辑与之前相同）
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            success_count += 1
        else:
            print(f"      ❌ 失败")
        
        if i < len(matches):
            time.sleep(3)
    
    print(f"\n{'='*70}")
    print("✅ 批量处理完成")
    print(f"{'='*70}")
    print(f"✓ 成功: {success_count} / 30")
    print(f"📁 保存位置: {output_dir}/")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    try:
        main('2023')
        main('2024')
        main('2025')
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
