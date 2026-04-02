#!/usr/bin/env python3
"""
验证文件名与数据中matchweek的一致性

用法:
  python3 scripts/verify_matchweek.py              # 验证所有赛季
  python3 scripts/verify_matchweek.py --season 2025  # 验证特定赛季
"""

import json
import glob
import os
import argparse
from pathlib import Path

def verify_season(season):
    """验证特定赛季的matchweek一致性"""
    dir_path = f'data/match-reports-{season}'
    
    if not os.path.exists(dir_path):
        print(f"⚠️  目录不存在: {dir_path}")
        return []
    
    files = sorted(glob.glob(f'{dir_path}/*.json'))
    
    if not files:
        print(f"⚠️  没有找到文件: {dir_path}")
        return []
    
    print(f"\n{'='*70}")
    print(f"{season}赛季验证")
    print(f"{'='*70}")
    
    matches = []
    mismatches = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        
        try:
            data = json.load(open(filepath, 'r', encoding='utf-8'))
            
            # 从文件名提取轮次
            if '-第' in filename:
                filename_round = filename.split('-第')[1].split('轮')[0]
            else:
                filename_round = '?'
            
            # 从数据中提取matchweek
            round_info = data.get('match_info', {}).get('competition', {}).get('round', '')
            if round_info:
                data_round = round_info.split()[-1]
            else:
                data_round = '?'
            
            # 检查是否匹配
            if filename_round == data_round:
                matches.append({
                    'file': filename,
                    'round': filename_round,
                    'date': data.get('match_info', {}).get('date', ''),
                    'teams': f"{data.get('teams', {}).get('home', {}).get('name', '')} vs {data.get('teams', {}).get('away', {}).get('name', '')}"
                })
            else:
                mismatches.append({
                    'file': filename,
                    'filename_round': filename_round,
                    'data_round': data_round,
                    'date': data.get('match_info', {}).get('date', ''),
                    'teams': f"{data.get('teams', {}).get('home', {}).get('name', '')} vs {data.get('teams', {}).get('away', {}).get('name', '')}"
                })
        except Exception as e:
            print(f"  ❌ 读取失败: {filename} - {e}")
    
    # 显示结果
    print(f"\n检查文件: {len(files)} 个")
    print(f"✅ 匹配: {len(matches)} 个")
    print(f"❌ 不匹配: {len(mismatches)} 个")
    
    if mismatches:
        print(f"\n⚠️  不匹配的文件:")
        for m in mismatches:
            print(f"\n  📄 {m['file']}")
            print(f"     文件名: 第{m['filename_round']}轮")
            print(f"     数据中: 第{m['data_round']}轮")
            print(f"     日期: {m['date']}")
            print(f"     比赛: {m['teams']}")
    else:
        print(f"\n✅ 所有文件名与数据中的matchweek一致!")
    
    return mismatches

def main():
    parser = argparse.ArgumentParser(description='验证matchweek一致性')
    parser.add_argument('--season', type=str, help='验证特定赛季 (例如: 2025)')
    args = parser.parse_args()
    
    print("📊 Matchweek一致性验证工具")
    print("=" * 70)
    
    total_mismatches = 0
    
    if args.season:
        # 验证特定赛季
        verify_season(args.season)
    else:
        # 验证所有赛季
        for season in ['2023', '2024', '2025']:
            mismatches = verify_season(season)
            total_mismatches += len(mismatches)
    
    print(f"\n{'='*70}")
    if total_mismatches == 0:
        print(f"✅ 所有赛季验证完成 - 无问题")
    else:
        print(f"⚠️  总计发现 {total_mismatches} 个不匹配")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
