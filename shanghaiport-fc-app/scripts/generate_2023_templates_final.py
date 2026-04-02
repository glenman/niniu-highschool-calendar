#!/usr/bin/env python3
"""
上海海港2023赛季比赛数据框架生成器（精简版）
"""

import json
import os
from datetime import datetime

def main():
    """主函数"""
    
    print("="*70)
    print("上海海港2023赛季比赛数据框架生成器")
    print("="*70)
    print()
    
    # 读取URL列表
    url_file = 'shanghaiport-fc-app/data/2023-match_urls.json'
    print(f"📖 读取比赛列表: {url_file}")
    
    with open(url_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    matches = data['match_urls']
    print(f"✓ 共 {len(matches)} 场比赛\n")
    
    # 创建输出目录
    output_dir = 'shanghaiport-fc-app/data/match-reports-2023'
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 输出目录: {output_dir}\n")
    
    # 处理每场比赛
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match['match_report_url']
        
        # 从URL提取match_id
        match_id = url.split('/')[-2]
        
        # 创建模板数据
        template = {
            "match_info": {
                "match_id": match_id,
                "date": date,
                "time": "20:00",
                "competition": {
                    "name": "Chinese Super League",
                    "season": "2023",
                    "round": f"Matchweek {i}"
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
                    "name": "",
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
                    "name": "",
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
            "statistics": {
                "possession": {"home": 0, "away": 0},
                "shots": {"home": 0, "away": 0},
                "shots_on_target": {"home": 0, "away": 0},
                "saves": {"home": 0, "away": 0},
                "fouls": {"home": 0, "away": 0},
                "corners": {"home": 0, "away": 0},
                "crosses": {"home": 0, "away": 0},
                "interceptions": {"home": 0, "away": 0},
                "offsides": {"home": 0, "away": 0},
                "yellow_cards": {"home": 0, "away": 0},
                "red_cards": {"home": 0, "away": 0}
            },
            "player_stats": {
                "home": [],
                "away": []
            },
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "1.0",
            }
        }
        
        # 保存文件
        filename = f"{date}-中超-第{i}轮.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 第{i}轮: {date}")
    
    print(f"\n{'='*70}")
    print("✅ 数据框架生成完成")
    print(f"{'='*70}")
    print(f"✓ 共生成 {len(matches)} 个JSON文件")
    print(f"\n📁 保存位置: {output_dir}/")
    print(f"\n📝 文件命名: YYYY-MM-DD-中超-第X轮.json")
    print(f"\n⚠️  重要说明:")
    print("  由于FBref使用Cloudflare保护，无法自动抓取完整数据。")
    print("  生成的文件是数据框架，需要手动填充实际比赛数据。")
    print("\n📋 后续步骤:")
    print("  1. 访问 https://fbref.com/en/matches/{MATCH_ID} 查看比赛详情")
    print("  2. 根据COMPLETE_SCRAPER_GUIDE.md的规范填充数据")
    print("  3. 确保数据完整性和准确性")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
