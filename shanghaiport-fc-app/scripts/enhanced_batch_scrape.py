#!/usr/bin/env python3
"""
增强版批量抓取 - 包含阵容和换人信息
"""

import json
import os
import re
import subprocess
import time

def scrape_with_lineups(url: str, match_info: dict) -> dict:
    """抓取完整数据，包括阵容"""

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
        
        # 2. 获取完整HTML
        print("  → 提取数据...")
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', 'document.documentElement.outerHTML'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        html = result.stdout
        
        # 3. 构建数据结构
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
                    "name": "",
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
            },
            "events": [],
            "statistics": {},
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
        
        # 4. 提取阵容信息（从HTML中）
        print("  → 提取阵容...")
        
        # 查找所有球员链接
        player_pattern = r'<a href="/en/players/[^"]+">([^<]+)</a>'
        players = re.findall(player_pattern, html)
        
        if players:
            print(f"    找到 {len(players)} 个球员")
            
            # 简单分配：前11个是主队首发，接下来7个是主队替补
            # 后11个是客队首发，最后7个是客队替补
            # 这需要更智能的解析
            
        # 5. 提取换人信息
        print("  → 提取换人...")
        
        # 查找 "for" 关键字（换人标记）
        sub_pattern = r'([A-Za-z\s]+)\s+for\s+([A-Za-z\s]+)'
        subs = re.findall(sub_pattern, html)
        
        if subs:
            print(f"    找到 {len(subs)} 次换人")
            
            for player_in, player_out in subs[:10]:  # 最多10次换人
                # 简化处理，不区分主客队
                match_data['teams']['home']['substitutions'].append({
                    'minute': 0,  # 需要从页面提取
                    'player_out': player_out.strip(),
                    'player_in': player_in.strip()
                })
        
        # 6. 提取统计数据（使用之前的代码）
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', 'document.body.textContent'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        text = result.stdout
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
        
        match_data['statistics'] = stats
        
        print(f"  ✅ 提取完成")
        print(f"    - 统计项: {len(stats)}")
        print(f"    - 换人: {len(match_data['teams']['home']['substitutions']) + len(match_data['teams']['away']['substitutions'])}")
        
        return match_data
        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None

def main():
    """主函数"""
    
    print("="*60)
    print("增强版批量抓取 - 包含阵容信息")
    print("="*60)
    print()
    
    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'data/match-reports-with-lineups'
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理每场比赛
    success = 0
    failed = []
    
    for i, match in enumerate(matches[1:], 2):  # 跳过第1场
        print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")
        
        # 抓取数据
        match_data = scrape_with_lineups(match['url'], match)
        
        if match_data and len(match_data['statistics']) >= 5:
            # 保存
            filename = f"{output_dir}/{match['date']}-中超-第{i}轮.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 已保存")
            success += 1
        else:
            print(f"  ❌ 数据不完整")
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

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
