#!/usr/bin/env python3
"""
快速数据粘贴工具
从 FBref 网页直接复制粘贴文本数据
"""

import json
from datetime import datetime
import re

def parse_pasted_data():
    """解析粘贴的文本数据"""
    print("=" * 60)
    print("FBref 数据快速提取工具")
    print("=" * 60)
    print()
    print("📝 请从 FBref 页面复制以下内容（可以直接粘贴多行）:")
    print()
    print("示例格式:")
    print("-" * 60)
    print("Shanghai Port 3-1 Wuhan Three Towns")
    print("Friday, March 1, 2024")
    print("19:35 CST")
    print("Pudong Football Stadium")
    print("Attendance: 28,500")
    print("Referee: Ma Ning")
    print("-" * 60)
    print()

    print("请粘贴比赛信息（输入空行结束）:")
    print("-" * 60)

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line.strip())

    print()
    print("=" * 60)
    print("正在解析数据...")
    print("=" * 60)

    # 解析数据
    data = {
        "match_info": {
            "date": "",
            "time": "",
            "competition": {"name": "Chinese Super League", "season": "2024"},
            "venue": {"name": "", "city": "", "attendance": 0},
            "referee": {"name": ""}
        },
        "teams": {
            "home": {"name": "", "score": 0, "lineup": [], "substitutes": []},
            "away": {"name": "", "score": 0, "lineup": [], "substitutes": []}
        },
        "events": [],
        "statistics": {},
        "metadata": {
            "source": "FBref (手动复制)",
            "scraped_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    }

    # 解析文本
    text = "\n".join(lines)

    # 提取比分
    score_match = re.search(r'(.+?)\s+(\d+)-(\d+)\s+(.+)', text)
    if score_match:
        data["teams"]["home"]["name"] = score_match.group(1).strip()
        data["teams"]["home"]["score"] = int(score_match.group(2))
        data["teams"]["away"]["score"] = int(score_match.group(3))
        data["teams"]["away"]["name"] = score_match.group(4).strip()

    # 提取日期
    date_match = re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(.+?),\s+(\d{4})', text)
    if date_match:
        data["match_info"]["date"] = f"{date_match.group(3)}-{date_match.group(2)}"

    # 提取时间
    time_match = re.search(r'(\d{1,2}:\d{2})', text)
    if time_match:
        data["match_info"]["time"] = time_match.group(1)

    # 提取球场
    if "Stadium" in text:
        stadium_match = re.search(r'([A-Za-z\s]+Stadium)', text)
        if stadium_match:
            data["match_info"]["venue"]["name"] = stadium_match.group(1)

    # 提取观众人数
    attendance_match = re.search(r'Attendance:\s*([\d,]+)', text)
    if attendance_match:
        data["match_info"]["venue"]["attendance"] = int(attendance_match.group(1).replace(",", ""))

    # 提取裁判
    referee_match = re.search(r'Referee:\s*(.+?)(?:\n|$)', text)
    if referee_match:
        data["match_info"]["referee"]["name"] = referee_match.group(1).strip()

    print()
    print("✅ 解析完成！")
    print()
    print("📋 提取的信息:")
    print(f"  比赛: {data['teams']['home']['name']} {data['teams']['home']['score']}-{data['teams']['away']['score']} {data['teams']['away']['name']}")
    print(f"  日期: {data['match_info']['date']}")
    print(f"  时间: {data['match_info']['time']}")
    print(f"  球场: {data['match_info']['venue']['name']}")
    print(f"  观众: {data['match_info']['venue']['attendance']}")
    print(f"  裁判: {data['match_info']['referee']['name']}")
    print()

    # 保存
    filename = f"match_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"📁 数据已保存到: {filename}")
    print()

    return filename

if __name__ == "__main__":
    try:
        filename = parse_pasted_data()
        print("✅ 完成！")
        print()
        print("下一步:")
        print(f"  python3 process_match_data.py {filename}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
