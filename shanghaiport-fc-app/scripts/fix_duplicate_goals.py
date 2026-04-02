#!/usr/bin/env python3
"""
智能修复脚本 - 删除重复进球并验证比分
"""

import json
import glob
from collections import defaultdict

def fix_duplicate_goals(data):
    """删除同一分钟+球员的重复进球"""
    goals = [e for e in data['events'] if e['type'] == 'goal']
    
    # 按分钟+球员分组
    goal_groups = defaultdict(list)
    for g in goals:
        key = (g['minute'], g['player'])
        goal_groups[key].append(g)
    
    # 删除重复（保留第一个）
    duplicate_ids = set()
    for key, group in goal_groups.items():
        if len(group) > 1:
            # 保留主队的，删除客队的重复
            home_goals = [g for g in group if g['team'] == 'home']
            away_goals = [g for g in group if g['team'] == 'away']
            
            if home_goals and away_goals:
                # 同一球员不可能同时为主客队进球，删除客队的
                for g in away_goals:
                    duplicate_ids.add(id(g))
    
    # 过滤掉重复的
    data['events'] = [e for e in data['events'] if id(e) not in duplicate_ids]
    
    # 验证比分
    home_score = data['teams']['home']['score']
    away_score = data['teams']['away']['score']
    expected = home_score + away_score
    
    goals_after = [e for e in data['events'] if e['type'] == 'goal']
    recorded = len(goals_after)
    
    return data, expected == recorded, expected, recorded

def main():
    print("🔧 智能修复脚本")
    print("=" * 70)
    print()
    
    fixed_count = 0
    
    for season in ['2023', '2024', '2025']:
        files = sorted(glob.glob(f'data/match-reports-{season}/*.json'))
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 修复前统计
                goals_before = len([e for e in data['events'] if e['type'] == 'goal'])
                home_score = data['teams']['home']['score']
                away_score = data['teams']['away']['score']
                expected = home_score + away_score
                
                if goals_before == expected:
                    continue  # 跳过正确的
                
                # 修复
                data, is_ok, exp, rec = fix_duplicate_goals(data)
                
                if not is_ok:
                    filename = filepath.split('/')[-1]
                    print(f"⚠️  {season} - {filename}")
                    print(f"    修复前: {goals_before}个进球")
                    print(f"    修复后: {rec}个进球 (期望{exp}个)")
                    
                    # 保存
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    fixed_count += 1
                    
            except Exception as e:
                print(f"❌  处理失败: {filepath} - {e}")
    
    print(f"\n{'=' * 70}")
    print(f"✅ 修复完成: {fixed_count}场比赛")
    print("=" * 70)

if __name__ == '__main__':
    main()
