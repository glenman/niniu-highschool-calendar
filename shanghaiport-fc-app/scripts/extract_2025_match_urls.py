#!/usr/bin/env python3
"""
从已提取的Match Report URL生成2025赛季JSON文件
"""

import json
import re
from datetime import datetime

# 从fbref.com实际提取的30个Match Report URL (2026-03-28)
# 这些是从agent-browser成功提取的真实URL
match_report_urls = [
    "https://fbref.com/en/matches/a67ccb3a/Shanghai-Port-Shenzhen-Peng-City-February-23-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/3b73c88e/Shanghai-Port-Changchun-Yatai-February-28-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/2f370b43/Qingdao-West-Coast-Shanghai-Port-March-28-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/c68a6901/Shanghai-Port-Meizhou-Hakka-April-2-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/803b999f/Shanghai-Port-Shanghai-Shenhua-April-6-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/c6873008/Tianjin-Jinmen-Tiger-Shanghai-Port-April-16-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/0ba10b52/Shanghai-Port-Chengdu-Rongcheng-April-20-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/17986854/Yunnan-Yukun-Shanghai-Port-April-25-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/8566c2e7/Shanghai-Port-Beijing-Guoan-May-1-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/0335ec07/Wuhan-Three-Towns-Shanghai-Port-May-5-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/353e5683/Shanghai-Port-Qingdao-Hainiu-May-9-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/568d7618/Shanghai-Port-Shandong-Taishan-May-17-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/fbeb6358/Zhejiang-Professional-Shanghai-Port-June-14-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/b5329d01/Henan-Shanghai-Port-June-18-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/4a677b43/Shanghai-Port-Dalian-Yingbo-June-26-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/7cd535f9/Shenzhen-Peng-City-Shanghai-Port-June-30-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/255615e4/Changchun-Yatai-Shanghai-Port-July-18-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/060cb1c5/Shanghai-Port-Qingdao-West-Coast-July-26-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/368deade/Meizhou-Hakka-Shanghai-Port-August-2-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/7432a7ba/Shanghai-Shenhua-Shanghai-Port-August-9-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/29084c32/Shanghai-Port-Henan-August-15-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/ca6210fb/Shanghai-Port-Tianjin-Jinmen-Tiger-August-24-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/8a9a13cd/Chengdu-Rongcheng-Shanghai-Port-August-30-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/69db674c/Shanghai-Port-Yunnan-Yukun-September-12-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/22415967/Beijing-Guoan-Shanghai-Port-September-21-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/d89a6df4/Shanghai-Port-Wuhan-Three-Towns-September-26-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/ec35cbb7/Qingdao-Hainiu-Shanghai-Port-October-17-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/f9c8d5c7/Shandong-Taishan-Shanghai-Port-October-26-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/cd0da27e/Shanghai-Port-Zhejiang-Professional-October-31-2025-Chinese-Super-League",
    "https://fbref.com/en/matches/e94b4d3f/Dalian-Yingbo-Shanghai-Port-November-22-2025-Chinese-Super-League",
]

# 月份名称映射
month_map = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04',
    'May': '05', 'June': '06', 'July': '07', 'August': '08',
    'September': '09', 'October': '10', 'November': '11', 'December': '12'
}

def parse_date_from_url(url):
    """从URL中解析日期"""
    # URL格式: ...-Month-Day-YYYY-Chinese-Super-League
    pattern = r'([A-Z][a-z]+)-(\d+)-(\d{4})-Chinese-Super-League'
    match = re.search(pattern, url)
    
    if match:
        month_name, day, year = match.groups()
        month = month_map.get(month_name, '01')
        day = day.zfill(2)
        return f"{year}-{month}-{day}"
    
    return ""

def parse_teams_from_url(url):
    """从URL中解析对阵双方"""
    # URL格式: https://fbref.com/en/matches/{ID}/{Team1}-{Team2}-{Date}-Chinese-Super-League
    # 示例: Shanghai-Port-Shenzhen-Peng-City-February-23-2025-Chinese-Super-League
    pattern = r'/matches/[a-z0-9]+/(.+?)-([A-Z][a-z]+)-\d+-\d{4}-Chinese-Super-League'
    match = re.search(pattern, url)
    
    if match:
        teams_part = match.group(1)
        return teams_part
    
    return ""

# 生成JSON数据
match_urls = []
for url in match_report_urls:
    date = parse_date_from_url(url)
    teams = parse_teams_from_url(url)
    
    match_urls.append({
        "date": date,
        "teams": teams,
        "match_report_url": url
    })

# 按日期排序
match_urls.sort(key=lambda x: x["date"])

# 生成最终JSON结构
output = {
    "team": "Shanghai Port FC",
    "season": 2025,
    "competition": "Chinese Super League",
    "data_source": "fbref.com",
    "last_updated": datetime.now().strftime("%Y-%m-%d"),
    "total_matches": len(match_urls),
    "match_urls": match_urls
}

# 保存到文件（使用绝对路径）
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "..", "data", "2025-match_urls.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✓ 成功生成 {output_path}")
print(f"✓ 共提取 {len(match_urls)} 场比赛")
print(f"✓ 时间范围: {match_urls[0]['date']} 至 {match_urls[-1]['date']}")
