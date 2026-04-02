#!/usr/bin/env python3
"""修复10场0-0比分的比赛"""

import json
import os
import subprocess
import time

def get_correct_score(url: str) -> tuple:
    """从页面提取正确比分"""
    try:
        result = subprocess.run(['openclaw', 'browser', 'open', url], capture_output=True, text=True, timeout=30)
        if 'opened:' not in result.stdout:
            return None
        time.sleep(5)

        # 提取比分 - 改进版
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn',
             """(() => {
                const scorebox = document.querySelector('.scorebox') || document.querySelector('#content');
                if (!scorebox) return '0,0';

                const scores = scorebox.querySelectorAll('.score');
                if (scores.length >= 2) {
                    return Array.from(scores).map(s => s.textContent.trim()).join(',');
                }
                return '0,0';
             })()""],
            capture_output=True,
            text=True,
            timeout=15
        )

        scores_str = result.stdout.strip().strip('"')
        parts = scores_str.split(',')
        if len(parts) >= 2:
            return (int(parts[0]), int(parts[1]))
        return None

    except Exception as e:
        print(f"    错误: {e}")
        return None

def main():
    print("="*60)
    print("修复10场0-0比分的比赛")
    print("="*60)

    # 需要修复的比赛
    matches_to_fix = [
        "2024-03-09-中超-第2轮-final.json",
        "2024-05-26-中超-第13轮-final.json",
        "2024-07-26-中超-第21轮-final.json",
        "2024-08-03-中超-第22轮-final.json",
        "2024-08-09-中超-第23轮-final.json",
        "2024-09-13-中超-第25轮-final.json",
        "2024-09-28-中超-第27轮-final.json",
        "2024-10-18-中超-第28轮-final.json",
        "2024-10-27-中超-第29轮-final.json",
        "2024-11-02-中超-第30轮-final.json",
    ]

    output_dir = 'data/match-reports-final-fixed'
    fixed = 0

    for filename in matches_to_fix:
        filepath = os.path.join(output_dir, filename)
        if not os.path.exists(filepath):
            print(f"\n❌ 文件不存在: {filename}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        home = data['teams']['home']['name']
        away = data['teams']['away']['name']
        url = data['metadata']['url']

        print(f"\n{filename}")
        print(f"  {home} vs {away}")

        scores = get_correct_score(url)
        if scores:
            home_score, away_score = scores
            print(f"  新比分: {home} {home_score} - {away_score} {away}")

            data['teams']['home']['score'] = home_score
            data['teams']['away']['score'] = away_score

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"  ✅ 已修复")
            fixed += 1
        else:
            print(f"  ❌ 提取失败")

        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"✅ 完成！修复: {fixed}/10")

if __name__ == '__main__':
    main()
