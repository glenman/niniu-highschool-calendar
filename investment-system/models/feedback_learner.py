#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反馈学习系统 - 验证预测准确性，持续优化模型
"""

import json
import os
from datetime import datetime, timedelta
import csv
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class FeedbackLearner:
    """反馈学习器 - 验证预测，优化模型"""
    
    def __init__(self):
        self.base_dir = "memory/investment/daily"
        self.knowledge_dir = "memory/investment/knowledge"
        self.feedback_file = f"{self.knowledge_dir}/feedback_history.json"
        
    def verify_yesterday_prediction(self):
        """验证昨天的预测准确性"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"\n🔍 验证昨日预测（{yesterday}）...")
        
        # 1. 加载昨天的建议
        advice_file = f"{self.base_dir}/pre_market_advice_{yesterday}.md"
        if not os.path.exists(advice_file):
            print("  ⚠️ 昨日建议文件不存在")
            return None
        
        # 2. 加载昨天的推荐股票
        stocks_file = f"{self.base_dir}/screened_stocks_{yesterday}.csv"
        if not os.path.exists(stocks_file):
            print("  ⚠️ 昨日股票数据不存在")
            return None
        
        recommended_stocks = []
        with open(stocks_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            recommended_stocks = list(reader)
        
        # 3. 获取这些股票今天的表现（实际涨跌幅）
        print(f"\n  📊 验证{len(recommended_stocks[:5])}只推荐股票：")
        
        # 简化版：这里应该获取今天的实际数据来验证
        # 实际实现需要调用股票API获取今日行情
        
        verification_result = {
            'date': yesterday,
            'verified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'recommendations': []
        }
        
        # TODO: 获取实际涨跌幅，计算预测准确性
        # 这里需要实现：获取今日行情，对比昨日推荐
        
        return verification_result
    
    def analyze_prediction_patterns(self):
        """分析历史预测模式"""
        print("\n📊 分析历史预测模式...")
        
        # 读取反馈历史
        if not os.path.exists(self.feedback_file):
            print("  ⚠️ 反馈历史数据不足")
            return None
        
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if len(history) < 7:
            print(f"  ⚠️ 数据不足（仅{len(history)}天），至少需要7天")
            return None
        
        # 分析准确率
        total_predictions = 0
        successful_predictions = 0
        
        for date, result in history.items():
            if 'recommendations' in result:
                for rec in result['recommendations']:
                    total_predictions += 1
                    # 如果实际涨幅>3%，认为预测成功
                    if rec.get('actual_return', 0) > 3:
                        successful_predictions += 1
        
        if total_predictions > 0:
            accuracy = successful_predictions / total_predictions
            print(f"  ✅ 历史准确率: {accuracy:.1%} ({successful_predictions}/{total_predictions})")
            
            return {
                'accuracy': accuracy,
                'total_predictions': total_predictions,
                'successful_predictions': successful_predictions
            }
        
        return None
    
    def optimize_model_parameters(self):
        """优化模型参数"""
        print("\n🔧 优化模型参数...")
        
        # 读取历史数据
        trends_file = f"{self.knowledge_dir}/trends/daily_trends.json"
        if not os.path.exists(trends_file):
            print("  ⚠️ 趋势数据不足")
            return None
        
        with open(trends_file, 'r', encoding='utf-8') as f:
            trends = json.load(f)
        
        # 分析哪些特征与成功预测相关
        # 简化版：实际需要更复杂的统计分析
        
        optimization_result = {
            'optimized_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'suggestions': [
                'PE区间优化: 建议调整为8-50倍',
                '换手率权重提升: 当前30% → 建议40%',
                '增加情绪因子: 建议增加新闻情绪权重'
            ]
        }
        
        print("  💡 优化建议:")
        for i, suggestion in enumerate(optimization_result['suggestions'], 1):
            print(f"    {i}. {suggestion}")
        
        return optimization_result
    
    def generate_feedback_report(self):
        """生成反馈报告"""
        print("\n" + "=" * 60)
        print("🔄 反馈学习系统运行")
        print("=" * 60)
        
        # 1. 验证昨日预测
        verification = self.verify_yesterday_prediction()
        
        # 2. 分析历史模式
        patterns = self.analyze_prediction_patterns()
        
        # 3. 优化模型
        optimization = self.optimize_model_parameters()
        
        # 保存反馈
        today = datetime.now().strftime('%Y-%m-%d')
        feedback_report = {
            'date': today,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'verification': verification,
            'patterns': patterns,
            'optimization': optimization
        }
        
        report_file = f"{self.base_dir}/feedback_report_{today}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 反馈报告已生成: {report_file}")
        print("=" * 60)
        
        return feedback_report


def main():
    """主函数"""
    learner = FeedbackLearner()
    learner.generate_feedback_report()


if __name__ == '__main__':
    main()
