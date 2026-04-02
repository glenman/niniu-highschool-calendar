# 足球比赛数据抓取和处理工具

## 📋 概述

这套工具用于将足球比赛数据（如FBref）转换为标准化的JSON格式，并导出到Excel。

## 🚨 重要说明

**FBref网站有严格的Cloudflare反爬虫保护**，自动化访问会被拦截。推荐两种方式：

1. **手动复制数据** → 使用提供的模板
2. **使用浏览器插件** → 手动导出数据后处理

## 📁 文件说明

### 1. `match-report.json` - JSON Schema模板
定义了完整的比赛数据格式规范，包括：
- 比赛基本信息（日期、时间、球场、裁判等）
- 球队信息（阵容、替补、阵型、比分等）
- 比赛事件（进球、换人、黄牌、红牌等）
- 统计数据（控球率、射门、传球等）
- 球员详细统计

### 2. `match_data_template.json` - 数据填写模板
预填充了部分示例数据，可以直接编辑填写：
- 包含上海海港 vs 武汉三镇的基本框架
- 所有字段都有说明和示例
- 支持中文和英文

### 3. `process_match_data.py` - 数据处理脚本
提供以下功能：
- 数据验证：检查JSON格式是否符合规范
- Excel导出：将数据转换为多工作表的Excel文件
- 模板生成：创建空白数据模板

## 🛠️ 使用方法

### 方法一：手动填写数据

1. **编辑模板**
```bash
# 打开模板文件
open templates/match_data_template.json

# 或使用你喜欢的编辑器
code templates/match_data_template.json
```

2. **填写数据**
从FBref网页手动复制数据，填写到JSON模板中：
- 比赛基本信息
- 球员阵容和替补
- 比赛事件（按时间顺序）
- 统计数据
- 球员个人统计

3. **验证数据**
```bash
python3 templates/process_match_data.py
```

4. **导出Excel**
修改脚本中的数据路径，然后运行：
```bash
python3 templates/process_match_data.py
```

### 方法二：程序化处理

```python
from process_match_data import MatchDataProcessor

# 初始化处理器
processor = MatchDataProcessor()

# 加载你的数据
import json
with open('your_match_data.json', 'r', encoding='utf-8') as f:
    match_data = json.load(f)

# 验证数据
is_valid, errors = processor.validate_match_data(match_data)
if is_valid:
    # 导出Excel
    excel_path = processor.create_excel_report(match_data)
    print(f"Excel已生成: {excel_path}")
else:
    print("验证失败:")
    for error in errors:
        print(f"  - {error}")
```

## 📊 Excel输出格式

生成的Excel文件包含5个工作表：

1. **比赛信息** - 基本比赛信息
2. **球员阵容** - 双方首发和替补球员
3. **比赛事件** - 按时间排列的所有事件
4. **统计数据** - 双方数据对比
5. **球员统计** - 所有球员的详细数据

## 🎯 数据字段说明

### 必需字段
- ✅ 比赛日期和时间
- ✅ 赛事名称
- ✅ 主客队名称和比分
- ✅ 至少一个比赛事件

### 可选字段
- ⚪ 球场信息和观众人数
- ⚪ 裁判信息
- ⚪ 天气状况
- ⚪ 详细球员统计

## 🔧 扩展和定制

### 添加新的统计项
编辑 `match-report.json` 的 `statistics` 部分：

```json
"statistics": {
  "your_new_stat": {
    "home": 0,
    "away": 0
  }
}
```

然后在 `process_match_data.py` 的 `_translate_stat_name` 方法中添加翻译：

```python
translations = {
    # ... 现有翻译
    'your_new_stat': '你的新统计项'
}
```

### 自定义Excel格式
修改 `process_match_data.py` 的 `create_excel_report` 方法，可以：
- 调整列顺序
- 添加条件格式
- 设置单元格样式
- 添加图表

## 📝 注意事项

1. **JSON格式**
   - 确保所有字符串使用双引号
   - 数字不需要引号
   - 布尔值使用 `true`/`false`（小写）
   - 空值使用 `null`

2. **数据验证**
   - 控球率总和应接近100%
   - 比分应与进球事件一致
   - 时间应在0-120分钟范围内

3. **编码**
   - 所有文件使用UTF-8编码
   - 支持中文字符

## 🐛 常见问题

### Q: 为什么不能自动抓取FBref？
A: FBref使用Cloudflare保护，会检测和拦截自动化访问。必须手动复制数据或使用浏览器插件。

### Q: 如何处理缺失的数据？
A: 可以省略可选字段，或将值设为 `null` 或 `0`（根据字段类型）。

### Q: 可以处理其他网站的数据吗？
A: 可以！只需将数据调整为符合 `match-report.json` 的格式即可。

## 📚 参考资源

- [JSON Schema规范](https://json-schema.org/)
- [Pandas文档](https://pandas.pydata.org/)
- [FBref网站](https://fbref.com/)

## 📄 许可

本工具仅供学习和个人使用。请遵守FBref的使用条款。

---

**创建时间**: 2026-03-23
**版本**: 1.0
**维护者**: 小龙虾 🦞
