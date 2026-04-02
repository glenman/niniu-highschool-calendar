#!/usr/bin/env python3
"""
测试版：只抓取第一场比赛数据
"""

import json
import os
import subprocess
import time
from datetime import datetime
import re

# 测试URL - 第一场比赛
TEST_URL = "https://fbref.com/en/matches/13f114b6/Wuhan-Three-Towns-Shanghai-Port-April-15-2023-Chinese-Super-League"
TEST_DATE = "2023-04-15"
TEST_ROUND = 1

def test_scrape():
    """测试抓取第一场比赛"""
    
    print("="*70)
    print("测试抓取第一场比赛数据")
    print("="*70)
    print()
    
    # 1. 打开浏览器
    print("→ 打开浏览器...")
    result = subprocess.run(
        ['agent-browser', 'close'],
        capture_output=True,
        timeout=5
    )
    time.sleep(1)
    
    # 2. 打开页面
    print(f"→ 打开页面: {TEST_URL}")
    result = subprocess.run(
        ['agent-browser', 'open', TEST_URL],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        print(f"❌ 打开失败: {result.stderr}")
        return
    
    print("✓ 页面已加载")
    time.sleep(10)  # 等待Cloudflare验证和页面渲染
    
    # 3. 获取HTML
    print("→ 提取HTML...")
    result_html = subprocess.run(
        ['agent-browser', 'eval', 'document.documentElement.outerHTML'],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    if result_html.returncode != 0:
        print(f"❌ 提取失败")
        return
    
    html = result_html.stdout
    print(f"✓ HTML长度: {len(html)} 字符")
    
    # 4. 获取文本
    print("→ 提取文本...")
    result_text = subprocess.run(
        ['agent-browser', 'eval', 'document.body.textContent'],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    text = result_text.stdout if result_text.returncode == 0 else ""
    print(f"✓ 文本长度: {len(text)} 字符")
    
    # 5. 保存原始数据以供分析
    os.makedirs('shanghaiport-fc-app/data/test', exist_ok=True)
    
    with open('shanghaiport-fc-app/data/test/match1_html.txt', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ 已保存HTML")
    
    with open('shanghaiport-fc-app/data/test/match1_text.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("✓ 已保存文本")
    
    # 6. 关闭浏览器
    print("\n→ 关闭浏览器...")
    subprocess.run(['agent-browser', 'close'], capture_output=True, timeout=5)
    
    print("\n✅ 测试完成！")
    print("\n请检查以下文件:")
    print("  - shanghaiport-fc-app/data/test/match1_html.txt")
    print("  - shanghaiport-fc-app/data/test/match1_text.txt")

if __name__ == '__main__':
    try:
        test_scrape()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
