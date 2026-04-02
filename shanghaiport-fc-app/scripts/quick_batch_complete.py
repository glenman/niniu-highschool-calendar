#!/usr/bin/env python3
"""
快速批量补充统计数据
基于已有的基础数据，补充详细统计
"""

import json
import os
import re
import subprocess
import time

def quick_scrape_stats(url):
    """快速抓取统计数据"""
    
    try:
        # 打开页面
        result = subprocess.run(
            ['openclaw', 'browser', 'open', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if 'opened:' not in result.stdout:
            return None
        
        time.sleep(5)
        
        # 获取页面文本
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', 'document.body.textContent'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        text = result.stdout
        
        # 提取统计数据
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
        
        # 红牌
        stats['red_cards'] = {'home': 0, 'away': 0}
        
        return stats
        
    except Exception as e:
        print(f"    错误: {e}")
        return None

def main():
    """主函数"""
    
    print("="*60)
    print("批量补充详细统计数据")
    print("="*60)
    print()
    
    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    print(f"📋 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'data/match-reports-complete'
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理每场比赛
    success = 0
    failed = []
    
    for i, match in enumerate(matches[1:], 2):  # 跳过第1场
        print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")
        
        # 抓取统计数据
        stats = quick_scrape_stats(match['url'])
        
        if stats and len(stats) > 3:  # 至少有3项统计
            # 读取基础数据
            base_file = f"data/match-reports/{match['date']}-中超-第{i}轮.json"
            
            if os.path.exists(base_file):
                with open(base_file, 'r', encoding='utf-8') as f:
                    base_data = json.load(f)
                
                # 合并统计
                if 'statistics' not in base_data:
                    base_data['statistics'] = {}
                
                base_data['statistics'].update(stats)
                
                # 保存
                output_file = f"{output_dir}/{match['date']}-中超-第{i}轮-complete.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(base_data, f, ensure_ascii=False, indent=2)
                
                print(f"  ✅ 已保存 ({len(stats)} 项统计)")
                success += 1
            else:
                print(f"  ⚠️  基础文件不存在")
                failed.append(i)
        else:
            print(f"  ❌ 统计数据不足")
            failed.append(i)
        
        time.sleep(2)
    
    # 总结
    print(f"\n{'='*60}")
    print(f"✅ 处理完成")
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
