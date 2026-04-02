#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日投资分析报告生成器
"""

import json
import csv
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class DailyReportGenerator:
    """每日报告生成器"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.base_dir = "memory/investment/daily"
    
    def load_stock_data(self):
        """加载股票筛选数据"""
        csv_file = f"{self.base_dir}/screened_stocks_{self.today}.csv"
        if not os.path.exists(csv_file):
            print(f"❌ 股票数据文件不存在: {csv_file}")
            return None
        
        stocks = []
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stocks.append(row)
        
        return stocks
    
    def load_north_fund(self):
        """加载北向资金数据"""
        json_file = f"{self.base_dir}/north_fund_{self.today}.json"
        if not os.path.exists(json_file):
            return None
        
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_report(self, stocks, north_fund=None):
        """生成每日报告"""
        report = []
        report.append("=" * 80)
        report.append(f"🦞 A股投资分析日报 - {self.today}")
        report.append("=" * 80)
        report.append("")
        
        # 风险提示
        report.append("⚠️  风险提示：本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
        report.append("")
        
        # 市场概况
        report.append("## 📊 市场概况")
        report.append("")
        
        if north_fund:
            report.append(f"**北向资金**：净流入 {north_fund.get('当日净流入', 0):.2f} 亿元")
        else:
            report.append("**北向资金**：数据暂无")
        report.append("")
        
        # 推荐股票
        if stocks:
            report.append("## 📈 今日推荐股票（TOP10）")
            report.append("")
            report.append("基于多因子模型筛选（PE、换手率、涨跌幅等综合评分）：")
            report.append("")
            
            for i, stock in enumerate(stocks[:10], 1):
                report.append(f"### {i}. {stock['代码']} {stock['名称']}")
                report.append(f"- **最新价**: {float(stock['最新价']):.2f} 元")
                report.append(f"- **涨跌幅**: {float(stock['涨跌幅']):.2f}%")
                report.append(f"- **市盈率**: {float(stock['市盈率']):.2f}")
                report.append(f"- **换手率**: {float(stock['换手率']):.2f}%")
                report.append(f"- **综合评分**: {float(stock['评分']):.1f}")
                report.append("")
        else:
            report.append("## 📈 今日推荐股票")
            report.append("")
            report.append("⚠️  今日无符合筛选条件的股票")
            report.append("")
        
        # 筛选条件说明
        report.append("## 🔍 筛选条件说明")
        report.append("")
        report.append("1. **基本面筛选**：")
        report.append("   - PE（市盈率）：5-100倍")
        report.append("   - 排除ST和退市股票")
        report.append("")
        report.append("2. **技术面筛选**：")
        report.append("   - 换手率：0.01%-50%（适应不同市场环境）")
        report.append("   - 排除极端波动（涨跌幅<10%）")
        report.append("")
        report.append("3. **综合评分模型**：")
        report.append("   - 涨跌幅权重：40%")
        report.append("   - 换手率权重：30%")
        report.append("   - 市盈率权重：30%")
        report.append("")
        
        # 免责声明
        report.append("---")
        report.append("")
        report.append("🦞 **小龙虾AI投资助手**")
        report.append("📅 生成时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        report.append("")
        report.append("⚠️  **免责声明**：")
        report.append("- 本报告由AI自动生成，基于公开数据分析")
        report.append("- 不构成任何投资建议或承诺")
        report.append("- 投资决策请结合自身判断，谨慎投资")
        report.append("- 历史表现不代表未来收益")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, report):
        """保存报告"""
        report_file = f"{self.base_dir}/daily_report_{self.today}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 报告已保存: {report_file}")
        return report_file


def main():
    """主函数"""
    generator = DailyReportGenerator()
    
    # 加载数据
    stocks = generator.load_stock_data()
    north_fund = generator.load_north_fund()
    
    if stocks:
        # 生成报告
        report = generator.generate_report(stocks, north_fund)
        
        # 保存报告
        report_file = generator.save_report(report)
        
        # 输出到控制台
        print("\n" + report)
        
        return report
    else:
        print("❌ 无法生成报告：缺少股票数据")
        return None


if __name__ == '__main__':
    main()
