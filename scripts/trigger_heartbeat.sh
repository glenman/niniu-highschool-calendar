#!/bin/bash
# Heartbeat触发脚本 - A股投资分析
# 在指定时间窗口执行分析任务

cd /Users/glenman/.openclaw/workspace

LOG_FILE="/tmp/heartbeat.log"
CURRENT_HOUR=$(date +%H)
CURRENT_MINUTE=$(date +%M)

echo "$(date '+%Y-%m-%d %H:%M:%S') - Heartbeat check (hour=$CURRENT_HOUR, minute=$CURRENT_MINUTE)" >> "$LOG_FILE"

# 检查是否在执行时间窗口（8:30-9:00）
if [ "$CURRENT_HOUR" -eq 8 ] && [ "$CURRENT_MINUTE" -ge 30 ] && [ "$CURRENT_MINUTE" -le 59 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Within time window, executing A-share analysis..." >> "$LOG_FILE"
    
    # 执行整合版投资分析
    /opt/homebrew/bin/python3 investment-system/run_integrated_system.py >> "$LOG_FILE" 2>&1
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Analysis completed" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Outside time window, skipping" >> "$LOG_FILE"
fi
