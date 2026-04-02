#!/usr/bin/env python3
"""检查抓取进度"""

import os
import json

output_dir = 'data/match-reports-100percent'

if not os.path.exists(output_dir):
    print("目录不存在")
    exit(1)

files = [f for f in os.listdir(output_dir) if f.endswith('.json')]

print(f"已完成: {len(files)}/29\n")

if files:
    print("文件列表:")
    for f in sorted(files):
        filepath = os.path.join(output_dir, f)
        with open(filepath, 'r') as file:
            data = json.load(file)
        
        stats_count = len(data.get('statistics', {}))
        lineup_count = len(data.get('teams', {}).get('home', {}).get('lineup', []))
        
        print(f"  {f}")
        print(f"    统计: {stats_count}项, 阵容: {lineup_count}人")
