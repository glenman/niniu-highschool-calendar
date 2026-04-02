#!/bin/bash
# 通过SOCKS5代理获取贵金属价格

PROXY="socks5://127.0.0.1:28310"

# 尝试多个数据源
echo "Fetching precious metals prices via proxy..."

# 方法1: Kitco (可能需要JS渲染)
# 方法2: 使用更简单的API
# 方法3: 从新闻中提取

# 尝试Barchart API (更简单)
curl -x $PROXY -s "https://www.barchart.com/futures/quotes/GCK26" 2>&1 | grep -o '\$[0-9,.]*' | head -1

# 或从MarketWatch提取
curl -x $PROXY -s "https://www.marketwatch.com/investing/future/gold" 2>&1 | grep -i "gold.*price\|[0-9],[0-9][0-9][0-9]\." | head -5
