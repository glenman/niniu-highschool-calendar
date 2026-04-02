#!/bin/bash
# 每日投资分析 - 完整闭环
# 包含：学习→预测→验证→优化

cd /Users/glenman/.openclaw/workspace

echo "============================================================"
echo "🦞 每日投资分析 - 完整闭环系统"
echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# 1. 验证昨日预测（反馈学习）
echo ""
echo "【步骤1/3】验证昨日预测..."
python3 investment-system/models/feedback_learner.py

# 2. 生成今日建议（整合知识库）
echo ""
echo "【步骤2/3】生成今日操盘建议..."
python3 investment-system/run_integrated_system.py

# 3. 知识归档（持续学习）
echo ""
echo "【步骤3/3】知识归档与趋势追踪..."
python3 investment-system/run_daily_analysis.py

echo ""
echo "============================================================"
echo "✅ 闭环系统运行完成"
echo "📊 明日将验证今日预测准确性"
echo "============================================================"
