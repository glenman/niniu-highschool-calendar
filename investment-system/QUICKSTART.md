# 每日荐股分析 - 快速参考

> 一页纸快速了解项目

---

## 🎯 项目定位

基于AI的持续学习投资分析系统，通过闭环学习提供预见性操盘建议。

---

## 📁 核心文件（5个）

```
investment-system/
│
├── run_integrated_system.py       # 主程序 ⭐
│   └── 整合知识库 + 生成建议
│
├── run_daily_closed_loop.sh       # 闭环脚本 ⭐
│   └── 验证 → 学习 → 预测
│
├── models/feedback_learner.py     # 反馈学习 ⭐
│   └── 验证预测 → 计算准确率
│
├── data_collectors/               # 数据采集
│   ├── news_fetcher.py            # 国内新闻
│   ├── global_news_fetcher.py     # 海外新闻
│   └── stock_data_fetcher.py      # 股票数据
│
└── README.md                      # 完整文档
```

---

## 🔄 每日流程（3步）

```
1️⃣ 验证昨日预测
   └─ 计算准确率

2️⃣ 生成今日建议
   └─ 结合历史知识库
   └─ 动态置信度

3️⃣ 知识归档
   └─ 持续积累
```

---

## 📊 产出物（5个）

| 文件 | 内容 | 用途 |
|------|------|------|
| integrated_advice_*.md | 操盘建议 | 今日操作 |
| screened_stocks_*.csv | 筛选股票 | 备选标的 |
| feedback_report_*.json | 反馈报告 | 验证准确率 |
| news_archive/ | 新闻归档 | 历史查询 |
| daily_trends.json | 趋势数据 | 模式分析 |

---

## 🚀 快速使用

```bash
# 查看今日建议
cat memory/investment/daily/integrated_advice_$(date +%Y-%m-%d).md

# 手动生成建议
python3 investment-system/run_integrated_system.py

# 运行完整闭环
./investment-system/run_daily_closed_loop.sh
```

---

## 💡 核心创新

### ❌ 传统方式
收盘后总结 → 无法操作

### ✅ 本系统
开盘前建议 → 可直接操作

### ❌ 静态建议
固定建议 → 不考虑准确率

### ✅ 动态调整
根据历史准确率 → 调整置信度和仓位

---

## 📈 置信度逻辑

```
准确率 >70% → 置信度高 → 仓位60-70%
准确率 50-70% → 置信度中 → 仓位40-50%
准确率 <50% → 置信度低 → 仓位20-30%
```

---

## ⏰ 定时任务

**本项目只有1个定时任务**。

| 任务名称 | 执行频率 | 状态 |
|---------|---------|------|
| 每日荐股分析 | 每日8:30-9:00 | ✅ 运行中 |

---

## ⚠️ 风险提示

- 所有建议仅供参考
- 市场有风险，投资需谨慎
- 请独立决策，控制风险

---

## 📞 查看完整文档

```bash
cat investment-system/README.md
```

---

🦞 **每日荐股分析 - 持续学习，智能决策**
