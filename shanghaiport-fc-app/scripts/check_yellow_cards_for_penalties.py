#!/usr/bin/env python3
"""
检查黄牌事件中是否有点球被误记录
"""

import json
import glob

for season in ['2024', '2025']:
    files = sorted(glob.glob(f'data/match-reports-{season}/*.json'))
    
    print(f"\n📊 {season}赛季检查黄牌中的点球\n")
    print("=" * 70)
    
    for filepath in files:
        data = json.load(open(filepath))
        
        # 获取黄牌事件
        yellow_cards = [e for e in data['events'] if e['type'] == 'yellow_card']
        
        # 检查黄牌中是否有(P)标记
        for yc in yellow_cards:
            # 检查原始文本
            raw_text = yc.get('text', '')
            if '(P)' in raw_text or 'Penalty' in raw_text or 'penalty' in raw_text.lower():
                filename = filepath.split('/')[-1].replace('.json', '')
                print(f"❌ {filename}")
                print(f"  黄牌: {yc['minute']}' - {yc['player']}")
                print(f"  原始文本: {raw_text[:100]}")
