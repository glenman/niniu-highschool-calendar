# 妞妞高中衔接补课日程 📚

## 项目概述

妞妞2026年7月高中衔接补课日程网站，提供月度日历视图和每周详细课表。

## 课程安排

| 科目 | 时间 | 频次 |
|------|------|------|
| 📐 数学 | 13:00-15:00 | 周一/三/五 |
| 📖 语文 | 09:00-11:00 | 周三/五 |
| ⚡ 物理 | 16:00-18:00 | 周二/四/六 |
| 🧪 化学 | 19:15-21:15 | 周二/四/六 |

## 在线查看

🌐 **GitHub Pages**: https://glenman.github.io/niniu-highschool-calendar/

## 日历导入

📱 下载 ICS 文件导入手机日历：[niu_niu_tutoring.ics](niu_niu_tutoring.ics)

## 本地运行

```bash
cd niniu-highschool-calendar
python3 -m http.server 8080
# 访问 http://localhost:8080
```

## 文件结构

```
niu-highschool-calendar/
├── index.html          # 主页面（含日历视图）
├── schedule.json       # 课程数据
├── niu_niu_tutoring.ics # 日历导入文件
└── README.md           # 本文件
```

## 技术栈

- 纯 HTML/CSS/JavaScript，无需框架
- GitHub Pages 托管

---

祝妞妞高中衔接顺利！加油！💪
