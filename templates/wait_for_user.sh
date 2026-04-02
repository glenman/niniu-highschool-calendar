#!/bin/bash
# 持续监控页面变化，等待用户完成验证

echo "开始监控页面变化..."
echo "请在浏览器窗口中点击 Cloudflare 验证框"

for i in {1..60}; do
    # 获取页面标题
    TITLE=$(agent-browser eval "document.title" 2>&1 | tr -d '"')

    # 检查是否已经通过验证
    if [[ "$TITLE" != *"请稍候"* ]] && [[ "$TITLE" != *"执行安全验证"* ]] && [[ "$TITLE" != *"fbref.com"* ]]; then
        echo ""
        echo "✅ 检测到页面变化！"
        echo "新标题: $TITLE"
        echo "开始抓取数据..."

        # 等待页面完全加载
        agent-browser wait --load networkidle

        # 保存页面快照
        agent-browser snapshot --json > /tmp/fbref_match_data.json
        echo "✅ 数据已保存到 /tmp/fbref_match_data.json"

        exit 0
    fi

    # 每5秒显示一次状态
    if [ $((i % 5)) -eq 0 ]; then
        echo "[$i/60] 等待验证... 当前标题: $TITLE"
    fi

    sleep 1
done

echo ""
echo "⏰ 超时：60秒内未检测到页面变化"
exit 1
