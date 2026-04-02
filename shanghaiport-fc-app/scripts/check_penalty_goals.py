#!/usr/bin/env python3
"""
检查2025赛季比赛报告中是否有丢失的penalty_goal
"""

import json
import glob
import os

def check_penalty_goals():
    """检查所有2025赛季比赛报告中的penalty_goal"""
    
    files = sorted(glob.glob('data/match-reports-2025/*.json'))
    
    print(f"📋 检查 {len(files)} 场比赛报告\n")
    
    total_goals = 0
    penalty_goals = 0
    own_goals = 0
    regular_goals = 0
    
    matches_with_issues = []
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        filename = os.path.basename(filepath)
        goals = [e for e in data['events'] if e['type'] == 'goal']
        
        for goal in goals:
            total_goals += 1
            goal_type = goal.get('goal_type', '')
            
            if goal_type == 'penalty_goal':
                penalty_goals += 1
            elif goal_type == 'own_goal':
                own_goals += 1
            elif goal_type == 'goal':
                regular_goals += 1
            else:
                # 没有goal_type字段的进球
                matches_with_issues.append({
                    'file': filename,
                    'minute': goal['minute'],
                    'player': goal['player'],
                    'goal_type': goal_type
                })
    
    print("=" * 70)
    print("进球统计")
    print("=" * 70)
    print(f"总进球数: {total_goals}")
    print(f"  - 普通进球: {regular_goals}")
    print(f"  - 点球: {penalty_goals}")
    print(f"  - 乌龙球: {own_goals}")
    print()
    
    if matches_with_issues:
        print("=" * 70)
        print("问题进球（缺少goal_type）")
        print("=" * 70)
        for issue in matches_with_issues:
            print(f"{issue['file']}")
            print(f"  {issue['minute']}' {issue['player']} - goal_type: {issue['goal_type']}")
    
    return {
        'total': total_goals,
        'penalty': penalty_goals,
        'own': own_goals,
        'regular': regular_goals,
        'issues': matches_with_issues
    }

if __name__ == "__main__":
    stats = check_penalty_goals()
    
    print("\n" + "=" * 70)
    print("结论")
    print("=" * 70)
    print(f"✅ 找到 {stats['penalty']} 个点球")
    print(f"✅ 找到 {stats['own']} 个乌龙球")
    
    if stats['issues']:
        print(f"⚠️  有 {len(stats['issues'])} 个进球缺少正确的goal_type")
    else:
        print("✅ 所有进球都有正确的goal_type")
