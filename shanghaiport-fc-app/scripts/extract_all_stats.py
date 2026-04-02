#!/usr/bin/env python3
"""
提取完整的比赛统计数据
"""

import subprocess
import json
import re

print("获取完整统计数据...\n")

# 执行JavaScript获取整个team_stats区域的HTML
js_code = """
(function() {
    const teamStatsDiv = document.querySelector('#team_stats');
    if (!teamStatsDiv) return JSON.stringify({error: 'team_stats div not found'});
    
    // 获取HTML和文本
    return JSON.stringify({
        html: teamStatsDiv.innerHTML,
        text: teamStatsDiv.textContent
    });
})()
"""

result = subprocess.run(
    ['openclaw', 'browser', 'evaluate', '--fn', js_code],
    capture_output=True,
    text=True,
    timeout=30
)

# 提取JSON
lines = result.stdout.strip().split('\n')
json_str = None

for line in reversed(lines):
    if 'team_stats' in line or 'html' in line:
        # 找到JSON开始
        json_start = line.find('{')
        if json_start >= 0:
            json_str = line[json_start:]
            try:
                data = json.loads(json_str)
                
                if 'error' in data:
                    print(f"❌ 错误: {data['error']}")
                    break
                
                # 保存
                with open('data/match1_team_stats_html.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print("✅ 统计数据已保存\n")
                
                # 解析文本提取统计
                text = data.get('text', '')
                
                # 提取各项统计
                stats = {}
                
                # Possession
                possession_match = re.search(r'Possession.*?(\d+)%.*?(\d+)%', text, re.DOTALL)
                if possession_match:
                    stats['possession'] = {
                        'home': int(possession_match.group(1)),
                        'away': int(possession_match.group(2))
                    }
                
                # Shots on Target
                shots_match = re.search(r'Shots on Target.*?(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)', text, re.DOTALL)
                if shots_match:
                    stats['shots_on_target'] = {
                        'home': int(shots_match.group(1)),
                        'away': int(shots_match.group(3))
                    }
                    stats['shots'] = {
                        'home': int(shots_match.group(2)),
                        'away': int(shots_match.group(4))
                    }
                
                # Saves
                saves_match = re.search(r'Saves.*?(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)', text, re.DOTALL)
                if saves_match:
                    stats['saves'] = {
                        'home': int(saves_match.group(1)),
                        'away': int(saves_match.group(3))
                    }
                
                # Cards
                cards_match = re.search(r'Cards', text, re.DOTALL)
                if cards_match:
                    # 查找Cards之后的yellow和red
                    cards_section = text[cards_match.end():cards_match.end() + 200]
                    yellow = cards_section.count('yellow_card')
                    red = cards_section.count('red_card')
                    stats['yellow_cards'] = {'home': 1 if yellow >= 1 else 0, 'away': 1 if yellow >= 2 else 0}
                    stats['red_cards'] = {'home': 0, 'away': 0}
                
                # Fouls
                fouls_match = re.search(r'Fouls.*?(\d+).*?(\d+)', text, re.DOTALL)
                if fouls_match:
                    stats['fouls'] = {
                        'home': int(fouls_match.group(1)),
                        'away': int(fouls_match.group(2))
                    }
                
                # Corners
                corners_match = re.search(r'Corners.*?(\d+).*?(\d+)', text, re.DOTALL)
                if corners_match:
                    stats['corners'] = {
                        'home': int(corners_match.group(1)),
                        'away': int(corners_match.group(2))
                    }
                
                # Crosses
                crosses_match = re.search(r'Crosses.*?(\d+).*?(\d+)', text, re.DOTALL)
                if crosses_match:
                    stats['crosses'] = {
                        'home': int(crosses_match.group(1)),
                        'away': int(crosses_match.group(2))
                    }
                
                # Interceptions
                interceptions_match = re.search(r'Interceptions.*?(\d+).*?(\d+)', text, re.DOTALL)
                if interceptions_match:
                    stats['interceptions'] = {
                        'home': int(interceptions_match.group(1)),
                        'away': int(interceptions_match.group(2))
                    }
                
                # Offsides
                offsides_match = re.search(r'Offsides?.*?(\d+).*?(\d+)', text, re.DOTALL)
                if offsides_match:
                    stats['offsides'] = {
                        'home': int(offsides_match.group(1)),
                        'away': int(offsides_match.group(2))
                    }
                
                # 显示提取的统计
                print("📊 提取的统计数据:")
                print("=" * 60)
                for stat, values in stats.items():
                    print(f"{stat:20s}: 主队 {values['home']:3d} - {values['away']:3d} 客队")
                
                # 保存提取的统计
                with open('data/match1_extracted_stats.json', 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                
                print(f"\n✅ 已保存 {len(stats)} 项统计数据")
                
                break
            except Exception as e:
                print(f"解析错误: {e}")
                continue

EOF
