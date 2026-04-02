#!/usr/bin/env python3
"""
重新提取所有比赛的比分 - 修复版
问题：之前提取的比分可能不准确
"""

import json
import os
import subprocess
import time

def get_scores_from_page(url: str) -> tuple:
    """从页面正确提取比分"""

    try:
        # 打开页面
        result = subprocess.run(
            ['openclaw', 'browser', 'open', url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if 'opened:' not in result.stdout:
            return (0, 0)

        time.sleep(5)

        # 方法1: 提取所有.score元素
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn',
             """(() => {
                const scores = Array.from(document.querySelectorAll('.score'));
                if (scores.length >= 2) {
                    return scores.slice(0, 2).map(s => s.textContent).join(',');
                }
                return '';
             })()"""],
            capture_output=True,
            text=True,
            timeout=15
        )

        scores_str = result.stdout.strip().strip('"')
        if ',' in scores_str:
            parts = scores_str.split(',')
            if len(parts) >= 2:
                home_score = int(parts[0].strip()) if parts[0].strip().isdigit() else 0
                away_score = int(parts[1].strip()) if parts[1].strip().isdigit() else 0
                return (home_score, away_score)

        # 方法2: 从scorebox提取
        result = subprocess.run(
            ['openclaw', 'browser', 'evaluate', '--fn',
             """(() => {
                const scorebox = document.querySelector('.scorebox');
                if (scorebox) {
                    const divs = scorebox.querySelectorAll('div');
                    const scores = [];
                    divs.forEach(div => {
                        const text = div.textContent.trim();
                        if (/^\\d+$/.test(text)) {
                            scores.push(text);
                        }
                    });
                    return scores.slice(0, 2).join(',');
                }
                return '';
             })()"""],
            capture_output=True,
            text=True,
            timeout=15
        )

        scores_str = result.stdout.strip().strip('"')
        if ',' in scores_str:
            parts = scores_str.split(',')
            if len(parts) >= 2:
                home_score = int(parts[0].strip()) if parts[0].strip().isdigit() else 0
                away_score = int(parts[1].strip()) if parts[1].strip().isdigit() else 0
                return (home_score, away_score)

        return (0, 0)

    except Exception as e:
        print(f"      错误: {e}")
        return (0, 0)

def main():
    print("="*60)
    print("重新提取所有比赛的比分")
    print("="*60)
    print()

    output_dir = 'data/match-reports-final-fixed'

    # 读取所有文件
    files = sorted([f for f in os.listdir(output_dir) if f.endswith('.json')])

    print(f"📋 共 {len(files)} 场比赛需要更新\n")

    updated = 0
    errors = []

    for i, filename in enumerate(files, 1):
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            date = data['match_info']['date']
            home = data['teams']['home']['name']
            away = data['teams']['away']['name']
            url = data['metadata']['url']
            old_home_score = data['teams']['home']['score']
            old_away_score = data['teams']['away']['score']

            print(f"[{i}/{len(files)}] {date} - {home} vs {away}")
            print(f"  原比分: {home} {old_home_score} - {old_away_score} {away}")

            # 重新提取比分
            home_score, away_score = get_scores_from_page(url)

            print(f"  新比分: {home} {home_score} - {away_score} {away}")

            # 更新数据
            data['teams']['home']['score'] = home_score
            data['teams']['away']['score'] = away_score

            # 保存
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"  ✅ 已更新")
            updated += 1
            time.sleep(2)

        except Exception as e:
            print(f"  ❌ 错误: {e}")
            errors.append(filename)

    print(f"\n{'='*60}")
    print(f"✅ 更新完成")
    print(f"{'='*60}")
    print(f"成功: {updated}/{len(files)}")
    if errors:
        print(f"失败: {len(errors)}")
        for e in errors:
            print(f"  - {e}")

if __name__ == '__main__':
    main()
