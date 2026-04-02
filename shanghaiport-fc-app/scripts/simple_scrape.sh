#!/bin/bash

cd /Users/glenman/.openclaw/workspace/shanghaiport-fc-app

echo "开始抓取30场比赛数据..."
echo "========================================"
echo ""

counter=0
total=30

while IFS='|' read -r round url; do
  counter=$((counter + 1))
  echo "[$counter/$total] 第${round}轮"

  output_file="data/scraped_html/match_${round}.html"

  # 使用agent-browser获取HTML
  echo "  正在抓取..."

  # 打开URL
  agent-browser --cdp 9222 open "$url" > /dev/null 2>&1

  # 等待页面加载
  sleep 5

  # 获取HTML
  agent-browser --cdp 9222 eval "document.documentElement.outerHTML" > "$output_file" 2>&1

  if [ -s "$output_file" ]; then
    size=$(wc -c < "$output_file" | awk '{print int($1/1024)}')
    echo "  ✓ 已保存 (${size}KB)"
  else
    echo "  ✗ 抓取失败"
  fi

  echo ""

  # 避免请求过快
  if [ $counter -lt $total ]; then
    sleep 2
  fi

done < <(cat data/match_urls.json | jq -r '.[] | "\(.index)|\(.url)"')

echo "========================================"
echo "抓取完成！"
echo "共抓取: $(ls data/scraped_html/*.html 2>/dev/null | wc -l | xargs) 个文件"
