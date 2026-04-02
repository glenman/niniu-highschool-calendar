#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股荐股分析脚本
严格按照用户指定的5步流程执行
"""

import akshare as ak
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class StockAnalyzer:
    """A股荐股分析器"""
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.report_lines = []
        
    def log(self, message: str):
        """记录日志"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def add_section(self, title: str, content: List[str]):
        """添加报告段落"""
        self.report_lines.append(f"\n### {title}\n")
        for line in content:
            self.report_lines.append(f"{line}\n")
    
    def step1_screening(self) -> List[Dict]:
        """
        第1步：初步筛选
        指令词：通过价值因子和质量因子，帮我找到目前国内股市中最具潜力的股票。
        """
        self.log("📊 第1步：初步筛选 - 价值因子与质量因子分析")
        
        try:
            # 获取A股实时行情数据
            self.log("  获取A股全市场行情数据...")
            df_all = ak.stock_zh_a_spot_em()
            
            self.log(f"  共获取 {len(df_all)} 只股票数据")
            
            # 价值因子筛选条件：
            # 1. 市盈率（PE）：5 < PE < 25（合理估值区间）
            # 2. 市净率（PB）：0.5 < PB < 3（资产价值合理）
            # 3. 质量因子：
            #    - 成交额 > 5亿（流动性好）
            #    - 涨跌幅：-3% < 涨跌幅 < 3%（避免极端波动）
            
            df_filtered = df_all[
                (df_all['市盈率-动态'] > 5) & 
                (df_all['市盈率-动态'] < 25) &
                (df_all['市净率'] > 0.5) & 
                (df_all['市净率'] < 3) &
                (df_all['涨跌幅'] > -3) & 
                (df_all['涨跌幅'] < 3) &
                (df_all['成交额'] > 500000000)  # 5亿
            ].copy()
            
            self.log(f"  筛选后剩余 {len(df_filtered)} 只股票")
            
            if len(df_filtered) == 0:
                self.log("  ⚠️ 没有符合条件的股票")
                return []
            
            # 综合评分系统（价值因子 + 质量因子）
            # 价值因子（60分）：
            #   - PE得分（30分）：PE越低越好
            #   - PB得分（30分）：PB越低越好
            # 质量因子（40分）：
            #   - 流动性得分（20分）：成交额越高越好
            #   - 稳定性得分（20分）：涨跌幅越接近0越好
            
            df_filtered['pe_score'] = ((25 - df_filtered['市盈率-动态']) / 20 * 30).clip(0, 30)
            df_filtered['pb_score'] = ((3 - df_filtered['市净率']) / 2.5 * 30).clip(0, 30)
            df_filtered['liquidity_score'] = (df_filtered['成交额'] / df_filtered['成交额'].max() * 20).clip(0, 20)
            df_filtered['stability_score'] = ((3 - abs(df_filtered['涨跌幅'])) / 3 * 20).clip(0, 20)
            
            df_filtered['total_score'] = (
                df_filtered['pe_score'] + 
                df_filtered['pb_score'] + 
                df_filtered['liquidity_score'] + 
                df_filtered['stability_score']
            )
            
            # 按综合得分排序，选择前5只
            top_stocks = df_filtered.nlargest(5, 'total_score')
            
            stocks = []
            for _, row in top_stocks.iterrows():
                stocks.append({
                    'code': row['代码'],
                    'name': row['名称'],
                    'price': row['最新价'],
                    'pe': round(row['市盈率-动态'], 2),
                    'pb': round(row['市净率'], 2),
                    'change': round(row['涨跌幅'], 2),
                    'volume': round(row['成交额'] / 100000000, 2),  # 亿元
                    'score': round(row['total_score'], 2),
                    'pe_score': round(row['pe_score'], 2),
                    'pb_score': round(row['pb_score'], 2),
                    'liquidity_score': round(row['liquidity_score'], 2),
                    'stability_score': round(row['stability_score'], 2)
                })
            
            self.log(f"  ✅ 筛选出 {len(stocks)} 只最具潜力股票")
            return stocks
            
        except Exception as e:
            self.log(f"  ❌ 筛选失败: {str(e)}")
            import traceback
            self.log(f"  详细错误: {traceback.format_exc()}")
            return []
    
    def step2_fundamentals(self, stock: Dict) -> Dict:
        """
        第2步：确认基本盘
        指令词：评估选中股票的财务健康程度，列出盈利趋势和现金流走向。
        """
        self.log(f"  📈 分析 {stock['name']} ({stock['code']}) 基本面...")
        
        fundamentals = {
            '财务健康程度': {},
            '盈利趋势': {},
            '现金流走向': {}
        }
        
        try:
            # 获取关键财务指标
            df_indicator = ak.stock_financial_analysis_indicator(symbol=stock['code'])
            
            if len(df_indicator) > 0:
                latest = df_indicator.iloc[0]
                
                # 财务健康程度
                fundamentals['财务健康程度'] = {
                    '资产负债率': latest.get('资产负债率(%)', 'N/A'),
                    '流动比率': latest.get('流动比率', 'N/A'),
                    '速动比率': latest.get('速动比率', 'N/A'),
                }
                
                # 盈利趋势
                fundamentals['盈利趋势'] = {
                    '净资产收益率(ROE)': latest.get('净资产收益率(%)', 'N/A'),
                    '总资产净利率(ROA)': latest.get('总资产净利率(%)', 'N/A'),
                    '销售毛利率': latest.get('销售毛利率(%)', 'N/A'),
                    '销售净利率': latest.get('销售净利率(%)', 'N/A'),
                }
                
        except Exception as e:
            self.log(f"    ⚠️  财务指标获取失败: {str(e)}")
            fundamentals['财务健康程度'] = {'备注': '数据暂时无法获取'}
            fundamentals['盈利趋势'] = {'备注': '数据暂时无法获取'}
        
        try:
            # 获取现金流数据
            df_cashflow = ak.stock_cash_flow_sheet_by_report_em(symbol=stock['code'])
            
            if len(df_cashflow) > 0:
                # 获取最近3期的现金流数据
                recent_3_periods = df_cashflow.head(3)
                
                cashflow_trend = []
                for idx, row in recent_3_periods.iterrows():
                    period = row.get('报告期', 'N/A')
                    operating_cf = row.get('经营活动产生的现金流量净额(元)', 0)
                    investing_cf = row.get('投资活动产生的现金流量净额(元)', 0)
                    financing_cf = row.get('筹资活动产生的现金流量净额(元)', 0)
                    
                    cashflow_trend.append({
                        '报告期': period,
                        '经营现金流': f"{operating_cf/100000000:.2f}亿" if operating_cf != 0 else 'N/A',
                        '投资现金流': f"{investing_cf/100000000:.2f}亿" if investing_cf != 0 else 'N/A',
                        '筹资现金流': f"{financing_cf/100000000:.2f}亿" if financing_cf != 0 else 'N/A',
                    })
                
                fundamentals['现金流走向'] = {
                    '最近3期现金流': cashflow_trend,
                    '趋势分析': self._analyze_cashflow_trend(recent_3_periods)
                }
            else:
                fundamentals['现金流走向'] = {'备注': '数据暂时无法获取'}
                
        except Exception as e:
            self.log(f"    ⚠️  现金流数据获取失败: {str(e)}")
            fundamentals['现金流走向'] = {'备注': '数据暂时无法获取'}
        
        return fundamentals
    
    def _analyze_cashflow_trend(self, df: pd.DataFrame) -> str:
        """分析现金流趋势"""
        if len(df) < 2:
            return "数据不足，无法分析趋势"
        
        try:
            # 对比最近两期经营现金流
            latest_cf = df.iloc[0].get('经营活动产生的现金流量净额(元)', 0)
            prev_cf = df.iloc[1].get('经营活动产生的现金流量净额(元)', 0)
            
            if latest_cf > prev_cf:
                return "✅ 经营现金流持续改善"
            elif latest_cf < prev_cf:
                return "⚠️ 经营现金流有所下降"
            else:
                return "➡️ 经营现金流基本稳定"
        except:
            return "趋势分析失败"
    
    def step3_capital_flow(self, stock: Dict) -> Dict:
        """
        第3步：资金动向
        指令词：结合整体股市，深度分析近1个月以来主力资金的流向，
               以及选中股票的量比，换手率，委比是否健康。
        """
        self.log(f"  💰 分析 {stock['name']} ({stock['code']}) 资金动向...")
        
        capital_data = {
            '整体股市资金流向': {},
            '个股资金流向': {},
            '交易活跃度': {}
        }
        
        try:
            # 1. 整体股市资金流向（大盘资金流向）
            self.log("    获取大盘资金流向...")
            df_market = ak.stock_market_fund_flow()
            
            if len(df_market) > 0:
                latest_market = df_market.iloc[0]
                capital_data['整体股市资金流向'] = {
                    '日期': latest_market.get('日期', 'N/A'),
                    '上证净流入': f"{latest_market.get('上证净流入(亿)', 'N/A')}亿",
                    '深证净流入': f"{latest_market.get('深证净流入(亿)', 'N/A')}亿",
                    '主力净流入': f"{latest_market.get('主力净流入(亿)', 'N/A')}亿",
                }
                
        except Exception as e:
            self.log(f"    ⚠️  大盘资金流向获取失败: {str(e)}")
            capital_data['整体股市资金流向'] = {'备注': '数据暂时无法获取'}
        
        try:
            # 2. 个股资金流向（近1个月）
            self.log("    获取个股资金流向...")
            market = "sh" if stock['code'].startswith('6') else "sz"
            df_flow = ak.stock_individual_fund_flow(stock=stock['code'], market=market)
            
            if len(df_flow) > 0:
                # 取最近一个月的数据
                recent_flow = df_flow.head(30) if len(df_flow) >= 30 else df_flow
                
                # 计算主力资金净流入
                main_inflow = recent_flow['主力净流入-净额'].sum() / 100000000  # 亿元
                retail_inflow = recent_flow['小单净流入-净额'].sum() / 100000000  # 亿元
                
                capital_data['个股资金流向'] = {
                    '近1月主力净流入': f"{main_inflow:.2f}亿",
                    '近1月散户净流入': f"{retail_inflow:.2f}亿",
                    '资金流向评估': self._assess_main_inflow(main_inflow)
                }
                
        except Exception as e:
            self.log(f"    ⚠️  个股资金流向获取失败: {str(e)}")
            capital_data['个股资金流向'] = {'备注': '数据暂时无法获取'}
        
        try:
            # 3. 交易活跃度指标（量比、换手率、委比）
            self.log("    获取交易活跃度数据...")
            df_realtime = ak.stock_zh_a_spot_em()
            stock_realtime = df_realtime[df_realtime['代码'] == stock['code']]
            
            if len(stock_realtime) > 0:
                row = stock_realtime.iloc[0]
                
                volume_ratio = row.get('量比', 'N/A')
                turnover_rate = row.get('换手率', 'N/A')
                
                # 尝试获取委比数据
                try:
                    df_quote = ak.stock_zh_a_hist_min_em(symbol=stock['code'], period='1', adjust='')
                    if len(df_quote) > 0:
                        latest_quote = df_quote.iloc[-1]
                        bid_price = latest_quote.get('买一', 0)
                        ask_price = latest_quote.get('卖一', 0)
                        if bid_price > 0 and ask_price > 0:
                            # 计算委比（简化版本）
                            bid_volume = latest_quote.get('买一量', 0)
                            ask_volume = latest_quote.get('卖一量', 0)
                            if bid_volume + ask_volume > 0:
                                commission_ratio = (bid_volume - ask_volume) / (bid_volume + ask_volume) * 100
                            else:
                                commission_ratio = 'N/A'
                        else:
                            commission_ratio = 'N/A'
                    else:
                        commission_ratio = 'N/A'
                except:
                    commission_ratio = 'N/A'
                
                capital_data['交易活跃度'] = {
                    '量比': volume_ratio,
                    '换手率': f"{turnover_rate}%" if turnover_rate != 'N/A' else 'N/A',
                    '委比': f"{commission_ratio}%" if commission_ratio != 'N/A' else 'N/A',
                    '活跃度评估': self._assess_activity(volume_ratio, turnover_rate)
                }
                
        except Exception as e:
            self.log(f"    ⚠️  交易活跃度获取失败: {str(e)}")
            capital_data['交易活跃度'] = {'备注': '数据暂时无法获取'}
        
        return capital_data
    
    def _assess_main_inflow(self, main_inflow: float) -> str:
        """评估主力资金流向"""
        if main_inflow > 5:
            return "✅ 非常健康（主力大幅流入）"
        elif main_inflow > 1:
            return "✅ 健康（主力持续流入）"
        elif main_inflow > -1:
            return "⚠️ 观望（资金相对平衡）"
        elif main_inflow > -5:
            return "⚠️ 谨慎（主力小幅流出）"
        else:
            return "❌ 异常（主力大幅流出）"
    
    def _assess_activity(self, volume_ratio, turnover_rate) -> str:
        """评估交易活跃度"""
        try:
            vr = float(volume_ratio) if volume_ratio != 'N/A' else 0
            tr = float(turnover_rate) if turnover_rate != 'N/A' else 0
            
            if vr >= 1.5 and tr >= 3:
                return "✅ 活跃（交投活跃，流动性好）"
            elif vr >= 0.8 and tr >= 1:
                return "➡️ 正常（交投平稳）"
            elif vr < 0.5 or tr < 0.5:
                return "⚠️ 低迷（交投清淡，流动性不足）"
            else:
                return "➡️ 正常"
        except:
            return "评估失败"
    
    def step4_future_growth(self, stock: Dict) -> Dict:
        """
        第4步：未来发展
        指令词：在其行业内的成长空间，以及公司发展方向是否有相关政策支持。
        """
        self.log(f"  🚀 分析 {stock['name']} ({stock['code']}) 未来发展...")
        
        growth_data = {
            '行业分析': {},
            '成长空间': {},
            '政策支持': {}
        }
        
        try:
            # 获取行业信息
            self.log("    获取行业分类信息...")
            
            # 尝试获取行业板块信息
            df_industry = ak.stock_board_industry_name_em()
            
            # 简化版本：根据股票名称和代码进行基础判断
            name = stock['name']
            industry_info = self._identify_industry(name)
            
            growth_data['行业分析'] = {
                '所属行业': industry_info['行业'],
                '行业地位': industry_info['地位']
            }
            
            growth_data['成长空间'] = {
                '评估': industry_info['成长空间'],
                '依据': industry_info['成长依据']
            }
            
            growth_data['政策支持'] = {
                '相关政策': industry_info['政策'],
                '影响分析': industry_info['政策影响']
            }
            
        except Exception as e:
            self.log(f"    ⚠️  行业信息获取失败: {str(e)}")
            growth_data = {
                '行业分析': {'备注': '建议手动查询行业分类'},
                '成长空间': {'备注': '建议分析行业报告'},
                '政策支持': {'备注': '建议关注相关政策动态'}
            }
        
        return growth_data
    
    def _identify_industry(self, name: str) -> Dict:
        """根据股票名称识别行业"""
        # 新能源相关
        if any(keyword in name for keyword in ['新能源', '锂电', '光伏', '风电', '储能']):
            return {
                '行业': '新能源',
                '地位': '成长期行业',
                '成长空间': '高',
                '成长依据': '碳中和背景下，新能源替代传统能源是大势所趋',
                '政策': '碳中和政策、新能源发展规划、补贴政策',
                '政策影响': '政策强力支持，但需关注补贴退坡影响'
            }
        # 半导体/芯片
        elif any(keyword in name for keyword in ['半导体', '芯片', '集成电路', '微电']):
            return {
                '行业': '半导体',
                '地位': '国家战略产业',
                '成长空间': '高',
                '成长依据': '国产替代需求强烈，技术突破带来成长空间',
                '政策': '集成电路产业政策、国产替代支持、研发补贴',
                '政策影响': '政策持续支持，但需关注国际技术限制'
            }
        # 医药生物
        elif any(keyword in name for keyword in ['医药', '生物', '医疗', '制药', '药']):
            return {
                '行业': '医药生物',
                '地位': '刚需行业',
                '成长空间': '中高',
                '成长依据': '人口老龄化带来持续需求，创新药有成长空间',
                '政策': '医疗改革、创新药支持、医保政策',
                '政策影响': '集采政策影响利润，创新药受鼓励'
            }
        # 银行
        elif any(keyword in name for keyword in ['银行']):
            return {
                '行业': '银行',
                '地位': '成熟行业',
                '成长空间': '中',
                '成长依据': '估值低，分红稳定，但成长性有限',
                '政策': '金融监管、利率政策、风险管理要求',
                '政策影响': '受利率政策影响大，监管趋严'
            }
        # 保险
        elif any(keyword in name for keyword in ['保险', '平安']):
            return {
                '行业': '保险',
                '地位': '成熟行业',
                '成长空间': '中',
                '成长依据': '保险渗透率提升空间，但竞争激烈',
                '政策': '保险监管、投资限制、偿付能力要求',
                '政策影响': '监管趋严，投资渠道受限'
            }
        # 消费
        elif any(keyword in name for keyword in ['白酒', '食品', '饮料', '家电']):
            return {
                '行业': '消费',
                '地位': '成熟行业',
                '成长空间': '中',
                '成长依据': '消费升级趋势，但需关注消费降级风险',
                '政策': '内需刺激政策、消费券、消费升级支持',
                '政策影响': '受经济周期影响，政策刺激消费'
            }
        else:
            return {
                '行业': '其他',
                '地位': '待分析',
                '成长空间': '需进一步研究',
                '成长依据': '建议查阅行业研究报告',
                '政策': '需关注相关政策动态',
                '政策影响': '需具体分析'
            }
    
    def step5_risk_warning(self, stock: Dict, fundamentals: Dict, capital: Dict) -> List[str]:
        """
        第5步：规避风险
        指令词：股票有可能存在的风险，分析出哪些因素可能会导致股价波动。
        """
        self.log(f"  ⚠️  分析 {stock['name']} ({stock['code']}) 风险因素...")
        
        risks = []
        
        # 1. 估值风险
        if stock['pe'] > 20:
            risks.append(f"估值风险：PE={stock['pe']}倍，估值偏高，存在回调风险")
        elif stock['pe'] < 8:
            risks.append(f"估值洼地：PE={stock['pe']}倍，可能存在市场担忧或行业问题")
        
        if stock['pb'] > 2.5:
            risks.append(f"资产溢价风险：PB={stock['pb']}倍，市值明显高于净资产")
        
        # 2. 财务风险
        financial_health = fundamentals.get('财务健康程度', {})
        if '资产负债率' in financial_health and financial_health['资产负债率'] != 'N/A':
            try:
                debt_ratio = float(financial_health['资产负债率'])
                if debt_ratio > 70:
                    risks.append(f"财务风险：资产负债率{debt_ratio:.1f}%，负债率过高")
                elif debt_ratio > 60:
                    risks.append(f"财务关注：资产负债率{debt_ratio:.1f}%，需关注负债结构")
            except:
                pass
        
        # 3. 资金流向风险
        capital_flow = capital.get('个股资金流向', {})
        if '近1月主力净流入' in capital_flow:
            try:
                inflow_str = capital_flow['近1月主力净流入'].replace('亿', '')
                inflow = float(inflow_str)
                if inflow < -10:
                    risks.append(f"资金风险：近1月主力净流出{abs(inflow):.2f}亿，主力大幅撤离")
                elif inflow < -5:
                    risks.append(f"资金关注：近1月主力净流出{abs(inflow):.2f}亿，需关注资金动向")
            except:
                pass
        
        # 4. 市场风险
        if abs(stock['change']) > 2:
            risks.append(f"波动风险：今日涨跌幅{stock['change']:.2f}%，短期波动较大")
        
        # 5. 流动性风险
        if stock['volume'] < 3:
            risks.append(f"流动性风险：成交额{stock['volume']:.2f}亿，流动性不足，大单交易可能影响股价")
        
        # 6. 整体市场风险
        market_flow = capital.get('整体股市资金流向', {})
        if '主力净流入' in market_flow:
            try:
                market_inflow_str = market_flow['主力净流入'].replace('亿', '')
                market_inflow = float(market_inflow_str)
                if market_inflow < -100:
                    risks.append(f"系统性风险：大盘主力净流出{abs(market_inflow):.0f}亿，市场整体承压")
            except:
                pass
        
        if not risks:
            risks.append("✅ 暂无明显风险信号，但仍需持续关注市场变化")
        
        return risks
    
    def generate_report(self, stocks: List[Dict]) -> str:
        """生成完整的荐股分析报告"""
        self.log("\n📝 生成分析报告...")
        
        report = []
        report.append(f"# 📈 A股荐股分析报告\n")
        report.append(f"**日期：** {self.today}\n")
        report.append(f"**分析模型：** GLM-5 | **数据来源：** Akshare\n")
        report.append(f"\n---\n")
        
        for i, stock in enumerate(stocks, 1):
            report.append(f"\n## 🎯 精选股票 {i}：{stock['name']} ({stock['code']})\n")
            report.append(f"\n**💰 当前价格：** ¥{stock['price']} | **今日涨跌：** {stock['change']}%\n")
            report.append(f"**📊 综合得分：** {stock['score']}/100\n")
            
            # 执行2-5步分析
            fundamentals = self.step2_fundamentals(stock)
            capital = self.step3_capital_flow(stock)
            future = self.step4_future_growth(stock)
            risks = self.step5_risk_warning(stock, fundamentals, capital)
            
            # 第1步：初步筛选
            report.append(f"\n### 1️⃣ 初步筛选\n")
            report.append(f"\n**价值因子：**\n")
            report.append(f"- PE（市盈率）：{stock['pe']}倍 | 得分：{stock['pe_score']}/30\n")
            report.append(f"- PB（市净率）：{stock['pb']}倍 | 得分：{stock['pb_score']}/30\n")
            report.append(f"\n**质量因子：**\n")
            report.append(f"- 流动性（成交额）：{stock['volume']}亿 | 得分：{stock['liquidity_score']}/20\n")
            report.append(f"- 稳定性（涨跌幅）：{stock['change']}% | 得分：{stock['stability_score']}/20\n")
            
            # 第2步：确认基本盘
            report.append(f"\n### 2️⃣ 确认基本盘\n")
            
            report.append(f"\n**财务健康程度：**\n")
            for key, value in fundamentals['财务健康程度'].items():
                report.append(f"- {key}：{value}\n")
            
            report.append(f"\n**盈利趋势：**\n")
            for key, value in fundamentals['盈利趋势'].items():
                report.append(f"- {key}：{value}\n")
            
            report.append(f"\n**现金流走向：**\n")
            if '最近3期现金流' in fundamentals['现金流走向']:
                for cf in fundamentals['现金流走向']['最近3期现金流']:
                    report.append(f"- {cf['报告期']}：经营{cf['经营现金流']} / 投资{cf['投资现金流']} / 筹资{cf['筹资现金流']}\n")
                report.append(f"- **趋势分析：** {fundamentals['现金流走向']['趋势分析']}\n")
            else:
                for key, value in fundamentals['现金流走向'].items():
                    report.append(f"- {key}：{value}\n")
            
            # 第3步：资金动向
            report.append(f"\n### 3️⃣ 资金动向\n")
            
            report.append(f"\n**整体股市资金流向：**\n")
            for key, value in capital['整体股市资金流向'].items():
                report.append(f"- {key}：{value}\n")
            
            report.append(f"\n**个股资金流向：**\n")
            for key, value in capital['个股资金流向'].items():
                report.append(f"- {key}：{value}\n")
            
            report.append(f"\n**交易活跃度：**\n")
            for key, value in capital['交易活跃度'].items():
                report.append(f"- {key}：{value}\n")
            
            # 第4步：未来发展
            report.append(f"\n### 4️⃣ 未来发展\n")
            
            report.append(f"\n**行业分析：**\n")
            for key, value in future['行业分析'].items():
                report.append(f"- {key}：{value}\n")
            
            report.append(f"\n**成长空间：**\n")
            for key, value in future['成长空间'].items():
                report.append(f"- {key}：{value}\n")
            
            report.append(f"\n**政策支持：**\n")
            for key, value in future['政策支持'].items():
                report.append(f"- {key}：{value}\n")
            
            # 第5步：规避风险
            report.append(f"\n### 5️⃣ 规避风险 ⚠️\n")
            for risk in risks:
                report.append(f"- {risk}\n")
            
            report.append(f"\n---\n")
        
        report.append(f"\n⚠️ **免责声明：** 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。\n")
        
        return "".join(report)
    
    def run(self) -> str:
        """运行完整的荐股分析流程"""
        self.log("🦞 开始A股荐股分析...")
        self.log("=" * 60)
        
        # 第1步：筛选股票
        stocks = self.step1_screening()
        
        if not stocks:
            return "❌ 未能筛选出符合条件的股票，请稍后重试"
        
        # 生成完整报告（包含2-5步分析）
        report = self.generate_report(stocks)
        
        self.log("=" * 60)
        self.log("✅ 荐股分析完成！")
        return report


def main():
    """主函数"""
    analyzer = StockAnalyzer()
    report = analyzer.run()
    
    # 打印报告
    print("\n" + "=" * 60)
    print(report)
    
    # 保存报告到文件
    report_dir = "/Users/glenman/.openclaw/workspace/memory"
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"stock-analysis-{datetime.now().strftime('%Y-%m-%d')}.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 报告已保存至：{report_file}")
    
    return report


if __name__ == "__main__":
    main()
