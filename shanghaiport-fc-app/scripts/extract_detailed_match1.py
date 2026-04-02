#!/usr/bin/env python3
"""
提取第一场比赛的详细数据
包括：主教练、队长、首发、替补、换人、详细统计
"""

import json
import re

def parse_scorebox(scorebox_text):
    """解析比赛基本信息"""
    lines = scorebox_text.split('\n')

    data = {
        'home_team': '',
        'home_score': 0,
        'home_manager': '',
        'home_captain': '',
        'away_team': '',
        'away_score': 0,
        'away_manager': '',
        'away_captain': '',
        'date': '',
        'competition': '',
        'attendance': 0,
        'venue': '',
        'goals': []
    }

    # 解析主队
    if len(lines) > 0:
        data['home_team'] = lines[0].strip()
    if len(lines) > 1 and lines[1].strip().isdigit():
        data['home_score'] = int(lines[1].strip())

    # 解析客队
    for i, line in enumerate(lines):
        if 'Wuhan Three Towns' in line or '武汉三镇' in line:
            data['away_team'] = line.strip()
            if i + 1 < len(lines) and lines[i + 1].strip().isdigit():
                data['away_score'] = int(lines[i + 1].strip())

    # 解析教练和队长
    for line in lines:
        if 'Manager:' in line:
            manager = line.split('Manager:')[1].strip()
            if not data['home_manager']:
                data['home_manager'] = manager
            else:
                data['away_manager'] = manager
        if 'Captain:' in line:
            captain = line.split('Captain:')[1].strip()
            if not data['home_captain']:
                data['home_captain'] = captain
            else:
                data['away_captain'] = captain

    # 解析日期和赛事
    for line in lines:
        if 'March' in line or '2024' in line:
            data['date'] = line.strip()
        if 'Super League' in line or '中超' in line:
            data['competition'] = line.strip()
        if 'Attendance:' in line:
            match = re.search(r'(\d[\d,]*)', line)
            if match:
                data['attendance'] = int(match.group(1).replace(',', ''))
        if 'Venue:' in line:
            data['venue'] = line.split('Venue:')[1].strip()

    # 解析进球
    goal_pattern = r'([A-Za-z\s]+)\s+·\s+(\d+\'|\d+\+\d+\')'
    for match in re.finditer(goal_pattern, scorebox_text):
        player = match.group(1).strip()
        minute = match.group(2).strip()
        data['goals'].append({'player': player, 'minute': minute})

    return data

def parse_lineups(lineups_text):
    """解析阵容信息"""
    data = {
        'home_starting': [],
        'home_subs': [],
        'away_starting': [],
        'away_subs': [],
        'substitutions': []
    }

    lines = lineups_text.split('\n')

    # 简化处理：查找球员名字（通常是带有号码的）
    current_team = None
    current_list = None

    for line in lines:
        # 检测球队名称
        if 'Shanghai Port' in line or '上海海港' in line:
            current_team = 'home'
        elif 'Wuhan Three Towns' in line or '武汉三镇' in line:
            current_team = 'away'

        # 检测首发或替补标记
        if 'Starting' in line or '首发' in line:
            current_list = 'starting'
        elif 'Substitutes' in line or '替补' in line:
            current_list = 'subs'

        # 提取球员（简化版：提取看起来像球员名字的行）
        # 这里需要根据实际页面结构调整

    return data

def parse_events(events_text):
    """解析比赛事件"""
    events = []
    lines = events_text.split('\n')

    for line in lines:
        # 解析换人
        if 'for' in line:
            parts = line.split('for')
            if len(parts) == 2:
                minute_match = re.search(r'(\d+\'|\d+\+\d+\')', line)
                if minute_match:
                    events.append({
                        'type': 'substitution',
                        'minute': minute_match.group(1),
                        'player_out': parts[1].strip(),
                        'player_in': parts[0].split()[-1].strip()
                    })

        # 解析进球
        if 'Assist:' in line or '·' in line:
            # 查找包含分钟数和球员的行
            pass

    return events

def parse_stats(stats_text):
    """解析详细统计数据"""
    stats = {}
    lines = stats_text.split('\n')

    # 定义要提取的统计项
    stat_items = [
        'Possession', 'Shots', 'Shots on Target', 'Saves',
        'Cards', 'Fouls', 'Corners', 'Crosses', 'Interceptions', 'Offsides'
    ]

    for item in stat_items:
        # 查找包含该统计项的行
        for i, line in enumerate(lines):
            if item in line:
                # 尝试提取数值
                # 这里需要根据实际格式调整
                pass

    return stats

def main():
    # 读取原始数据
    with open('data/match1_detailed_raw.json', 'r') as f:
        content = f.read()

    # 解析JSON
    raw_data = json.loads(json.loads(content))

    print('🔍 开始解析详细数据...\n')

    # 1. 解析比赛信息
    print('📋 比赛基本信息:')
    scorebox_data = parse_scorebox(raw_data['scorebox'])
    print(f'  主队: {scorebox_data["home_team"]}')
    print(f'  主队比分: {scorebox_data["home_score"]}')
    print(f'  主队教练: {scorebox_data["home_manager"]}')
    print(f'  主队队长: {scorebox_data["home_captain"]}')
    print(f'  客队: {scorebox_data["away_team"]}')
    print(f'  客队比分: {scorebox_data["away_score"]}')
    print(f'  客队教练: {scorebox_data["away_manager"]}')
    print(f'  客队队长: {scorebox_data["away_captain"]}')
    print(f'  日期: {scorebox_data["date"]}')
    print(f'  赛事: {scorebox_data["competition"]}')
    print(f'  观众: {scorebox_data["attendance"]:,}')
    print(f'  球场: {scorebox_data["venue"]}')
    print(f'  进球: {len(scorebox_data["goals"])} 个')

    # 2. 解析阵容
    if 'lineups' in raw_data and raw_data['lineups']:
        print('\n👥 阵容信息:')
        lineup_data = parse_lineups(raw_data['lineups'])
        # 这里可以添加更详细的解析

    # 3. 解析事件
    if 'events' in raw_data and raw_data['events']:
        print('\n⚽ 比赛事件:')
        events_data = parse_events(raw_data['events'])
        print(f'  检测到 {len(events_data)} 个事件')

    # 4. 解析统计
    if 'team_stats' in raw_data and raw_data['team_stats']:
        print('\n📊 统计数据:')
        stats_data = parse_stats(raw_data['team_stats'])
        # 这里可以添加更详细的解析

    print('\n✅ 数据解析完成')

if __name__ == '__main__':
    main()
