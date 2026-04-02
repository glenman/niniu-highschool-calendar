#!/usr/bin/env python3
"""
快速批量抓取 - 简化版
"""

import json
import subprocess
import time
import os

def quick_scrape(url, match_num):
    """快速抓取单场比赛"""
    print(f"\n[{match_num}/30] 处理中...")

    try:
        # 打开页面
        result = subprocess.run(
            ["openclaw", "browser", "open", url],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "opened:" not in result.stdout:
            print(f"  ❌ 失败")
            return None

        print(f"  ✅ 页面已打开")
        time.sleep(5)

        # 抓取基本信息
        js = "(function() { return JSON.stringify({title: document.title, scorebox: document.querySelector('.scorebox')?.innerText || ''}); })()"

        result = subprocess.run(
            ["openclaw", "browser", "evaluate", "--fn", js],
            capture_output=True,
            text=True,
            timeout=15
        )

        lines = result.stdout.strip().split('\n')
        json_str = lines[-1] if lines else ""

        if json_str and json_str != "{}":
            print(f"  ✅ 数据抓取成功")
            return json.loads(json_str)
        else:
            print(f"  ❌ 无数据")
            return None

    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None

def main():
    print("开始批量抓取...")

    # 读取URL列表
    with open('data/match_urls.json', 'r') as f:
        matches = json.load(f)

    # 创建输出目录
    os.makedirs('data/match-reports', exist_ok=True)

    success = 0
    for i, match in enumerate(matches[1:], 2):  # 跳过第1场
        raw = quick_scrape(match['url'], i)

        if raw:
            # 简单处理
            data = {
                "match_info": {
                    "date": match['date'],
                    "competition": {"name": "中超", "round": f"第{i}轮"}
                },
                "teams": {
                    "home": {"name": match['home']},
                    "away": {"name": match['away']}
                },
                "raw_data": raw
            }

            filename = f"{match['date']}-中超-第{i}轮.json"
            with open(f'data/match-reports/{filename}', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"  ✅ 已保存: {filename}")
            success += 1
            time.sleep(2)

    print(f"\n完成！成功: {success}/29")

if __name__ == "__main__":
    main()
