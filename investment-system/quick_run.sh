# 投资分析系统 - 快速启动脚本
# 使用方法：./investment-system/quick_run.sh

#!/bin/bash

cd /Users/glenman/.openclaw/workspace
python3 investment-system/run_daily_analysis.py

# 如果需要在运行后推送到飞书，取消下面这行的注释
# cat memory/investment/daily/daily_report_$(date +%Y-%m-%d).md | <推送命令>
