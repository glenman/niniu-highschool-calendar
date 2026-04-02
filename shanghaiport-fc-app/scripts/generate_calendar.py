#!/usr/bin/env python3
"""
生成上海海港2026赛季赛程ICS文件（真实数据）
"""
from datetime import datetime
import json

def load_schedule():
    """从JSON文件加载赛程数据"""
    with open('data/2026-schedule.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_ics(schedule_data, filename="data/2026-calendar.ics"):
    """生成ICS日历文件"""

    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Shanghai Port FC Calendar//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:上海海港2026赛季赛程",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "X-WR-CALDESC:上海海港足球俱乐部2026赛季中超联赛赛程（真实数据）",
    ]

    for match in schedule_data['matches']:
        # 解析日期和时间
        date_str = match['date']
        time_str = match.get('time', '19:35')

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        hour, minute = map(int, time_str.split(':'))

        # 生成UID
        uid = f"shanghai-port-2026-{date_str}-match{match['match_number']}"

        # 生成时间戳
        dtstart = date_obj.replace(hour=hour, minute=minute)
        dtend = date_obj.replace(hour=hour+2, minute=minute)

        dtstart_str = dtstart.strftime("%Y%m%dT%H%M00")
        dtend_str = dtend.strftime("%Y%m%dT%H%M00")

        # 生成比赛标题
        venue_text = "主场" if match['venue'] == 'Home' else "客场"
        venue_emoji = "🏟️" if match['venue'] == 'Home' else "✈️"

        summary = f"{venue_emoji} {match['opponent_cn']} ({venue_text})"

        # 生成描述
        description = f"中超联赛 2026赛季 第{match['match_number']}轮\\n"
        description += f"上海海港 {venue_text} vs {match['opponent_cn']}\\n"
        description += f"开球时间: {match['time']}"

        # 主场比赛的地点
        location = "上海浦东足球场" if match['venue'] == 'Home' else f"{match['opponent_cn']}主场"

        # 生成事件
        event = [
            "BEGIN:VEVENT",
            f"DTSTART;TZID=Asia/Shanghai:{dtstart_str}",
            f"DTEND;TZID=Asia/Shanghai:{dtend_str}",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"UID:{uid}@shanghaiport.com",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{location}",
            "STATUS:CONFIRMED",
            "END:VEVENT",
        ]

        ics_content.extend(event)

    ics_content.append("END:VCALENDAR")

    # 写入文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(ics_content))

    print(f"✅ ICS文件已生成: {filename}")
    print(f"📊 共 {len(schedule_data['matches'])} 场比赛")
    print(f"🏟️ 主场: {schedule_data['statistics']['home_matches']} 场")
    print(f"✈️ 客场: {schedule_data['statistics']['away_matches']} 场")

    return filename

if __name__ == "__main__":
    print("正在生成上海海港2026赛季日历...")
    schedule = load_schedule()
    generate_ics(schedule)
    print("\n✓ 完成！")
