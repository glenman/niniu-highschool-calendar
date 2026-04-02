#!/bin/bash
# 监控抓取进度

while true; do
    COUNT=$(ls ~/.openclaw/workspace/shanghaiport-fc-app/data/match-reports-100percent/*.json 2>/dev/null | wc -l)
    echo "[$(date '+%H:%M:%S')] 已完成: $COUNT/29"
    
    if [ "$COUNT" -ge 29 ]; then
        echo "✅ 全部完成！"
        break
    fi
    
    sleep 60
done
