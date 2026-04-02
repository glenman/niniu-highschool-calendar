#!/usr/bin/env python3
"""
生成上海海港2026赛季赛程ICS文件（真实数据 + 详细球场信息）
"""
from datetime import datetime
import json

# 中超各队主场球场信息
STADIUMS = {
    "河南队": "郑州航海体育场",
    "青岛西海岸": "青岛西海岸大学城体育场",
    "大连英博": "大连体育中心体育场",
    "云南玉昆": "玉溪高原体育运动中心",
    "上海申花": "上海虹口足球场",
    "山东泰山": "济南奥体中心体育场",
    "重庆铜梁龙": "重庆铜梁龙体育场",
    "武汉三镇": "武汉体育中心体育场",
    "青岛海牛": "青岛青春足球场",
    "深圳新鹏城": "深圳大运中心体育场",
    "北京国安": "北京工人体育场",
    "浙江队": "杭州黄龙体育中心",
    "成都蓉城": "成都凤凰山体育公园",
    "天津津门虎": "天津泰达足球场",
    "沈阳城建": "沈阳奥林匹克体育中心"
}

def load_schedule():
    """从JSON文件加载赛程数据"""
    with open('data/2026-schedule.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_stadium(opponent_cn, venue):
    """获取比赛球场"""
    if venue == 'Home':
        return "上海浦东足球场"
    else:
        return STADIUMS.get(opponent_cn, f"{opponent_cn}主场")

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

        # 生成比赛标题（新格式）
        venue_text = "主场" if match['venue'] == 'Home' else "客场"
        summary = f"上海海港 vs {match['opponent_cn']}（{venue_text}）"

        # 生成描述
        description = f"中超联赛 2026赛季 第{match['match_number']}轮\\n"
        description += f"上海海港 {venue_text} vs {match['opponent_cn']}\\n"
        description += f"开球时间: {match['time']}"

        # 获取球场信息
        stadium = get_stadium(match['opponent_cn'], match['venue'])

        # 生成事件
        event = [
            "BEGIN:VEVENT",
            f"DTSTART;TZID=Asia/Shanghai:{dtstart_str}",
            f"DTEND;TZID=Asia/Shanghai:{dtend_str}",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"UID:{uid}@shanghaiport.com",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{stadium}",
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

    # 显示示例
    print("\n示例日历事件:")
    print(f"  标题: 上海海港 vs 云南玉昆（主场）")
    print(f"  地点: 上海浦东足球场")
    print(f"  标题: 上海海港 vs 山东泰山（客场）")
    print(f"  地点: 济南奥体中心体育场")

    return filename

if __name__ == "__main__":
    print("正在生成上海海港2026赛季日历（详细版本）...")
    schedule = load_schedule()
    generate_ics(schedule)
    print("\n✓ 完成！")
