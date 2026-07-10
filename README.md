# 妞妞高中衔接补课日程 📚

## 项目概述

妞妞 2026 年 7 月高中衔接补课日程网站，提供月度日历视图和每周详细课表，支持手机日历导入。

> **祝妞妞高中衔接顺利！加油！💪**

---

## 在线查看

🌐 [https://glenman.github.io/niniu-highschool-calendar/](https://glenman.github.io/niniu-highschool-calendar/)

---

## 课程安排

| 科目 | 时间 | 频次 | 颜色标识 |
|------|------|------|----------|
| 📐 数学 | 13:00–15:00 | 周一 / 三 / 五 | 🔴 红色 |
| 📖 语文 | 09:00–11:00 | 周三 / 五 | 🔵 蓝色 |
| ⚡ 物理 | 16:00–18:00 | 周二 / 四 / 六 | 🟠 橙色 |
| 🧪 化学 | 19:15–21:15 | 周二 / 四 / 六 | 🟣 紫色 |

### 数据统计

- **补课周期**：2026 年 7 月 1 日 – 7 月 25 日
- **总上课天数**：20 天
- **涵盖科目**：4 科（数学、语文、物理、化学）
- **日均课时**：约 2–4 节

---

## 功能特性

### 📅 月度日历视图
- 以日历形式展示整个 7 月的补课安排
- 每天用颜色标记对应科目，一目了然
- 无课的日子自动折叠显示

### 📋 每周详细课表
- 按周组织课程，清晰展示每日多节课安排
- 标注具体时间段和科目信息
- 周末课程特别突出显示

### 📱 手机日历导入
- 提供 `.ics` 文件，可直接导入手机日历
- 支持 iOS / Android / Google Calendar / Outlook
- 下载链接：[niu_niu_tutoring.ics](niu_niu_tutoring.ics)

### 🎨 响应式设计
- 移动端优先的界面设计
- 适配各种屏幕尺寸
- 流畅的交互体验

---

## 日历导入方式

### iPhone / iPad
1. 下载 [niu_niu_tutoring.ics](niu_niu_tutoring.ics)
2. 通过 AirDrop 或邮件发送到设备
3. 点击文件，选择"添加到日历"

### Android
1. 下载 [niu_niu_tutoring.ics](niu_niu_tutoring.ics)
2. 用文件管理器打开
3. 选择导入到 Google 日历或其他日历应用

### 电脑
1. 下载 [niu_niu_tutoring.ics](niu_niu_tutoring.ics)
2. 双击文件，系统会自动用默认日历应用打开并导入

---

## 文件结构

```
niu-highschool-calendar/
├── index.html              # 主页面（含日历视图 + 每周课表）
├── schedule.json           # 课程数据（20 天 × 4 科目）
├── niu_niu_tutoring.ics    # 日历导入文件
├── _headers                # GitHub Pages HTTP 头配置
└── README.md               # 本文件
```

---

## 技术栈

| 技术 | 说明 |
|------|------|
| **HTML / CSS / JavaScript** | 纯前端实现，无需任何框架 |
| **GitHub Pages** | 静态托管，自动 HTTPS |
| **ICS 格式** | 标准日历交换格式 |
| **JSON** | 课程数据源 |

---

## 本地运行

```bash
cd niniu-highschool-calendar
python3 -m http.server 8080
# 浏览器访问 http://localhost:8080
```

---

## 数据修改

如需修改课程安排，编辑 `schedule.json` 即可：

```json
{
  "title": "妞妞高中衔接补课日程",
  "period": "2026年7月1日 - 7月31日",
  "total_days": 20,
  "subjects": ["数学", "语文", "物理", "化学"],
  "schedule": [
    {
      "date": "2026-07-02",
      "weekday": "周四",
      "events": [
        {
          "subject": "物理",
          "time": "16:00-18:00",
          "description": "高中物理衔接"
        }
      ]
    }
  ]
}
```

修改后提交推送到 GitHub，GitHub Pages 会自动更新。

---

## License

本项目仅供个人使用，无开源许可证。
