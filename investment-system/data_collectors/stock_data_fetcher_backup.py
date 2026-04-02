#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据采集器 - 使用urllib（无需额外安装包）
"""

import urllib.request
import urllib.error
import json
from datetime import datetime
import sys
import os
import csv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class StockDataFetcher:
    """股票数据采集器 - 使用urllib"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # 东方财富API端点
        self.api_endpoints = {
            'stock_list': 'https://push2.eastmoney.com/api/qt/clist/get',
            'north_fund': 'https://push2.eastmoney.com/api/qt/stock/fflow/kline/get'
        }
    
    def _fetch_url(self, url, params=None):
        """通用的URL请求方法"""
        try:
            # 构建完整URL
            if params:
                param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
                full_url = f"{url}?{param_str}"
            else:
                full_url = url
            
            # 创建请求
            req = urllib.request.Request(full_url, headers=self.headers)
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        
        except urllib.error.URLError as e:
            print(f"❌ 网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            return None
    
    def get_stock_list(self, limit=500):
        """获取A股股票列表（实时行情）- 分批获取避免超时"""
        try:
            print(f"📊 获取A股实时行情（目标{limit}只）...")
            
            all_stocks = []
            batch_size = 500  # 每批500只
            batches = (limit + batch_size - 1) // batch_size  # 计算批次
            
            for batch in range(batches):
                start = batch * batch_size + 1
                
                # 东方财富API参数
                params = {
                    'pn': batch + 1,  # 页码
                    'pz': batch_size,  # 每页数量
                    'po': 1,
                    'np': 1,
                    'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                    'fltt': 2,
                    'invt': 2,
                    'fid': 'f3',
                    'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
                    'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
                }
                
                print(f"  正在获取第{batch+1}/{batches}批...")
                data = self._fetch_url(self.api_endpoints['stock_list'], params)
                
                if not data or not data.get('data') or not data['data'].get('diff'):
                    print(f"  ⚠️ 第{batch+1}批数据获取失败")
                    continue
                
                # 处理当前批次数据
                for item in data['data']['diff']:
                    # 安全的数值转换函数
                    def safe_float(val, divisor=100):
                        try:
                            if val is None or val == '-':
                                return 0
                            return float(val) / divisor
                        except:
                            return 0
                    
                    def safe_int(val):
                        try:
                            if val is None or val == '-':
                                return 0
                            return int(val)
                        except:
                            return 0
                    
                    stock = {
                        '代码': item.get('f12', ''),
                        '名称': item.get('f14', ''),
                        '最新价': safe_float(item.get('f2')),
                        '涨跌幅': safe_float(item.get('f3')),
                        '涨跌额': safe_float(item.get('f4')),
                        '成交量': safe_int(item.get('f5')),
                        '成交额': safe_int(item.get('f6')),
                        '换手率': safe_float(item.get('f8')),
                        '市盈率': safe_float(item.get('f9')),
                        '振幅': safe_float(item.get('f7')),
                        '最高': safe_float(item.get('f15')),
                        '最低': safe_float(item.get('f16')),
                        '今开': safe_float(item.get('f17')),
                        '昨收': safe_float(item.get('f18')),
                        '量比': safe_float(item.get('f10')),
                        '市净率': safe_float(item.get('f23')),
                    }
                    all_stocks.append(stock)
                
                # 如果已达到目标数量，提前退出
                if len(all_stocks) >= limit:
                    break
            
            if all_stocks:
                print(f"  ✅ 成功获取{len(all_stocks)}只股票数据")
                return all_stocks[:limit]
                    # 安全的数值转换函数
                    def safe_float(val, divisor=100):
                        try:
                            if val is None or val == '-':
                                return 0
                            return float(val) / divisor
                        except:
                            return 0
                    
                    def safe_int(val):
                        try:
                            if val is None or val == '-':
                                return 0
                            return int(val)
                        except:
                            return 0
                    
                    stock = {
                        '代码': item.get('f12', ''),
                        '名称': item.get('f14', ''),
                        '最新价': safe_float(item.get('f2')),
                        '涨跌幅': safe_float(item.get('f3')),
                        '涨跌额': safe_float(item.get('f4')),
                        '成交量': safe_int(item.get('f5')),
                        '成交额': safe_int(item.get('f6')),
                        '换手率': safe_float(item.get('f8')),
                        '市盈率': safe_float(item.get('f9')),
                        '振幅': safe_float(item.get('f7')),
                        '最高': safe_float(item.get('f15')),
                        '最低': safe_float(item.get('f16')),
                        '今开': safe_float(item.get('f17')),
                        '昨收': safe_float(item.get('f18')),
                        '量比': safe_float(item.get('f10')),
                        '市净率': safe_float(item.get('f23')),
                    }
                    stocks.append(stock)
            
            print("❌ 所有批次数据获取失败")
            return None
            
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return None
    
    def get_north_fund(self):
        """获取北向资金数据"""
        try:
            print("🌏 获取北向资金...")
            
            params = {
                'lmt': 5,
                'klt': 101,
                'secid': '1',  # 沪股通
                'fields1': 'f1,f2,f3,f7',
                'fields2': 'f51,f52,f53,f54,f55,f56',
                'ut': 'b2884a393a59ad64002292a3e90d46a5'
            }
            
            data = self._fetch_url(self.api_endpoints['north_fund'], params)
            
            if data and data.get('data') and data['data'].get('klines'):
                latest = data['data']['klines'][0].split(',')
                result = {
                    '日期': latest[0],
                    '当日净流入': float(latest[1]) if latest[1] else 0,
                    '当日余额': float(latest[2]) if latest[2] else 0
                }
                print(f"  ✅ 北向资金净流入: {result['当日净流入']:.2f}亿元")
                return result
            
            print("  ⚠️ 北向资金数据获取失败")
            return None
            
        except Exception as e:
            print(f"❌ 获取北向资金失败: {e}")
            return None
    
    def screen_stocks(self, stock_list):
        """多因子选股"""
        print("\n🔍 开始多因子筛选...")
        
        if not stock_list:
            print("❌ 无股票数据")
            return None
        
        screened = stock_list.copy()
        
        # 1. 过滤ST股票
        before = len(screened)
        screened = [s for s in screened if 'ST' not in s['名称'] and '退市' not in s['名称']]
        print(f"  ✅ 过滤ST股票: {before} → {len(screened)}只")
        
        # 2. 过滤停牌和极端波动（非交易时间放宽条件）
        before = len(screened)
        
        # 检查是否为交易时间（有涨跌幅和成交量数据）
        has_trading_data = any(s['涨跌幅'] != 0 or s['成交量'] > 0 for s in screened)
        
        if has_trading_data:
            # 交易时间：严格过滤
            screened = [
                s for s in screened 
                if s['涨跌幅'] != 0 
                and abs(s['涨跌幅']) < 10 
                and s['成交量'] > 0
            ]
            print(f"  ✅ 过滤停牌/极端波动（交易时间）: {before} → {len(screened)}只")
        else:
            # 非交易时间：跳过涨跌幅和成交量过滤，只过滤ST
            print(f"  ⏰ 非交易时间，跳过涨跌幅/成交量过滤: {before} → {len(screened)}只")
        
        # 3. 市盈率筛选（5-100倍，非交易时间放宽为0-100）
        before = len(screened)
        if has_trading_data:
            screened = [s for s in screened if 5 < s['市盈率'] < 100]
        else:
            # 非交易时间：允许PE为0或合理范围
            screened = [s for s in screened if s['市盈率'] < 100]
        print(f"  ✅ PE筛选(5-100): {before} → {len(screened)}只")
        
        # 4. 换手率筛选（非交易时间放宽条件）
        before = len(screened)
        if has_trading_data:
            screened = [s for s in screened if 0.01 < s['换手率'] < 50]
        else:
            # 非交易时间：跳过滤换手率过滤
            pass
        print(f"  ✅ 换手率筛选(0.01%-50%): {before} → {len(screened)}只")
        
        # 5. 综合评分
        print("\n📊 计算综合评分...")
        for stock in screened:
            score = 0
            
            # 涨跌幅（适度上涨更好）
            score += min(max(stock['涨跌幅'], 0), 5) * 2
            
            # 换手率（适中最好，3%左右最优）
            turnover_score = 10 - abs(stock['换手率'] - 3)
            score += min(max(turnover_score, 0), 5)
            
            # 市盈率（适中最好，20倍左右最优）
            pe_score = 10 - abs(stock['市盈率'] - 20) / 5
            score += min(max(pe_score, 0), 5)
            
            stock['评分'] = score
        
        # 按评分排序
        screened.sort(key=lambda x: x['评分'], reverse=True)
        
        # 取前30名
        top_stocks = screened[:30]
        print(f"  ✅ 筛选完成，TOP30已选出")
        
        return top_stocks


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 A股投资分析系统 - 数据采集模块")
    print("=" * 60)
    
    fetcher = StockDataFetcher()
    
    # 1. 获取股票列表
    stock_list = fetcher.get_stock_list(limit=3000)
    
    if stock_list:
        # 2. 多因子筛选
        screened = fetcher.screen_stocks(stock_list)
        
        # 3. 获取北向资金
        north_fund = fetcher.get_north_fund()
        
        # 4. 保存结果
        today = datetime.now().strftime('%Y-%m-%d')
        output_dir = "memory/investment/daily"
        os.makedirs(output_dir, exist_ok=True)
        
        if screened:
            # 保存为CSV
            csv_file = f"{output_dir}/screened_stocks_{today}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                if screened:
                    writer = csv.DictWriter(f, fieldnames=screened[0].keys())
                    writer.writeheader()
                    writer.writerows(screened)
            print(f"\n✅ 筛选结果已保存: {csv_file}")
            
            # 显示TOP10
            print("\n📈 今日TOP10推荐股票:")
            print("-" * 80)
            for i, stock in enumerate(screened[:10], 1):
                print(f"{i:>2}. {stock['代码']:>8} {stock['名称']:<10} "
                      f"价格:{stock['最新价']:>7.2f} "
                      f"涨跌:{stock['涨跌幅']:>6.2f}% "
                      f"PE:{stock['市盈率']:>6.2f} "
                      f"换手:{stock['换手率']:>5.2f}% "
                      f"评分:{stock['评分']:>5.1f}")
        
        if north_fund:
            json_file = f"{output_dir}/north_fund_{today}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(north_fund, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 北向资金已保存: {json_file}")
        
        return screened
    
    return None


if __name__ == '__main__':
    main()
