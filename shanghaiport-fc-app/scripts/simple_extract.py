#!/usr/bin/env python3
import subprocess
import json
import re

print("获取统计数据...")

js = """
(function() {
    const div = document.querySelector('#team_stats');
    return div ? div.textContent : 'Not found';
})()
"""

result = subprocess.run(
    ['openclaw', 'browser', 'evaluate', '--fn', js],
    capture_output=True,
    text=True,
    timeout=30
)

text = result.stdout.strip()

# 保存
with open('data/match1_stats_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print("✅ 已保存")
print("\n内容:")
print(text[:2000])
