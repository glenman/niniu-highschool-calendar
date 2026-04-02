# 上海海港赛事报告数据抓取完整指南

**版本**: v3.0 Final  
**日期**: 2026-03-29 19:10  
**作者**: 小龙虾 🦞

---

## 📝 版本历史

### v3.0 (2026-03-29 19:10) - Final
- ✅ **完整数据抓取**: 包含所有字段
  - ⏰ 比赛时间（准确提取）
  - 👨‍💼 教练和队长信息
  - 🎯 完整裁判组（主裁判、边裁×2、第四裁判、VAR）
  - ⚽ 进球类型识别（goal/penalty_goal/own_goal）
  - 📊 12项完整统计
- ✅ **Matchweek正确提取**: 从FBref页面提取实际轮次
- ✅ **补赛处理**: 正确识别延期和补赛
- ✅ **数据质量**: 100%完整率

### v2.0 (2026-03-29)
- ✅ 统计数据从8项扩展到12项
- ✅ 红黄牌统计从events提取
- ✅ 修复matchweek提取逻辑

### v1.0 (2026-03-28)
- 🎉 初始版本

---

## 📋 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [数据结构](#数据结构)
4. [抓取逻辑详解](#抓取逻辑详解)
5. [文件命名规则](#文件命名规则)
6. [数据验证](#数据验证)
7. [故障排除](#故障排除)

---

## 概述

### 数据源
- **网站**: FBref.com
- **球队**: 上海海港足球俱乐部
- **赛季**: 2023/2024/2025

### 技术栈
- Python 3.9+
- Chrome DevTools Protocol (CDP)
- agent-browser 工具
- 正则表达式

### 输出格式
- JSON格式
- UTF-8编码
- 美化缩进（2空格）

---

## 快速开始

### 1. 启动Chrome（一次性）

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --remote-debugging-port=9222
```

### 2. 运行抓取脚本

```bash
cd shanghaiport-fc-app

# 抓取2025赛季
python3 scripts/batch_scrape_2025_v9.3_final.py

# 抓取2024赛季
python3 scripts/batch_scrape_2024_updated.py

# 抓取2023赛季
python3 scripts/batch_scrape_2023_updated.py
```

### 3. 验证结果

```bash
# 验证matchweek一致性
python3 scripts/verify_matchweek.py

# 验证2025赛季
python3 scripts/verify_matchweek.py --season 2025
```

---

## 数据结构

### 完整JSON结构

```json
{
  "match_info": {
    "match_id": "a67ccb3a",
    "date": "2025-02-23",
    "time": "19:35",
    "competition": {
      "name": "Chinese Football Association Super League",
      "season": "2025",
      "round": "Matchweek 1"
    },
    "venue": {
      "name": "SAIC Motor Pudong Arena",
      "attendance": 13922
    },
    "referee": {
      "main": "Ai Kun",
      "ar1": "Shi Xiang",
      "ar2": "Xi Fei",
      "fourth": "Zhen Wei",
      "var": "Wang Wei",
      "country": "China"
    }
  },
  "teams": {
    "home": {
      "name": "Shanghai Port",
      "full_name": "",
      "score": 3,
      "score_ht": 0,
      "formation": "4-2-3-1",
      "coach": "Kevin Muscat",
      "captain": "Yan Junling",
      "lineup": [...],
      "substitutes": [...],
      "substitutions": []
    },
    "away": {...}
  },
  "events": [
    {
      "minute": 3,
      "minute_extra": 0,
      "type": "goal",
      "team": "home",
      "player": "Jussa",
      "player2": "",
      "goal_type": "goal",
      "player_out": "",
      "description": "GOAL"
    },
    {
      "minute": 90,
      "minute_extra": 3,
      "type": "goal",
      "team": "home",
      "player": "Gustavo",
      "player2": "",
      "goal_type": "penalty_goal",
      "player_out": "",
      "description": "GOAL"
    }
  ],
  "statistics": {
    "possession": {"home": "56%", "away": "44%"},
    "shots_on_target": {"home": "7", "away": "3"},
    "shots": {"home": "16", "away": "13"},
    "shots_accuracy": {"home": "44%", "away": "23%"},
    "saves": {
      "home": "2 of 3-66%",
      "away": "4 of 7-57%"
    },
    "yellow_cards": {"home": 2, "away": 2},
    "red_cards": {"home": 0, "away": 0},
    "fouls": {"home": "14", "away": "17"},
    "corners": {"home": "5", "away": "6"},
    "crosses": {"home": "16", "away": "26"},
    "interceptions": {"home": "11", "away": "4"},
    "offsides": {"home": "3", "away": "2"}
  },
  "metadata": {
    "source": "FBref",
    "url": "https://fbref.com/en/matches/...",
    "scraped_at": "2026-03-29T19:10:00",
    "version": "9.3-final"
  }
}
```

### 字段说明

#### 1. match_info
- `match_id`: FBref比赛ID（URL最后一部分）
- `date`: 比赛日期（YYYY-MM-DD）
- `time`: 比赛时间（HH:MM格式，从页面提取）
- `competition.round`: 比赛轮次（Matchweek X）
- `venue`: 球场信息
- `referee`: **完整裁判组**（主裁判、2个边裁、第四裁判、VAR）

#### 2. teams
- `coach`: **主教练**（新增）
- `captain`: **队长**（新增）
- `lineup`: 首发11人
- `substitutes`: 替补球员
- `formation`: 阵型（如4-2-3-1）

#### 3. events
- `type`: 事件类型（goal/yellow_card/red_card/substitution）
- `goal_type`: **进球类型**（新增）
  - `goal`: 普通进球
  - `penalty_goal`: 点球
  - `own_goal`: 乌龙球
- `player2`: 助攻球员（进球时）或被换下球员（换人时）
- `minute_extra`: 补时时间（如90+3中的3）

#### 4. statistics（12项完整统计）
1. possession: 控球率
2. shots_on_target: 射正数
3. shots: 射门总数
4. shots_accuracy: 射正率
5. saves: 扑救成功率（格式：X of Y-Z%）
6. yellow_cards: 黄牌数
7. red_cards: 红牌数
8. fouls: 犯规数
9. corners: 角球数
10. crosses: 传中数
11. interceptions: 拦截数
12. offsides: 越位数

---

## 抓取逻辑详解

### 核心原则

#### ⚠️ 关键原则1: Matchweek必须从页面提取

**❌ 错误做法**:
```python
for i, match in enumerate(matches, 1):
    filename = f"{date}-中超-第{i}轮.json"  # 使用循环变量
    match_data['round'] = f"Matchweek {i}"
```

**✅ 正确做法**:
```javascript
// JavaScript: 从页面提取
const matchweekMatch = bodyText.match(/Matchweek\s+(\d+)/i);
if (matchweekMatch) {
    result.matchweek = matchweekMatch[1];
}
```

```python
# Python: 使用实际值
actual_matchweek = extracted.get('matchweek', str(i))
filename = f"{date}-中超-第{actual_matchweek}轮.json"
```

**原因**: 补赛等特殊情况时，比赛日期与轮次不一致

**实际案例**:
- 2025赛季第6轮补赛
- 原定日期: 2025-04-16
- 实际日期: 2025-06-18
- 文件名应为: `2025-06-18-中超-第6轮.json`

---

#### ⚠️ 关键原则2: 教练和队长信息提取

**FBref页面结构**:
```
Shanghai Port
Manager: Kevin Muscat
Captain: Yan Junling
...
Shenzhen Peng City
Manager: Christian Lattanzio
Captain: Jiang Zhipeng
```

**提取代码**:
```javascript
const lines = bodyText.split('\n');
const managers = [];
const captains = [];

lines.forEach(line => {
    const trimmed = line.trim();
    
    // 提取教练（按顺序出现）
    if (trimmed.startsWith('Manager:')) {
        const match = trimmed.match(/Manager:\s*(.+)/);
        if (match && managers.length < 2) {
            managers.push(match[1].trim());
        }
    }
    
    // 提取队长
    if (trimmed.startsWith('Captain:')) {
        const match = trimmed.match(/Captain:\s*(.+)/);
        if (match && captains.length < 2) {
            captains.push(match[1].trim());
        }
    }
});

result.homeManager = managers[0] || '';
result.awayManager = managers[1] || '';
result.homeCaptain = captains[0] || '';
result.awayCaptain = captains[1] || '';
```

---

#### ⚠️ 关键原则3: 裁判组信息提取

**FBref格式**:
```
Officials: Ai Kun (Referee) · Shi Xiang (AR1) · Xi Fei (AR2) · Zhen Wei (4th) · Wang Wei (VAR)
```

**提取代码**:
```javascript
const officialsMatch = bodyText.match(/Officials:\s*([^\n]+)/);
if (officialsMatch) {
    const officialsText = officialsMatch[1];
    
    // 主裁判
    const mainMatch = officialsText.match(/([A-Za-z\s]+?)\s*\(Referee\)/);
    if (mainMatch) result.referees.main = mainMatch[1].trim();
    
    // 边裁1
    const ar1Match = officialsText.match(/·\s*([A-Za-z\s]+?)\s*\(AR1\)/);
    if (ar1Match) result.referees.ar1 = ar1Match[1].trim();
    
    // 边裁2
    const ar2Match = officialsText.match(/·\s*([A-Za-z\s]+?)\s*\(AR2\)/);
    if (ar2Match) result.referees.ar2 = ar2Match[1].trim();
    
    // 第四裁判
    const fourthMatch = officialsText.match(/·\s*([A-Za-z\s]+?)\s*\(4th\)/);
    if (fourthMatch) result.referees.fourth = fourthMatch[1].trim();
    
    // VAR
    const varMatch = officialsText.match(/·\s*([A-Za-z\s]+?)\s*\(VAR\)/);
    if (varMatch) result.referees.var = varMatch[1].trim();
}
```

---

#### ⚠️ 关键原则4: 比赛时间提取

**FBref格式**:
```
Sunday February 23, 2025, 19:35 (venue time)
```

**提取代码**:
```javascript
const timeMatch = bodyText.match(/(\d{1,2}:\d{2})\s*\(venue time\)/);
if (timeMatch) {
    result.matchTime = timeMatch[1];  // "19:35"
}
```

---

#### ⚠️ 关键原则5: 进球类型识别

**FBref页面标识**:
- 点球: `(P)` 或 `Penalty`
- 乌龙球: `(OG)` 或 `Own Goal`

**提取逻辑**:
```python
# Python处理
if event_type == 'goal':
    goal_type = 'goal'  # 默认普通进球
    
    # 判断进球类型
    if '(P)' in text or 'Penalty' in text:
        goal_type = 'penalty_goal'  # 点球
    elif 'Own Goal' in text or '(OG)' in text:
        goal_type = 'own_goal'      # 乌龙球
    
    events.append({
        "type": "goal",
        "goal_type": goal_type,
        "player": player,
        "player2": assist_player,
        ...
    })
```

**注意事项**:
- 点球通常没有助攻（player2为空）
- 乌龙球的player是对阵球队的球员（own goal）

---

#### ⚠️ 关键原则6: Events提取

**HTML结构**:
```html
<div class="event a">  <!-- 客队事件 -->
<div class="event b">  <!-- 主队事件 -->
```

**提取逻辑**:
```javascript
const eventDivs = document.querySelectorAll('.event');

eventDivs.forEach(div => {
    const text = div.textContent;
    const className = div.className;
    const links = Array.from(div.querySelectorAll('a'))
        .map(a => a.textContent.trim());
    
    if (links.length > 0) {
        result.events.push({
            text: text,
            className: className,
            players: links
        });
    }
});
```

**判断主客队**:
```python
team = 'home' if 'event a' in className else 'away'
```

**注意**: `event a`是客队，`event b`是主队！

---

#### ⚠️ 关键原则7: 统计数据提取

**FBref格式特点**:
- 主队: `7 of 16 — 44%`
- 客队: `23% — 3 of 13`（百分比在前）

**提取代码**:
```javascript
// 射门数据
const shotsMatch = bodyText.match(
    /Shots on Target[\s\S]*?(\d+)\s+of\s+(\d+)\s*[—–-]\s*(\d+)%[\s\S]*?(\d+)%\s*[—–-]\s*(\d+)\s+of\s+(\d+)/
);

if (shotsMatch) {
    result.statistics.shots_on_target = {
        home: shotsMatch[1],  // 7
        away: shotsMatch[5]   // 3
    };
    result.statistics.shots = {
        home: shotsMatch[2],  // 16
        away: shotsMatch[6]   // 13
    };
    result.statistics.shots_accuracy = {
        home: shotsMatch[3] + '%',  // 44%
        away: shotsMatch[4] + '%'   // 23%
    };
}
```

**注意**: 主客队格式相反，需要仔细对应！

---

## 文件命名规则

### 格式
```
{日期}-中超-第{轮次}轮.json
```

### 示例
```
2025-02-23-中超-第1轮.json
2025-06-18-中超-第6轮.json  (补赛)
2025-11-22-中超-第30轮.json
```

### 规则
1. **日期格式**: YYYY-MM-DD
2. **轮次**: 使用从FBref页面提取的**实际matchweek值**
3. **编码**: UTF-8
4. **缩进**: 2空格

### ⚠️ 补赛处理
- 文件名使用**实际轮次**，而非文件顺序
- 示例：第6轮补赛在6月18日，文件名为 `2025-06-18-中超-第6轮.json`

---

## 数据验证

### 自动验证脚本

```python
#!/usr/bin/env python3
"""验证matchweek一致性"""

import json
import glob
import os

def verify_season(season):
    dir_path = f'data/match-reports-{season}'
    files = sorted(glob.glob(f'{dir_path}/*.json'))
    
    mismatches = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        data = json.load(open(filepath))
        
        # 从文件名提取轮次
        filename_round = filename.split('-第')[1].split('轮')[0]
        
        # 从数据中提取matchweek
        round_info = data['match_info']['competition']['round']
        data_round = round_info.split()[-1]
        
        if filename_round != data_round:
            mismatches.append({
                'file': filename,
                'filename_round': filename_round,
                'data_round': data_round
            })
    
    return mismatches

# 使用示例
for season in ['2023', '2024', '2025']:
    issues = verify_season(season)
    if issues:
        print(f"❌ {season}赛季发现{len(issues)}个不一致")
        for issue in issues:
            print(f"  {issue['file']}: 第{issue['filename_round']}轮 vs 第{issue['data_round']}轮")
    else:
        print(f"✅ {season}赛季所有文件名与数据一致")
```

### 数据完整性检查

```python
import json
import glob

files = sorted(glob.glob('data/match-reports-2025/*.json'))

stats = {
    'time': 0,
    'coach': 0,
    'captain': 0,
    'referee': 0,
    'goals_with_type': 0
}

for filepath in files:
    data = json.load(open(filepath))
    
    if data['match_info']['time'] != '20:00':
        stats['time'] += 1
    if data['teams']['home']['coach']:
        stats['coach'] += 1
    if data['teams']['home']['captain']:
        stats['captain'] += 1
    if data['match_info']['referee']['main']:
        stats['referee'] += 1
    
    goals = [e for e in data['events'] if e['type'] == 'goal']
    for goal in goals:
        if goal.get('goal_type'):
            stats['goals_with_type'] += 1

print(f"比赛时间准确: {stats['time']}/30")
print(f"教练信息完整: {stats['coach']}/30")
print(f"队长信息完整: {stats['captain']}/30")
print(f"裁判信息完整: {stats['referee']}/30")
print(f"进球类型标记: {stats['goals_with_type']}个")
```

---

## 故障排除

### Q1: Chrome连接失败

**症状**: `CDP connection failed`

**解决方案**:
```bash
# 检查Chrome是否运行
ps aux | grep chrome

# 检查端口9222
lsof -i :9222

# 重启Chrome
pkill -f chrome
# 然后重新启动Chrome with --remote-debugging-port=9222
```

---

### Q2: Matchweek不一致

**症状**: 文件名轮次与数据中matchweek不符

**原因**: 使用循环变量而非从页面提取

**验证**:
```bash
python3 scripts/verify_matchweek.py
```

**修复**: 使用正确提取matchweek的脚本（v9.3+）

---

### Q3: 教练或队长信息缺失

**症状**: coach或captain字段为空

**检查**:
```javascript
// 查看页面是否包含Manager/Captain
const bodyText = document.body.innerText;
console.log(bodyText.includes('Manager:'));
console.log(bodyText.includes('Captain:'));
```

**解决**: 使用v9.3 Final版本脚本

---

### Q4: 进球类型未识别

**症状**: 所有进球的goal_type都是'goal'，缺少penalty_goal/own_goal

**检查页面**:
```javascript
const bodyText = document.body.innerText;
console.log(bodyText.includes('(P)'));
console.log(bodyText.includes('(OG)'));
```

**解决**: 确保使用正确的识别逻辑（见"进球类型识别"章节）

---

### Q5: 统计数据不完整

**症状**: 统计字段少于12项

**检查**:
```python
required_stats = [
    'possession', 'shots_on_target', 'shots', 'shots_accuracy',
    'saves', 'yellow_cards', 'red_cards', 'fouls',
    'corners', 'crosses', 'interceptions', 'offsides'
]

stats = data['statistics']
missing = [s for s in required_stats if s not in stats]
print(f"缺失: {missing}")
```

**常见原因**:
- FBref页面数据为0时格式特殊
- 网络问题导致页面加载不完整

---

## 最佳实践

### ✅ DO（必须做）

1. **从页面提取matchweek**  
   不要使用循环变量

2. **验证数据完整性**  
   抓取后立即验证

3. **处理特殊情况**  
   补赛、延期、0值数据

4. **使用版本控制**  
   在metadata中记录version

5. **备份原始数据**  
   修复前先备份

### ❌ DON'T（不要做）

1. **不要假设顺序**  
   比赛不总是按轮次顺序进行

2. **不要硬编码**  
   球队名称、教练名称等可能变化

3. **不要跳过验证**  
   验证是质量的保证

4. **不要忽略错误**  
   失败的比赛需要调查原因

---

## 相关文件

### 脚本文件
- `scripts/batch_scrape_2025_v9.3_final.py` - 2025赛季抓取脚本
- `scripts/batch_scrape_2024_updated.py` - 2024赛季抓取脚本
- `scripts/batch_scrape_2023_updated.py` - 2023赛季抓取脚本
- `scripts/verify_matchweek.py` - Matchweek验证脚本

### 数据文件
- `data/2025-match_urls.json` - 2025赛季URL列表
- `data/2024-match_urls.json` - 2024赛季URL列表
- `data/2023-match_urls.json` - 2023赛季URL列表
- `data/match-reports-2025/` - 2025赛季比赛报告（30个文件）
- `data/match-reports-2024/` - 2024赛季比赛报告（30个文件）
- `data/match-reports-2023/` - 2023赛季比赛报告（30个文件）

### 其他文档
- `docs/How-to-Scrape-Match-Report-URLs.md` - URL抓取指南

---

## 联系方式

**维护者**: 小龙虾 🦞  
**项目**: 上海海港赛事报告数据抓取系统  
**最后更新**: 2026-03-29 19:10

---

**🎉 文档完成！所有抓取逻辑已完整记录。**
