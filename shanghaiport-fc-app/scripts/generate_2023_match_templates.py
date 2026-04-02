#!/usr/bin/env python3
"""
上海海港2023赛季比赛数据框架生成器
根据2023-match_urls.json生成每场比赛的JSON框架文件
"""

import json
import os
from datetime import datetime

# 比赛数据框架模板
def create_match_template(match_url: str, date: str, round_num: int) -> dict:
    """创建单场比赛的数据框架"""
    
    # 从URL解析对手信息
    # URL格式: https://fbref.com/en/matches/{ID}/{Team1}-{Team2}-{Date}-Chinese-Super-League
    url_parts = match_url.split('/')
    match_id = url_parts[-2] if len(url_parts) > 5 else ''
    
    # 解析球队名称（简化版）
    teams_part = url_parts[-1] if len(url_parts) > 5 else ''
    
    # 判断主客场
    is_home = 'Shanghai-Port' in teams_part.split('-Shanghai-Port')[0]
    
    template = {
        "match_info": {
            "match_id": match_id,
            "date": date,
            "time": "19:35",  # 默认比赛时间
            "competition": {
                "name": "Chinese Football Association Super League",
                "season": "2023",
                "round": f"Matchweek {round_num}"
            },
            "venue": {
                "name": "待填充",
                "city": "Shanghai" if is_home else "待填充",
                "attendance": 0
            },
            "referee": {
                "name": "待填充",
                "country": "China"
            }
        },
        "teams": {
            "home": {
                "name": "Shanghai Port FC" if is_home else "待填充",
                "full_name": "Shanghai Port Football Club" if is_home else "待填充",
                "score": 0,
                "score_ht": 0,
                "formation": "待填充",
                "coach": "待填充",
                "captain": "待填充",
                "lineup": [],
                "substitutes": [],
                "substitutions": []
            },
            "away": {
                "name": "待填充" if is_home else "Shanghai Port FC",
                "full_name": "待填充" if is_home else "Shanghai Port Football Club",
                "score": 0,
                "score_ht": 0,
                "formation": "待填充",
                "coach": "待填充",
                "captain": "待填充",
                "lineup": [],
                "substitutes": [],
                "substitutions": []
            }
        },
        "events": [],  # 比赛事件（进球、黄牌、红牌等）
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
            "url": match_url,
            "created_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "status": "template",  # template, partial, complete
            "version": "1.0",
            "notes": "此文件为数据框架，需要手动或使用抓取脚本填充完整数据"
        }
    }
    
    return template

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
    
    # 生成每场比赛的框架
    print("开始生成数据框架...")
    print()
    
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match['match_report_url']
        
        # 生成文件名：比赛日期-中超-第X轮.json
        filename = f"{date}-中超-第{i}轮.json"
        filepath = os.path.join(output_dir, filename)
        
        # 创建数据框架
        template = create_match_template(url, date, i)
        
        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"  [{i:2d}/{len(matches)}] {filename}")
    
    # 生成汇总文件
    print("\n生成汇总文件...")
    summary = {
        "season": 2023,
        "team": "Shanghai Port FC",
        "competition": "Chinese Super League",
        "total_matches": len(matches),
        "data_directory": output_dir,
        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "match_files": [
            {
                "round": i,
                "date": match['date'],
                "filename": f"{match['date']}-中超-第{i}轮.json",
                "url": match['match_report_url']
            }
            for i, match in enumerate(matches, 1)
        ]
    }
    
    summary_file = os.path.join(output_dir, 'SUMMARY.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已保存: {summary_file}")
    
    # 完成
    print(f"\n{'='*70}")
    print("✅ 数据框架生成完成")
    print(f"{'='*70}")
    print(f"\n📊 生成统计:")
    print(f"  ✓ 比赛场次: {len(matches)} 场")
    print(f"  ✓ 文件位置: {output_dir}/")
    print(f"  ✓ 文件命名: YYYY-MM-DD-中超-第X轮.json")
    print(f"\n📝 每个文件包含:")
    print(f"  ✓ 比赛基本信息框架")
    print(f"  ✓ 球队信息框架")
    print(f"  ✓ 统计数据框架（11项）")
    print(f"  ✓ 元数据（含原始URL）")
    print(f"\n⚠️  下一步:")
    print(f"  1. 手动填充比赛数据")
    print(f"  2. 或使用抓取脚本自动填充（需要绕过Cloudflare保护）")
    print(f"  3. 更新metadata.status为 'partial' 或 'complete'")
    print(f"\n{'='*70}\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
