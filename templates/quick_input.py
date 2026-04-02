#!/usr/bin/env python3
"""
交互式比赛数据收集工具
快速收集关键比赛数据并生成报告
"""

import json
from datetime import datetime

def collect_match_data():
    """交互式收集比赛数据"""
    print("=" * 60)
    print("足球比赛数据收集工具")
    print("=" * 60)
    print()

    match_data = {
        "match_info": {},
        "teams": {"home": {}, "away": {}},
        "events": [],
        "statistics": {},
        "metadata": {
            "source": "手动输入",
            "scraped_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    }

    # 1. 比赛基本信息
    print("📋 请输入比赛基本信息:")
    print("-" * 60)

    match_data["match_info"]["date"] = input("比赛日期 (YYYY-MM-DD): ").strip() or "2024-03-01"
    match_data["match_info"]["time"] = input("比赛时间 (HH:MM): ").strip() or "19:35"

    competition = input("赛事名称 (如：中超联赛): ").strip() or "Chinese Super League"
    match_data["match_info"]["competition"] = {
        "name": competition,
        "season": input("赛季 (如：2024): ").strip() or "2024",
        "round": input("轮次 (如：第1轮): ").strip() or "Round 1"
    }

    venue_name = input("球场名称: ").strip() or "Unknown Stadium"
    match_data["match_info"]["venue"] = {
        "name": venue_name,
        "city": input("城市: ").strip() or "Unknown",
        "attendance": int(input("观众人数 (数字): ").strip() or "0")
    }

    referee = input("主裁判: ").strip() or "Unknown"
    match_data["match_info"]["referee"] = {"name": referee}

    print()

    # 2. 球队信息
    print("👥 请输入球队信息:")
    print("-" * 60)

    # 主队
    home_team = input("主队名称: ").strip() or "Home Team"
    home_score = int(input(f"{home_team} 进球数: ").strip() or "0")
    match_data["teams"]["home"] = {
        "name": home_team,
        "score": home_score,
        "score_ht": int(input(f"{home_team} 半场比分: ").strip() or "0"),
        "formation": input(f"{home_team} 阵型 (如4-3-3): ").strip() or "4-4-2",
        "lineup": [],
        "substitutes": []
    }

    # 客队
    away_team = input("客队名称: ").strip() or "Away Team"
    away_score = int(input(f"{away_team} 进球数: ").strip() or "0")
    match_data["teams"]["away"] = {
        "name": away_team,
        "score": away_score,
        "score_ht": int(input(f"{away_team} 半场比分: ").strip() or "0"),
        "formation": input(f"{away_team} 阵型 (如4-3-3): ").strip() or "4-4-2",
        "lineup": [],
        "substitutes": []
    }

    print()

    # 3. 比赛事件
    print("⚽ 请输入比赛事件 (进球、黄牌、换人等):")
    print("-" * 60)
    print("事件类型: goal(进球), yellow_card(黄牌), red_card(红牌), substitution(换人)")
    print("输入 'done' 完成事件输入")
    print()

    event_count = 0
    while True:
        event_type = input(f"事件{event_count+1} 类型 (或输入 'done'): ").strip().lower()

        if event_type == 'done' or event_type == '':
            break

        if event_type in ['goal', 'yellow_card', 'red_card', 'substitution']:
            event = {
                "minute": int(input("  时间 (分钟): ").strip() or "0"),
                "type": event_type,
                "team": input("  球队 (home/away): ").strip(),
                "player": input("  球员: ").strip()
            }

            if event_type == 'goal':
                event["player2"] = input("  助攻球员 (可选): ").strip() or ""
                event["description"] = input("  描述: ").strip() or ""
            elif event_type == 'substitution':
                event["player_out"] = event["player"]
                event["player_in"] = input("  上场球员: ").strip()
                event["player"] = ""

            match_data["events"].append(event)
            event_count += 1
            print(f"  ✅ 已添加事件 {event_count}")
            print()

    print()

    # 4. 统计数据
    print("📊 请输入统计数据 (双方对比):")
    print("-" * 60)

    stats_items = [
        ("possession", "控球率 (%)"),
        ("shots", "射门次数"),
        ("shots_on_target", "射正次数"),
        ("corners", "角球"),
        ("fouls", "犯规"),
        ("yellow_cards", "黄牌"),
        ("red_cards", "红牌")
    ]

    for stat_key, stat_name in stats_items:
        home_val = input(f"{stat_name} - {home_team}: ").strip()
        away_val = input(f"{stat_name} - {away_team}: ").strip()

        if home_val and away_val:
            match_data["statistics"][stat_key] = {
                "home": float(home_val) if '.' in home_val else int(home_val),
                "away": float(away_val) if '.' in away_val else int(away_val)
            }

    print()

    # 5. 保存数据
    print("=" * 60)
    print("✅ 数据收集完成！")
    print("=" * 60)
    print()

    filename = f"match_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(match_data, f, ensure_ascii=False, indent=2)

    print(f"📁 数据已保存到: {filename}")
    print()

    # 显示摘要
    print("📋 比赛摘要:")
    print(f"  {home_team} {home_score} - {away_score} {away_team}")
    print(f"  日期: {match_data['match_info']['date']}")
    print(f"  事件: {len(match_data['events'])} 个")
    print(f"  统计: {len(match_data['statistics'])} 项")
    print()

    return filename

if __name__ == "__main__":
    try:
        filename = collect_match_data()
        print(f"✅ 完成！数据文件: {filename}")
        print()
        print("下一步:")
        print(f"  1. 查看数据: cat {filename}")
        print(f"  2. 生成Excel: python3 process_match_data.py {filename}")
    except KeyboardInterrupt:
        print("\n\n❌ 已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
