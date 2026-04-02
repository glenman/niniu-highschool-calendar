#!/bin/bash
# 监控页面变化脚本

for i in {1..30}; do
    echo "检查第 $i 次..."

    # 获取页面标题
    TITLE=$(agent-browser eval "document.title" 2>&1 | tr -d '"')

    echo "当前标题: $TITLE"

    # 如果标题不再是"请稍候..."，说明验证通过
    if [[ "$TITLE" != *"请稍候"* ]] && [[ "$TITLE" != *"执行安全验证"* ]]; then
        echo "✅ 页面已加载！开始抓取数据..."
        agent-browser snapshot --json > /tmp/fbref_loaded.json
        exit 0
    fi

    sleep 2
done

echo "⏰ 超时：30秒内页面未加载"
exit 1
