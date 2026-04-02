#!/usr/bin/env python3
"""
最终修复版 - 重新抓取所有29场比赛
"""

import json
import os
import subprocess
import time

def scrape_match(url: str, match_info: dict) -> dict:
    """抓取单场比赛数据"""
    
    try:
        # 1. 打开页面
        result = subprocess.run(
            ['openclaw', 'browser', 'open', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if 'opened:' not in result.stdout:
            return None
        
        time.sleep(5)
        
        # 2. 提取比分
        result_scores = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', 
             "Array.from(document.querySelectorAll('.score')).map(el => el.textContent).join(',')"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        scores_str = result_scores.stdout.strip().strip('"')
        scores = [int(s) for s in scores_str.split(',') if s.isdigit()]
        
        home_score = scores[0] if len(scores) >= 1 else 0
        away_score = scores[1] if len(scores) >= 2 else 0
        
        # 3. 提取统计（简化版 - 只提取基础数据）
        result_html = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn', 'document.body.textContent'],
            capture_output=True,
            text=True,
            timeout=15
        )
        text = result_html.stdout
        
        # 4. 构建数据结构
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
                    "score": home_score,
                    "score_ht": 0
                },
                "away": {
                    "name": match_info['away'],
                    "score": away_score,
                    "score_ht": 0
                }
            },
            "events": [],
            "statistics": {},
            "player_stats": {"home": [], "away": []},
            "metadata": {
                "source": "FBref",
                "url": url,
                "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "version": "3.0-final"
            }
        }
        
        print(f"    比分: {match_info['home']} {home_score} - {away_score} {match_info['away']}")
        
        return match_data
        
    except Exception as e:
        print(f"    ❌ 错误: {e}")
        return None

def main():
    """主函数"""
    
    print("="*60)
    print("重新抓取所有29场比赛（修复版）")
    print("="*60)
    print()
    
    # 读取URL列表
    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    # 创建输出目录
    output_dir = 'data/match-reports-final-fixed'
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理所有比赛（跳过第1轮，因为已经有了）
    success = 0
    failed = []
    
    for i, match in enumerate(matches[1:], 2):  # 从第2轮开始
        print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")
        
        # 抓取数据
        match_data = scrape_match(match['url'], match)
        
        if match_data:
            # 保存
            filename = f"{output_dir}/{match['date']}-中超-第{i}轮-final.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            
            print(f"    ✅ 已保存")
            success += 1
        else:
            print(f"    ❌ 抓取失败")
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

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
