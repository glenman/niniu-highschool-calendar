#!/bin/bash

while true; do
  count=$(ls shanghaiport-fc-app/data/scraped_html/*.html 2>/dev/null | wc -l | xargs)
  echo "$(date '+%H:%M:%S') - 已抓取: $count/30 个文件"
  if [ "$count" -ge 30 ]; then
    echo "✅ 抓取完成！"
    break
  fi
  sleep 5
done
