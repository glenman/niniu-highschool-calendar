#!/bin/bash
# 进度监控脚本 - 每5分钟自动检查一次

OUTPUT_DIR="$HOME/.openclaw/workspace/shanghaiport-fc-app/data/match-reports-100percent"
LOG_FILE="/tmp/scraper_progress.log"

echo "开始监控抓取进度..." > "$LOG_FILE"
echo "目标: 29场比赛" >> "$LOG_FILE"

while true; do
    COUNT=$(ls "$OUTPUT_DIR"/*.json 2>/dev/null | wc -l)
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$TIMESTAMP] 已完成: $COUNT/29" | tee -a "$LOG_FILE"
    
    if [ "$COUNT" -ge 29 ]; then
        echo "[$TIMESTAMP] ✅ 全部完成！" | tee -a "$LOG_FILE"
        echo "" >> "$LOG_FILE"
        echo "文件列表:" >> "$LOG_FILE"
        ls -lh "$OUTPUT_DIR"/*.json >> "$LOG_FILE"
        break
    fi
    
    sleep 300  # 每5分钟检查一次
done
