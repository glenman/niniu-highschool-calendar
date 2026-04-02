# 心跳任务配置

Heartbeat 每30分钟检查一次。

## 当前任务

### 📈 A股投资分析（每日）
**检查频率**: 每日早上8:30-9:00

**执行逻辑**:
1. **加载历史知识库**（趋势、模式、准确率）
2. 采集国内外财经新闻
3. **分析市场模式**（基于历史数据）
4. 多因子筛选优质股票
5. **生成智能推荐**（结合历史准确率调整置信度）
6. **记录预测结果**（用于次日验证）
7. **验证昨日预测**（计算准确率）
8. **优化模型参数**（反馈学习）

**系统特点**:
- ✅ **闭环学习**: 预测→记录→验证→优化
- ✅ **知识积累**: 历史数据持续沉淀
- ✅ **置信度调整**: 基于历史准确率动态调整
- ✅ **持续优化**: 根据反馈自动改进

**输出方式**:
- ⭐ **最终输出**: 只发送荐股建议（推荐股票+操作策略+风险提示）
- 📊 **内部数据**: 新闻/分析存入知识库（不发送给用户）
- 💾 **存档位置**: 
  - 整合版建议: `memory/investment/daily/integrated_advice_*.md`
  - 反馈报告: `memory/investment/daily/feedback_report_*.json`
  - 知识库: `memory/investment/knowledge/`

**手动触发**: 
- Heartbeat版（自动推送）: `python3 investment-system/run_heartbeat.py` ⭐
- 整合版（本地运行）: `python3 investment-system/run_integrated_system.py`
- 快速版: `python3 investment-system/run_pre_market_quick.py`

**状态**: ✅ 闭环系统已上线，每日自动学习和优化

---

## 其他任务

(暂无其他定时任务)

## 执行规则

- Heartbeat每30分钟自动检查
- 只在指定时间窗口执行相应任务
- 如果执行失败,记录到日志并通知用户
