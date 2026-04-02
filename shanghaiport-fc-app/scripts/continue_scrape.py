#!/usr/bin/env python3
"""继续处理剩余的14场比赛"""

import json
import os
import subprocess
import time

def scrape_match(url: str, match_info: dict) -> dict:
    try:
        result = subprocess.run(['openclaw', 'browser', 'open', url], capture_output=True, text=True, timeout=30)
        if 'opened:' not in result.stdout:
            return None
        time.sleep(5)

        result_scores = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn',
             "Array.from(document.querySelectorAll('.score')).map(el => el.textContent).join(',')"],
            capture_output=True, text=True, timeout=15
        )

        scores_str = result_scores.stdout.strip().strip('"')
        scores = [int(s) for s in scores_str.split(',') if s.isdigit()]
        home_score = scores[0] if len(scores) >= 1 else 0
        away_score = scores[1] if len(scores) >= 2 else 0

        match_data = {
            "match_info": {
                "match_id": url.split('/')[-2],
                "date": match_info['date'],
                "time": "20:00",
                "competition": {"name": "Chinese Football Association Super League", "season": "2024", "round": f"Matchweek {match_info['index']}"},
                "venue": {"name": "", "city": "", "attendance": 0},
                "referee": {"name": "", "country": "China"}
            },
            "teams": {
                "home": {"name": match_info['home'], "score": home_score, "score_ht": 0},
                "away": {"name": match_info['away'], "score": away_score, "score_ht": 0}
            },
            "events": [],
            "statistics": {},
            "player_stats": {"home": [], "away": []},
            "metadata": {"source": "FBref", "url": url, "scraped_at": time.strftime('%Y-%m-%dT%H:%M:%S'), "version": "3.0-final"}
        }

        print(f"    比分: {match_info['home']} {home_score} - {away_score} {match_info['away']}")
        return match_data
    except Exception as e:
        print(f"    ❌ 错误: {e}")
        return None

def main():
    print("="*60)
    print("继续处理剩余14场比赛")
    print("="*60)

    with open('data/match_urls.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)

    output_dir = 'data/match-reports-final-fixed'
    os.makedirs(output_dir, exist_ok=True)

    # 从第19轮开始（索引18）
    success = 0
    for i in range(18, 30):
        match = matches[i]
        print(f"\n[{i+1}/30] {match['date']} - {match['home']} vs {match['away']}")

        match_data = scrape_match(match['url'], match)
        if match_data:
            filename = f"{output_dir}/{match['date']}-中超-第{i+1}轮-final.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            print(f"    ✅ 已保存")
            success += 1
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"✅ 处理完成: {success}/12")
    print(f"总共: {15 + success}/29")

if __name__ == '__main__':
    main()
