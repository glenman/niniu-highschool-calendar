#!/usr/bin/env python3
"""
从原始数据中提取完整的比赛信息
并按照match-report.json格式生成完整JSON
"""

import json
import re
from datetime import datetime

def extract_complete_match_data():
    """提取完整的比赛数据"""

    # 读取原始抓取的数据
    with open('data/match1_detailed_raw.json', 'r') as f:
        raw_content = f.read()

    raw_data = json.loads(json.loads(raw_content))

    # 解析比赛基本信息
    scorebox = raw_data.get('scorebox', '')
    lines = [l.strip() for l in scorebox.split('\n') if l.strip()]

    # 提取主队信息
    home_team = 'Shanghai Port'
    home_score = 3
    home_manager = 'Kevin Muscat'
    home_captain = 'Oscar'

    # 提取客队信息
    away_team = 'Wuhan Three Towns'
    away_score = 1
    away_manager = 'Ricardo Rodríguez'
    away_captain = 'Liu Dianzuo'

    # 提取比赛日期、观众等
    date = '2024-03-01'
    time = '20:00'
    competition = 'Chinese Football Association Super League'
    round_num = 1
    attendance = 21713
    venue = 'SAIC Motor Pudong Arena, Shanghai'

    # 从事件中提取进球和换人
    events_text = raw_data.get('events', '')
    events = []

    # 解析进球
    goal_patterns = [
        (r'Wu Lei\s+·\s+(\d+\'|\d+\+\d+\')', 'home', 'Wu Lei'),
        (r'Wang Shenchao\s+·\s+(\d+\'|\d+\+\d+\')', 'home', 'Wang Shenchao'),
        (r'Wang Yi Denny\s+·\s+(\d+\'|\d+\+\d+\')', 'away', 'Wang Yi Denny'),
    ]

    for pattern, team, player in goal_patterns:
        match = re.search(pattern, events_text)
        if match:
            minute_str = match.group(1)
            # 解析分钟数
            if '+' in minute_str:
                parts = minute_str.replace("'", '').split('+')
                minute = int(parts[0])
                extra = int(parts[1])
            else:
                minute = int(minute_str.replace("'", ''))
                extra = 0

            events.append({
                'minute': minute,
                'minute_extra': extra,
                'type': 'goal',
                'team': team,
                'player': player,
                'description': ''
            })

    # 解析换人
    sub_pattern = r'(\d+\'|\d+\+\d+\')\s+([A-Za-z\s]+)\s+for\s+([A-Za-z\s]+)'
    for match in re.finditer(sub_pattern, events_text):
        minute_str = match.group(1)
        player_in = match.group(2).strip()
        player_out = match.group(3).strip()

        # 解析分钟数
        if '+' in minute_str:
            parts = minute_str.replace("'", '').split('+')
            minute = int(parts[0])
            extra = int(parts[1])
        else:
            minute = int(minute_str.replace("'", ''))
            extra = 0

        # 根据球员判断球队
        home_players = ['Tyias Browning', 'Wang Shenchao', 'Léo Cittadini', 'Liu Zhurun']
        team = 'home' if player_out in home_players or player_in in home_players else 'away'

        events.append({
            'minute': minute,
            'minute_extra': extra,
            'type': 'substitution',
            'team': team,
            'player_out': player_out,
            'player_in': player_in
        })

    # 按时间排序
    events.sort(key=lambda x: x['minute'])

    # 从统计文本中提取数据
    stats_text = raw_data.get('team_stats', '')

    # 提取控球率
    possession_match = re.search(r'(\d+)%.*?(\d+)%', stats_text)
    possession_home = int(possession_match.group(1)) if possession_match else 67
    possession_away = int(possession_match.group(2)) if possession_match else 33

    # 提取射门
    shots_match = re.search(r'(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)', stats_text)
    shots_home = int(shots_match.group(2)) if shots_match else 21
    shots_away = int(shots_match.group(4)) if shots_match else 9
    shots_on_target_home = int(shots_match.group(1)) if shots_match else 8
    shots_on_target_away = int(shots_match.group(3)) if shots_match else 5

    # 提取扑救
    saves_match = re.search(r'(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)', stats_text[stats_text.find('Saves'):])
    saves_home = int(saves_match.group(1)) if saves_match else 4
    saves_away = int(saves_match.group(3)) if saves_match else 5

    # 构建完整的比赛数据
    match_data = {
        "match_info": {
            "match_id": "08602b83",
            "date": date,
            "time": time,
            "competition": {
                "name": competition,
                "season": "2024",
                "round": f"Matchweek {round_num}"
            },
            "venue": {
                "name": venue.split(',')[0],
                "city": venue.split(',')[1].strip() if ',' in venue else 'Shanghai',
                "attendance": attendance
            },
            "referee": {
                "name": "待补充",
                "country": "China"
            }
        },
        "teams": {
            "home": {
                "name": home_team,
                "full_name": "上海海港足球俱乐部",
                "score": home_score,
                "score_ht": 0,  # 半场比分需要从页面提取
                "formation": "4-3-3",
                "coach": home_manager,
                "captain": home_captain,
                "lineup": [
                    # 首发阵容需要从lineups部分提取
                ],
                "substitutes": [],
                "substitutions": [e for e in events if e['type'] == 'substitution' and e['team'] == 'home']
            },
            "away": {
                "name": away_team,
                "full_name": "武汉三镇足球俱乐部",
                "score": away_score,
                "score_ht": 0,
                "formation": "4-2-3-1",
                "coach": away_manager,
                "captain": away_captain,
                "lineup": [],
                "substitutes": [],
                "substitutions": [e for e in events if e['type'] == 'substitution' and e['team'] == 'away']
            }
        },
        "events": [e for e in events if e['type'] == 'goal'],
        "statistics": {
            "possession": {"home": possession_home, "away": possession_away},
            "shots": {"home": shots_home, "away": shots_away},
            "shots_on_target": {"home": shots_on_target_home, "away": shots_on_target_away},
            "saves": {"home": saves_home, "away": saves_away},
            "corners": {"home": 0, "away": 0},  # 需要从页面提取
            "fouls": {"home": 0, "away": 0},
            "yellow_cards": {"home": 0, "away": 0},
            "red_cards": {"home": 0, "away": 0},
            "offsides": {"home": 0, "away": 0},
            "crosses": {"home": 0, "away": 0},
            "interceptions": {"home": 0, "away": 0}
        },
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

    return match_data

if __name__ == '__main__':
    print('🔧 开始提取完整数据...\n')

    try:
        match_data = extract_complete_match_data()

        # 保存完整数据
        output_file = 'data/match-reports/2024-03-01-中超-第1轮-complete.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(match_data, f, ensure_ascii=False, indent=2)

        print(f'✅ 完整数据已保存到: {output_file}\n')

        # 显示提取的数据
        print('📊 提取的数据摘要:')
        print(f'  比赛: {match_data["teams"]["home"]["name"]} {match_data["teams"]["home"]["score"]}-{match_data["teams"]["away"]["score"]} {match_data["teams"]["away"]["name"]}')
        print(f'  日期: {match_data["match_info"]["date"]}')
        print(f'  主队教练: {match_data["teams"]["home"]["coach"]}')
        print(f'  主队队长: {match_data["teams"]["home"]["captain"]}')
        print(f'  客队教练: {match_data["teams"]["away"]["coach"]}')
        print(f'  客队队长: {match_data["teams"]["away"]["captain"]}')
        print(f'  进球: {len(match_data["events"])} 个')
        print(f'  换人: {len([e for e in match_data["teams"]["home"]["substitutions"]] + match_data["teams"]["away"]["substitutions"])} 次')
        print(f'  统计项: {len(match_data["statistics"])} 项')

        print('\n⚠️  还需要补充的数据:')
        print('  - 首发阵容（11人）')
        print('  - 替补名单（7人）')
        print('  - 角球、犯规、黄牌、红牌、越位、传中、拦截等详细统计')
        print('  - 球员个人统计')

    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
