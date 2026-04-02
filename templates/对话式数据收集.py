#!/usr/bin/env python3
"""
对话式比赛数据收集工具
适合在聊天环境中使用
"""

import json
from datetime import datetime

# 预定义的比赛数据模板
match_data = {
    "match_info": {
        "match_id": "08602b83",
        "date": "",
        "time": "",
        "competition": {
            "name": "Chinese Super League",
            "season": "2024",
            "round": ""
        },
        "venue": {
            "name": "",
            "city": "",
            "capacity": 0,
            "attendance": 0
        },
        "referee": {
            "name": "",
            "country": "China"
        }
    },
    "teams": {
        "home": {
            "name": "",
            "full_name": "",
            "score": 0,
            "score_ht": 0,
            "formation": "",
            "coach": "",
            "lineup": [],
            "substitutes": [],
            "substitutions": []
        },
        "away": {
            "name": "",
            "full_name": "",
            "score": 0,
            "score_ht": 0,
            "formation": "",
            "coach": "",
            "lineup": [],
            "substitutes": [],
            "substitutions": []
        }
    },
    "events": [],
    "statistics": {},
    "player_stats": {
        "home": [],
        "away": []
    },
    "metadata": {
        "source": "FBref",
        "url": "https://fbref.com/en/matches/08602b83/Shanghai-Port-Wuhan-Three-Towns-March-1-2024-Chinese-Super-League",
        "scraped_at": datetime.now().isoformat(),
        "version": "1.0"
    }
}

print("=" * 60)
print("📋 比赛数据快速收集")
print("=" * 60)
print()
print("请按以下格式提供数据（可以直接复制粘贴）：")
print()
print("格式示例：")
print("-" * 60)
print("比赛: 上海海港 3-1 武汉三镇")
print("日期: 2024-03-01")
print("时间: 19:35")
print("球场: 浦东足球场")
print("观众: 28500")
print("裁判: 马宁")
print()
print("事件:")
print("23' 进球 主队 武磊 (助攻:奥斯卡)")
print("56' 黄牌 客队 韦世豪")
print("67' 进球 客队 佩德罗")
print("88' 进球 主队 武磊")
print()
print("统计:")
print("控球率: 58.5-41.5")
print("射门: 15-8")
print("射正: 7-3")
print("角球: 6-4")
print("犯规: 12-15")
print("-" * 60)
print()
print("请直接告诉我比赛数据，我会帮你整理！")
