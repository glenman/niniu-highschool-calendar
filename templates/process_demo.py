#!/usr/bin/env python3
"""
演示：从 JSON 数据生成 Excel 报告
"""

import json
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from process_match_data import MatchDataProcessor

def main():
    print("=" * 60)
    print("足球比赛数据处理演示")
    print("=" * 60)
    print()

    # 加载示例数据
    data_file = "demo_match_data.json"
    print(f"📂 加载数据文件: {data_file}")

    with open(data_file, 'r', encoding='utf-8') as f:
        match_data = json.load(f)

    print("✅ 数据加载成功")
    print()

    # 显示比赛信息
    print("📋 比赛信息:")
    print(f"  日期: {match_data['match_info']['date']}")
    print(f"  时间: {match_data['match_info']['time']}")
    print(f"  赛事: {match_data['match_info']['competition']['name']}")
    print(f"  球场: {match_data['match_info']['venue']['name']}")
    print(f"  主队: {match_data['teams']['home']['name']} {match_data['teams']['home']['score']}")
    print(f"  客队: {match_data['teams']['away']['name']} {match_data['teams']['away']['score']}")
    print()

    # 初始化处理器
    processor = MatchDataProcessor()

    # 验证数据
    print("🔍 验证数据格式...")
    is_valid, errors = processor.validate_match_data(match_data)

    if is_valid:
        print("✅ 数据验证通过！")
        print()

        # 生成 Excel
        print("📊 生成 Excel 报告...")
        output_path = "../match_report_demo.xlsx"
        excel_file = processor.create_excel_report(match_data, output_path)

        print()
        print("=" * 60)
        print("✅ 处理完成！")
        print("=" * 60)
        print()
        print(f"📁 Excel 文件: {excel_file}")
        print()
        print("📊 Excel 包含以下工作表:")
        print("  1. 比赛信息 - 基本比赛数据")
        print("  2. 球员阵容 - 双方首发和替补")
        print("  3. 比赛事件 - 进球、换人、黄牌等")
        print("  4. 统计数据 - 控球率、射门等对比")
        print("  5. 球员统计 - 详细个人数据")
        print()

        # 显示统计摘要
        print("📈 数据统计:")
        print(f"  - 比赛事件: {len(match_data['events'])} 个")
        print(f"  - 主队球员: {len(match_data['teams']['home']['lineup'])} 首发 + {len(match_data['teams']['home']['substitutes'])} 替补")
        print(f"  - 客队球员: {len(match_data['teams']['away']['lineup'])} 首发 + {len(match_data['teams']['away']['substitutes'])} 替补")
        print(f"  - 球员详细统计: {len(match_data['player_stats']['home']) + len(match_data['player_stats']['away'])} 人")
        print()

        return 0
    else:
        print("❌ 数据验证失败:")
        for error in errors:
            print(f"  - {error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
