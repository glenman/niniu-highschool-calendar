#!/bin/bash

# 重新抓取16场比赛的数据
INPUT_FILE="./data/matches_to_rescrape.json"
OUTPUT_DIR="./data/rescraped_matches"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "开始重新抓取比赛数据"
echo "=========================================="
echo ""

# 读取JSON并逐个处理
node -e "
const fs = require('fs');
const matches = JSON.parse(fs.readFileSync('$INPUT_FILE', 'utf8'));
matches.forEach((match, i) => {
  console.log(\`\${i + 1}|\${match.round}|\${match.date}|\${match.url}\`);
});
" | while IFS='|' read -r index round date url; do
  echo "[$index/16] 正在抓取第${round}轮 ($date)"
  echo "  URL: $url"

  OUTPUT_FILE="$OUTPUT_DIR/match_round_${round}.json"

  # 使用agent-browser抓取页面
  echo "  正在打开页面..."
  agent-browser open "$url" --timeout 30000 > /dev/null 2>&1

  # 等待页面加载
  sleep 3

  # 获取accessibility tree
  echo "  正在提取数据..."
  agent-browser snapshot --json > "$OUTPUT_FILE" 2>&1

  if [ $? -eq 0 ]; then
    echo "  ✓ 已保存: $OUTPUT_FILE"
  else
    echo "  ✗ 抓取失败"
  fi

  # 关闭浏览器
  agent-browser close > /dev/null 2>&1

  echo ""

  # 避免请求过快
  sleep 2
done

echo "=========================================="
echo "抓取完成！"
echo "=========================================="
echo ""
echo "文件保存位置: $OUTPUT_DIR"
