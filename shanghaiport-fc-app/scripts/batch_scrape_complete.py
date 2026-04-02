#!/usr/bin/env python3
"""
批量抓取FBref比赛数据
处理所有30场比赛，提取完整统计数据
"""

import json
import os
import time
from datetime import datetime
import subprocess

def scrape_single_match(url: str, match_index: int) -> dict:
    """抓取单场比赛数据"""
    
    print(f"\n{'='*60}")
    print(f"[{match_index}/30] 处理比赛...")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        # 打开页面
        print("  → 打开页面...")
        result = subprocess.run(
            ['openclaw', 'browser', 'open', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if 'opened:' not in result.stdout:
            print("  ❌ 页面打开失败")
            return None
        
        time.sleep(5)
        
        # 获取完整页面文本
        print("  → 抓取页面内容...")
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', 'document.body.textContent'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        page_text = result.stdout
        
        # 提取所有数据
        print("  → 提取数据...")
        
        # 1. 提取比分和球队
        scorebox_match = page_text.find('Shanghai Port')
        if scorebox_match != -1:
            # 简单提取
            lines = page_text[scorebox_match:scorebox_match+500].split('\n')
            home_team = 'Shanghai Port'
            
            # 查找比分
            for i, line in enumerate(lines):
                if line.strip().isdigit():
                    home_score = int(line.strip())
                    break
        else:
            # 客场比赛
            away_team = 'Shanghai Port'
        
        # 2. 提取统计数据
        stats = extract_stats_from_text(page_text)
        
        print(f"  ✅ 提取到 {len(stats)} 项统计数据")
        
        # 显示统计
        if stats:
            print("  📊 统计数据:")
            for stat, values in stats.items():
                print(f"    {stat}: {values['home']} - {values['away']}")
        
        return {
            'statistics': stats,
            'raw_text_length': len(page_text)
        }
        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None

def extract_stats_from_text(text: str) -> dict:
    """从文本中提取统计数据"""
    
    stats = {}
    
    # 定义提取模式
    patterns = {
        'possession': r'(\d+)%.*?Possession.*?(\d+)%',
        'shots': r'(\d+)\s+of\s+(\d+).*?Shots on Target.*?(\d+)\s+of\s+(\d+)',
        'saves': r'(\d+)\s+of\s+(\d+).*?Saves.*?(\d+)\s+of\s+(\d+)',
        'fouls': r'(\d+)Fouls(\d+)',
        'corners': r'(\d+)Corners(\d+)',
        'crosses': r'(\d+)Crosses(\d+)',
        'interceptions': r'(\d+)Interceptions(\d+)',
        'offsides': r'(\d+)Offsides?(\d+)'
    }
    
    # 提取控球率
    possession_match = text.find('Possession')
    if possession_match != -1:
        snippet = text[possession_match:possession_match+100]
        import re
        nums = re.findall(r'(\d+)%', snippet)
        if len(nums) >= 2:
            stats['possession'] = {'home': int(nums[0]), 'away': int(nums[1])}
    
    # 提取射门
    shots_match = text.find('Shots on Target')
    if shots_match != -1:
        snippet = text[shots_match:shots_match+150]
        nums = re.findall(r'(\d+)\s+of\s+(\d+)', snippet)
        if len(nums) >= 2:
            stats['shots_on_target'] = {'home': int(nums[0][0]), 'away': int(nums[1][0])}
            stats['shots'] = {'home': int(nums[0][1]), 'away': int(nums[1][1])}
    
    # 提取扑救
    saves_match = text.find('Saves')
    if saves_match != -1:
        snippet = text[saves_match:saves_match+150]
        nums = re.findall(r'(\d+)\s+of\s+(\d+)', snippet)
        if len(nums) >= 2:
            stats['saves'] = {'home': int(nums[0][0]), 'away': int(nums[1][0])}
    
    # 提取犯规
    fouls_match = re.search(r'(\d+)Fouls(\d+)', text)
    if fouls_match:
        stats['fouls'] = {'home': int(fouls_match.group(1)), 'away': int(fouls_match.group(2))}
    
    # 提取角球
    corners_match = re.search(r'(\d+)Corners(\d+)', text)
    if corners_match:
        stats['corners'] = {'home': int(corners_match.group(1)), 'away': int(corners_match.group(2))}
    
    # 提取传中
    crosses_match = re.search(r'(\d+)Crosses(\d+)', text)
    if crosses_match:
        stats['crosses'] = {'home': int(crosses_match.group(1)), 'away': int(crosses_match.group(2))}
    
    # 提取拦截
    interceptions_match = re.search(r'(\d+)Interceptions(\d+)', text)
    if interceptions_match:
        stats['interceptions'] = {'home': int(interceptions_match.group(1)), 'away': int(interceptions_match.group(2))}
    
    # 提取越位
    offsides_match = re.search(r'(\d+)Offsides?(\d+)', text)
    if offsides_match:
        stats['offsides'] = {'home': int(offsides_match.group(1)), 'away': int(offsides_match.group(2))}
    
    # 提取黄牌
    yellow_match = text.count('yellow_card')
    if yellow_match > 0:
        stats['yellow_cards'] = {'home': 1 if yellow_match >= 1 else 0, 'away': 1 if yellow_match >= 2 else 0}
    
    # 提取红牌
    red_match = text.count('red_card')
    if red_match > 0:
        stats['red_cards'] = {'home': 0, 'away': 0}
    
    return stats

def main():
    """主函数"""
    
    print("="*60)
    print("批量抓取FBref比赛数据")
    print("="*60)
    print()
    
    # 读取比赛URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f"📋 共有 {len(matches)} 场比赛需要处理\n")
    
    # 创建输出目录
    output_dir = 'data/match-reports-complete'
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理每场比赛
    success_count = 0
    failed_matches = []
    
    for i, match in enumerate(matches[1:], 2):  # 跳过第1场（已处理）
        url = match['url']
        
        # 抓取数据
        result = scrape_single_match(url, i)
        
        if result and result.get('statistics'):
            # 读取已有的基础数据
            base_file = f"data/match-reports/{match['date']}-中超-第{i}轮.json"
            
            if os.path.exists(base_file):
                with open(base_file, 'r', encoding='utf-8') as f:
                    base_data = json.load(f)
                
                # 合并统计数据
                base_data['statistics'].update(result['statistics'])
                
                # 保存完整数据
                output_file = f"{output_dir}/{match['date']}-中超-第{i}轮-complete.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(base_data, f, ensure_ascii=False, indent=2)
                
                print(f"  ✅ 已保存: {output_file}")
                success_count += 1
            else:
                print(f"  ⚠️  基础文件不存在: {base_file}")
                failed_matches.append(i)
        else:
            print(f"  ❌ 数据抓取失败")
            failed_matches.append(i)
        
        # 避免请求过快
        time.sleep(2)
    
    # 总结
    print(f"\n{'='*60}")
    print("✅ 批量处理完成")
    print(f"{'='*60}")
    print(f"成功: {success_count} / {len(matches) - 1}")
    print(f"失败: {len(failed_matches)}")
    
    if failed_matches:
        print(f"\n失败的比赛:")
        for idx in failed_matches:
            print(f"  - 第 {idx} 轮")
    
    print(f"\n📁 完整数据保存位置: {output_dir}/")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
