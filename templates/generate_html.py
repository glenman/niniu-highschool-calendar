#!/usr/bin/env python3
"""
从JSON数据生成HTML比赛报告
"""

import json
from datetime import datetime

def create_html_report(data, output_path="match_report_real.html"):
    """生成HTML可视化报告"""

    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>比赛报告 - {data["teams"]["home"]["name"]} vs {data["teams"]["away"]["name"]}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .score {{
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
        }}
        .teams {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            font-size: 1.5em;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .home-team {{
            color: #e74c3c;
        }}
        .away-team {{
            color: #3498db;
        }}
        .event-goal {{
            background-color: #d4edda;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 15px;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        .info-item {{
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .info-label {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏆 {data["match_info"]["competition"]["name"]} {data["match_info"]["competition"]["season"]}</h1>
        <div class="score">{data["teams"]["home"]["score"]} - {data["teams"]["away"]["score"]}</div>
        <div class="teams">
            <div class="home-team">{data["teams"]["home"]["name"]}</div>
            <div style="font-size: 0.8em; color: #ddd;">VS</div>
            <div class="away-team">{data["teams"]["away"]["name"]}</div>
        </div>
    </div>

    <div class="section">
        <h2>📋 比赛信息</h2>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">📅 日期</div>
                <div>{data["match_info"]["date"]}</div>
            </div>
            <div class="info-item">
                <div class="info-label">⏰ 时间</div>
                <div>{data["match_info"]["time"]}</div>
            </div>
            <div class="info-item">
                <div class="info-label">🏟️ 球场</div>
                <div>{data["match_info"]["venue"]["name"]}</div>
            </div>
            <div class="info-item">
                <div class="info-label">👥 观众</div>
                <div>{data["match_info"]["venue"]["attendance"]:,}人</div>
            </div>
            <div class="info-item">
                <div class="info-label">🏆 赛事</div>
                <div>{data["match_info"]["competition"]["name"]} {data["match_info"]["competition"]["round"]}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>📊 比赛统计</h2>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">控球率</div>
                <div class="stat-value">
                    <span class="home-team">{data["statistics"]["possession"]["home"]}%</span> - <span class="away-team">{data["statistics"]["possession"]["away"]}%</span>
                </div>
            </div>
            <div class="stat-box">
                <div class="stat-label">射门</div>
                <div class="stat-value">
                    <span class="home-team">{data["statistics"]["shots"]["home"]}</span> - <span class="away-team">{data["statistics"]["shots"]["away"]}</span>
                </div>
            </div>
            <div class="stat-box">
                <div class="stat-label">射正</div>
                <div class="stat-value">
                    <span class="home-team">{data["statistics"]["shots_on_target"]["home"]}</span> - <span class="away-team">{data["statistics"]["shots_on_target"]["away"]}</span>
                </div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>⚽ 比赛事件</h2>
        <table>
            <thead>
                <tr>
                    <th>时间</th>
                    <th>事件</th>
                    <th>球队</th>
                    <th>球员</th>
                </tr>
            </thead>
            <tbody>
'''

    # 添加事件
    for event in data["events"]:
        minute = event["minute"]
        if "minute_extra" in event:
            minute_str = f"{minute}'+{event['minute_extra']}'"
        else:
            minute_str = f"{minute}'"

        team_class = "home-team" if event["team"] == "home" else "away-team"
        team_name = data["teams"][event["team"]]["name"]

        html_template += f'''                <tr class="event-goal">
                    <td>{minute_str}</td>
                    <td>⚽ 进球</td>
                    <td class="{team_class}">{team_name}</td>
                    <td>{event["player"]}</td>
                </tr>
'''

    html_template += '''            </tbody>
        </table>
    </div>

    <div style="text-align: center; margin-top: 40px; padding: 20px; background: white; border-radius: 10px;">
        <p style="color: #6c757d; margin: 0;">
            📊 报告生成时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ''' | 数据来源: FBref
        </p>
    </div>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ HTML报告已生成: {output_path}")
    return output_path

if __name__ == "__main__":
    with open('fbref_real_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    create_html_report(data, '../match_report_real.html')
