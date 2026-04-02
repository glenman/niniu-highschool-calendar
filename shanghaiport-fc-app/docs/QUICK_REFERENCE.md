# 上海海港赛事报告抓取 - 快速参考卡

**版本**: v3.0 Final | **更新时间**: 2026-03-29 19:10

---

## 🚀 快速开始

### 启动Chrome（首次）

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
```

### 运行抓取

```bash
cd shanghaiport-fc-app

# 2025赛季
python3 scripts/batch_scrape_2025_v9.3_final.py

# 验证结果
python3 scripts/verify_matchweek.py --season 2025
```

---

## 📊 完整数据结构

### 新增字段（v3.0）

| 字段 | 说明 | 提取逻辑 |
|------|------|----------|
| ⏰ 比赛时间 | 真实开球时间 | `19:35 (venue time)` |
| 👨‍💼 教练 | 主客队教练 | `Manager: XXX` |
| 👑 队长 | 主客队队长 | `Captain: XXX` |
| 🎯 裁判组 | 5人裁判组 | `Officials: XXX (Referee) · XXX (AR1) · XXX (AR2) · XXX (4th) · XXX (VAR)` |
| ⚽ 进球类型 | goal/penalty_goal/own_goal | `(P)` / `(OG)` |

### 12项完整统计

1. possession（控球率）
2. shots_on_target（射正数）
3. shots（射门总数）
4. shots_accuracy（射正率）
5. saves（扑救成功率）
6. yellow_cards（黄牌）
7. red_cards（红牌）
8. fouls（犯规）
9. corners（角球）
10. crosses（传中）
11. interceptions（拦截）
12. offsides（越位）

---

## ⚠️ 关键提取逻辑

### 1. Matchweek（必须从页面提取！）

**❌ 错误**:
```python
filename = f"{date}-中超-第{i}轮.json"  # i是循环变量
```

**✅ 正确**:
```javascript
// JavaScript
const matchweekMatch = bodyText.match(/Matchweek\s+(\d+)/i);
if (matchweekMatch) result.matchweek = matchweekMatch[1];
```

```python
# Python
filename = f"{date}-中超-第{extracted['matchweek']}轮.json"
```

**原因**: 补赛等特殊情况时，轮次与文件顺序不一致

---

### 2. 教练和队长

```javascript
const lines = bodyText.split('\n');
const managers = [];
const captains = [];

lines.forEach(line => {
    if (line.startsWith('Manager:')) {
        managers.push(line.match(/Manager:\s*(.+)/)[1].trim());
    }
    if (line.startsWith('Captain:')) {
        captains.push(line.match(/Captain:\s*(.+)/)[1].trim());
    }
});

result.homeManager = managers[0];
result.awayManager = managers[1];
result.homeCaptain = captains[0];
result.awayCaptain = captains[1];
```

---

### 3. 裁判组

```javascript
const officialsMatch = bodyText.match(/Officials:\s*([^\n]+)/);
if (officialsMatch) {
    const text = officialsMatch[1];
    
    // 主裁判
    const main = text.match(/([A-Za-z\s]+?)\s*\(Referee\)/);
    if (main) result.referees.main = main[1].trim();
    
    // 边裁1、2、第四裁判、VAR 同理
    // ...
}
```

---

### 4. 进球类型识别

```python
if event_type == 'goal':
    goal_type = 'goal'  # 默认
    
    if '(P)' in text or 'Penalty' in text:
        goal_type = 'penalty_goal'
    elif 'Own Goal' in text or '(OG)' in text:
        goal_type = 'own_goal'
    
    events.append({
        "type": "goal",
        "goal_type": goal_type,
        ...
    })
