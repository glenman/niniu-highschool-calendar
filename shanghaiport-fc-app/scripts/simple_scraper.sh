#!/bin/bash
# 简单的批量抓取脚本

OUTPUT_DIR="data/match-reports-simple"
mkdir -p "$OUTPUT_DIR"

# 读取比赛列表
python3 << 'PYEOF'
import json
import subprocess
import time
import os

with open('data/match_urls.json') as f:
    matches = json.load(f)

output_dir = 'data/match-reports-simple'
os.makedirs(output_dir, exist_ok=True)

for i, match in enumerate(matches[1:], 2):
    print(f"\n[{i}/30] {match['date']} - {match['home']} vs {match['away']}")
    
    # 打开页面
    subprocess.run(['openclaw', 'browser', 'open', match['url']], 
                   capture_output=True, timeout=30)
    time.sleep(5)
    
    # 保存HTML到文件
    result = subprocess.run(
        ['openclaw', 'browser', 'evaluate', '--fn', 'document.documentElement.outerHTML'],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    # 提取HTML（去掉前面的日志）
    html_lines = result.stdout.split('\n')
    html = '\n'.join([line for line in html_lines if not line.startswith('[') and not line.startswith('Config')])
    
    # 保存
    filename = f"{output_dir}/{match['date']}-第{i}轮.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  ✅ 已保存: {filename}")
    time.sleep(2)

print("\n✅ 全部完成！")
PYEOF
