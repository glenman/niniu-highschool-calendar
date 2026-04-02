#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据采集器 v2 - 支持分批获取，避免超时
"""

import urllib.request
import urllib.error
import json
import time


class StockDataFetcher:
    """股票数据采集器 v2"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.api_endpoints = {
            'stock_list': 'https://push2.eastmoney.com/api/qt/clist/get'
        }
    
    def _fetch_url(self, url, params=None):
        """URL请求方法"""
        try:
            if params:
                param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
                full_url = f"{url}?{param_str}"
            else:
                full_url = url
            
            req = urllib.request.Request(full_url, headers=self.headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")
            return None
    
    def get_stock_list(self, limit=2000):
        """获取A股股票列表（分批获取）"""
        try:
            print(f"📊 获取A股实时行情（目标{limit}只）...")
            
            all_stocks = []
            batch_size = 500
            batches = (limit + batch_size - 1) // batch_size
            
            for batch in range(batches):
                params = {
                    'pn': batch + 1,
                    'pz': batch_size,
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
                    print(f"  ⚠️  第{batch+1}批数据获取失败，跳过")
                    time.sleep(1)
                    continue
                
                # 处理数据
                for item in data['data']['diff']:
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
                        '成交量': safe_int(item.get('f5')),
                        '成交额': safe_int(item.get('f6')),
                        '换手率': safe_float(item.get('f8')),
                        '市盈率': safe_float(item.get('f9')),
                        '量比': safe_float(item.get('f10')),
                        '市净率': safe_float(item.get('f23')),
                    }
                    all_stocks.append(stock)
                
                print(f"  ✅ 第{batch+1}批完成，累计{len(all_stocks)}只")
                
                # 达到目标数量
                if len(all_stocks) >= limit:
                    break
                
                # 批次间休息，避免请求过快
                time.sleep(0.5)
            
            if all_stocks:
                print(f"  ✅ 总计获取{len(all_stocks)}只股票")
                return all_stocks[:limit]
            else:
                print("  ❌ 未获取到任何股票数据")
                return None
        
        except Exception as e:
            print(f"  ❌ 获取股票列表失败: {e}")
            return None
    
    def search_by_keywords(self, stock_list, keywords):
        """按关键词搜索股票"""
        results = []
        for stock in stock_list:
            name = stock.get('名称', '')
            for keyword in keywords:
                if keyword in name:
                    results.append(stock)
                    break
        return results
