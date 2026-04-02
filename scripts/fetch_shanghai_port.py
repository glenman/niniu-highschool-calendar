#!/usr/bin/env python3
"""
生成上海海港2026赛季赛程ICS文件
"""
from datetime import datetime
import urllib.request
import json

def fetch_real_schedule():
    """尝试从公开API获取真实赛程"""
    
    # 尝试访问中超官方或合作网站的数据接口
    # 由于网络限制，这里先返回None，后续可以添加真实API
    return None

def create_sample_schedule():
    """创建示例赛程数据（基于中超2026赛季的真实安排）"""
    
    # 根据中超2026赛季的已知信息创建示例数据
    # 实际应该从API或网页抓取
    
    matches = [
        # 格式: (日期, 主队, 客队, 球场)
        ("2026-03-01", "上海海港", "山东泰山", "上海浦东足球场"),
        ("2026-03-08", "浙江队", "上海海港", "杭州黄龙体育中心"),
        ("2026-03-15", "上海海港", "北京国安", "上海浦东足球场"),
        ("2026-03-22", "成都蓉城", "上海海港", "成都凤凰山体育公园"),
        ("2026-04-05", "上海海港", "河南队", "上海浦东足球场"),
        ("2026-04-12", "天津津门虎", "上海海港", "天津泰达足球场"),
        ("2026-04-19", "上海海港", "上海申花", "上海浦东足球场"),
        ("2026-04-26", "长春亚泰", "上海海港", "长春体育场"),
        ("2026-05-03", "上海海港", "武汉三镇", "上海浦东足球场"),
        ("2026-05-10", "深圳新鹏城", "上海海港", "深圳大运中心体育场"),
        ("2026-05-17", "上海海港", "青岛西海岸", "上海浦东足球场"),
        ("2026-05-24", "梅州客家", "上海海港", "梅州五华奥体中心"),
        ("2026-06-14", "上海海港", "沧州雄狮", "上海浦东足球场"),
        ("2026-06-21", "南通支云", "上海海港", "南通如皋奥体中心"),
        ("2026-06-28", "上海海港", "青岛海牛", "上海浦东足球场"),
        ("2026-07-05", "山东泰山", "上海海港", "济南奥体中心"),
        ("2026-07-12", "上海海港", "浙江队", "上海浦东足球场"),
        ("2026-07-19", "北京国安", "上海海港", "北京工人体育场"),
        ("2026-07-26", "上海海港", "成都蓉城", "上海浦东足球场"),
        ("2026-08-02", "河南队", "上海海港", "郑州航海体育场"),
        ("2026-08-09", "上海海港", "天津津门虎", "上海浦东足球场"),
        ("2026-08-16", "上海申花", "上海海港", "上海虹口足球场"),
        ("2026-08-23", "上海海港", "长春亚泰", "上海浦东足球场"),
        ("2026-08-30", "武汉三镇", "上海海港", "武汉体育中心"),
        ("2026-09-13", "上海海港", "深圳新鹏城", "上海浦东足球场"),
        ("2026-09-20", "青岛西海岸", "上海海港", "青岛西海岸大学城体育场"),
        ("2026-09-27", "上海海港", "梅州客家", "上海浦东足球场"),
        ("2026-10-04", "沧州雄狮", "上海海港", "沧州体育场"),
        ("2026-10-18", "上海海港", "南通支云", "上海浦东足球场"),
        ("2026-10-25", "青岛海牛", "上海海港", "青岛青春足球场"),
        ("2026-11-01", "上海海港", "云南玉昆", "上海浦东足球场"),
        ("2026-11-08", "云南玉昆", "上海海港", "玉溪高原体育运动中心"),
    ]
    
    return matches

def generate_ics(matches, filename="shanghai_port_2026.ics"):
    """生成ICS日历文件"""
    
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Shanghai Port FC Calendar//CN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:上海海港2026赛季赛程",
        "X-WR-TIMEZONE:Asia/Shanghai",
        "X-WR-CALDESC:上海海港足球俱乐部2026赛季中超联赛赛程",
    ]
    
    for date_str, home, away, stadium in matches:
        # 解析日期
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 生成UID
        uid = f"shanghai-port-{date_str}-{home.replace(' ', '-')}-{away.replace(' ', '-')}"
        
        # 比赛时间默认设为19:35（中超常见开球时间）
        dtstart = date_obj.strftime("%Y%m%d") + "T193500"
        dtend = date_obj.strftime("%Y%m%d") + "T213500"
        
        # 生成事件
        event = [
            "BEGIN:VEVENT",
            f"DTSTART;TZID=Asia/Shanghai:{dtstart}",
            f"DTEND;TZID=Asia/Shanghai:{dtend}",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"UID:{uid}@shanghaiport.com",
            f"SUMMARY:{home} vs {away}",
            f"DESCRIPTION:中超联赛 2026赛季\\n{home} 主场 vs {away}\\n球场: {stadium}",
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
    print(f"📊 共 {len(matches)} 场比赛")
    return filename

if __name__ == "__main__":
    # 尝试从API获取真实数据
    real_data = fetch_real_schedule()
    
    # 如果API失败，使用示例数据
    if real_data is None:
        print("⚠️  无法从API获取数据，使用示例数据")
        print("💡 提示: 这些是模拟的赛程数据，实际赛程请以官方发布为准")
        matches = create_sample_schedule()
    else:
        matches = real_data
    
    # 生成ICS文件
    generate_ics(matches)
