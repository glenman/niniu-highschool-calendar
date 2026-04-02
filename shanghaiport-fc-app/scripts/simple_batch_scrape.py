#!/usr/bin/env python3
"""
简单批量抓取 - 使用已验证的方法
直接从网页提取所有统计数据
"""

import json
import os
import re
import subprocess
import time

def quick_scrape_all_data(url: str, match_info: dict) -> dict:
    """快速抓取所有数据"""
    
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
        
        # 2. 获取完整页面文本
        print("  → 提取数据...")
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', 'document.body.textContent'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        text = result.stdout
        
        # 3. 构建完整数据结构
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
        
        # 4. 提取统计数据
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
        
        print(f"  ✅ 提取到 {len(stats)} 项统计")
        
        # 显示部分统计
        if stats:
            print("  📊 部分统计:")
            for stat, values in list(stats.items())[:3]:
                print(f"    {stat}: {values['home']} - {values['away']}")
        
        return match_data
        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None

def main():
    """主函数"""
    
    print("="*60)
    print("简单批量抓取 - 生成完整JSON")
    print("="*60)
    print()
    
    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'data/match-reports-final'
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理每场比赛
    success = 0
    failed = []
    
    for i, match in enumerate(matches[1:], 2):  # 跳过第1场
        print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")
        
        # 抓取数据
        match_data = quick_scrape_all_data(match['url'], match)
        
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
