# 快速开始指南

## 🎯 任务目标

从FBref网页抓取足球比赛数据，转换为标准化JSON格式，并导出到Excel。

## ⚠️ 当前状态

**FBref网站有Cloudflare保护**，自动化访问被拦截。需要手动操作。

## 📝 推荐工作流程

### 步骤1：手动收集数据

1. 在浏览器中打开比赛页面：
   https://fbref.com/en/matches/08602b83/Shanghai-Port-Wuhan-Three-Towns-March-1-2024-Chinese-Super-League

2. 手动复制以下数据：
   - ✅ 比赛基本信息（日期、时间、球场、比分等）
   - ✅ 球队阵容（首发11人 + 替补）
   - ✅ 比赛事件（进球、换人、黄牌等）
   - ✅ 统计数据（控球率、射门、传球等）
   - ✅ 球员个人统计

### 步骤2：填写JSON模板

1. 打开模板文件：
   ```bash
   open templates/match_data_template.json
   ```

2. 填写数据（参考模板中的示例）：
   - 修改比赛信息
   - 添加球员阵容
   - 记录比赛事件
   - 填写统计数据

3. 保存文件

### 步骤3：验证数据

```bash
cd templates
python3 -c "
import json
from process_match_data import MatchDataProcessor

with open('match_data_template.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

processor = MatchDataProcessor()
is_valid, errors = processor.validate_match_data(data)

if is_valid:
    print('✅ 数据验证通过！')
else:
    print('❌ 发现错误:')
    for error in errors:
        print(f'  - {error}')
"
```

### 步骤4：导出Excel

创建导出脚本 `export_excel.py`：

```python
import json
from process_match_data import MatchDataProcessor

# 加载数据
with open('match_data_template.json', 'r', encoding='utf-8') as f:
    match_data = json.load(f)

# 创建处理器
processor = MatchDataProcessor()

# 验证
is_valid, errors = processor.validate_match_data(match_data)

if is_valid:
    # 导出Excel
    excel_path = processor.create_excel_report(
        match_data,
        output_path='../match_report.xlsx'
    )
    print(f'✅ Excel已生成: {excel_path}')
else:
    print('❌ 数据验证失败:')
    for error in errors:
        print(f'  - {error}')
```

运行：
```bash
cd templates
python3 export_excel.py
```

## 📊 模板格式检查清单

### ✅ match_info 部分
- [ ] match_id: 比赛ID
- [ ] date: 日期 (YYYY-MM-DD)
- [ ] time: 时间 (HH:MM)
- [ ] competition.name: 赛事名称
- [ ] venue.name: 球场名称

### ✅ teams 部分
- [ ] home.name: 主队名称
- [ ] home.score: 主队比分
- [ ] home.lineup: 首发阵容（11人）
- [ ] away.name: 客队名称
- [ ] away.score: 客队比分
- [ ] away.lineup: 首发阵容（11人）

### ✅ events 部分
- [ ] 每个事件包含: minute, type, team, player
- [ ] 事件类型: goal, penalty, yellow_card, red_card, substitution
- [ ] 按时间顺序排列

### ✅ statistics 部分
- [ ] possession: 控球率
- [ ] shots: 射门次数
- [ ] shots_on_target: 射正次数
- [ ] corners: 角球
- [ ] fouls: 犯规

### ✅ player_stats 部分
- [ ] 每个球员的基本信息
- [ ] 传球、射门、犯规等统计

## 🎨 Excel输出示例

生成的Excel包含5个工作表：

| 工作表 | 内容 | 行数 |
|--------|------|------|
| 比赛信息 | 日期、球场、裁判等 | 1 |
| 球员阵容 | 双方所有球员 | 22+ |
| 比赛事件 | 所有事件时间线 | 10-30 |
| 统计数据 | 双方数据对比 | 10-15 |
| 球员统计 | 详细个人数据 | 22+ |

## 🔧 常见问题

### Q: JSON格式错误怎么办？
A: 使用JSON验证工具检查：
- 所有字符串用双引号
- 数字不加引号
- 最后一个元素后不加逗号
- 使用 `true`/`false`（小写）

### Q: 数据验证失败？
A: 检查必需字段是否都已填写：
- match_info.date
- teams.home.name / teams.away.name
- teams.home.score / teams.away.score
- 至少一个events

### Q: Excel打开乱码？
A: 确保使用UTF-8编码，脚本已自动处理。

## 📚 相关文件

- `match-report.json` - JSON Schema规范
- `match_data_template.json` - 数据填写模板
- `process_match_data.py` - 处理脚本
- `README.md` - 详细文档

## 💡 下一步

1. 完善模板数据（当前只有示例数据）
2. 尝试导出Excel
3. 根据需要调整字段和格式

---

**提示**: 如果需要批量处理多场比赛，可以将数据收集工作标准化，然后编写脚本自动化处理。