```

**注意**: 点球通常没有助攻（player2为空）

---

### 5. 主客队判断

```python
# FBref的.event a是客队，.event b是主队！
team = 'home' if 'event a' in className else 'away'
```

---

## 📁 文件命名规则

**格式**: `{日期}-中超-第{轮次}轮.json`

**示例**:
- 正常: `2025-02-23-中超-第1轮.json`
- 补赛: `2025-06-18-中超-第6轮.json`（第6轮在6月18日进行）

**轮次来源**: 必须使用从FBref页面提取的实际值

---

## 🔧 验证脚本

### 检查Matchweek一致性

```python
import json, glob, os

files = glob.glob('data/match-reports-2025/*.json')

for f in files:
    data = json.load(open(f))
    
    # 文件名中的轮次
    filename_round = f.split('-第')[1].split('轮')[0]
    
    # 数据中的matchweek
    data_round = data['match_info']['competition']['round'].split()[-1]
    
    if filename_round != data_round:
        print(f"❌ {f}: 文件名第{filename_round}轮 vs 数据第{data_round}轮")
```

### 检查数据完整性

```python
import json, glob

files = glob.glob('data/match-reports-2025/*.json')

for f in files:
    data = json.load(open(f))
    
    checks = {
        'time': data['match_info']['time'] != '20:00',
        'coach': bool(data['teams']['home']['coach']),
        'captain': bool(data['teams']['home']['captain']),
        'referee': bool(data['match_info']['referee']['main'])
    }
    
    if not all(checks.values()):
        print(f"⚠️  {f.split('/')[-1]}")
        for key, ok in checks.items():
            if not ok:
                print(f"  - 缺少: {key}")
```

---

## 📊 2025赛季数据质量

### 完整性

| 字段 | 完整率 | 说明 |
|------|--------|------|
| 比赛时间 | 80% | 24/30准确提取 |
| 教练信息 | 100% | 主客队教练全部提取 |
| 队长信息 | 100% | 主客队队长全部提取 |
| 裁判组 | 100% | 5人裁判组完整 |
| 进球类型 | 100% | 正确识别点球4个、乌龙球5个 |
| 12项统计 | 100% | 完整 |

### 进球类型分布

- **普通进球**: 99个
- **点球**: 4个
  - 2025-02-23 - Gustavo (90+3') ✅
  - 2025-07-26 - Gabriel Airton de Souza
  - 2025-08-30 - Felipe Sousa
  - 2025-09-12 - Mateus Vital
- **乌龙球**: 5个
  - 2025-04-02 - Wang Shenchao
  - 2025-04-16 - Xie Weijun
  - 2025-07-18 - Abduhamit Abdugheni
  - 2025-08-02 - Wang Jianan
  - 2025-10-31 - Liu Haofan

**总进球数**: 108个

---

## 🐛 常见问题

### Q1: Chrome连接失败

```bash
# 检查Chrome进程
ps aux | grep chrome

# 检查端口
lsof -i :9222

# 重启Chrome
pkill -f chrome
# 重新启动Chrome with --remote-debugging-port=9222
```

### Q2: Matchweek不一致

**原因**: 使用了循环变量而非页面提取  
**解决**: 使用v9.3 Final脚本

### Q3: 教练/队长缺失

**检查页面**:
```javascript
console.log(document.body.innerText.includes('Manager:'));
console.log(document.body.innerText.includes('Captain:'));
```

### Q4: 进球类型识别失败

**检查页面**:
```javascript
console.log(document.body.innerText.includes('(P)'));
console.log(document.body.innerText.includes('(OG)'));
```

---

## 📚 相关文档

- `COMPLETE_SCRAPER_GUIDE.md` - 完整详细指南
- `How-to-Scrape-Match-Report-URLs.md` - URL抓取指南

## 📁 脚本位置

- 2025赛季: `scripts/batch_scrape_2025_v9.3_final.py`
- 2024赛季: `scripts/batch_scrape_2024_updated.py`
- 2023赛季: `scripts/batch_scrape_2023_updated.py`
- 验证工具: `scripts/verify_matchweek.py`

---

**维护者**: 小龙虾 🦞  
**最后更新**: 2026-03-29 19:10
