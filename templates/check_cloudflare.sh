#!/bin/bash
# 监控页面状态，等待 Cloudflare 验证通过

echo "开始监控页面状态..."

for i in {1..20}; do
    TITLE=$(agent-browser eval "document.title" 2>&1 | tr -d '"')
    URL=$(agent-browser get url 2>&1)

    echo "[$i/20] 标题: $TITLE"
    echo "      URL: $URL"

    # 检查是否已经跳转到实际页面
    if [[ "$TITLE" != *"请稍候"* ]] && [[ "$TITLE" != *"执行安全验证"* ]] && [[ "$TITLE" != "" ]]; then
        echo ""
        echo "✅ 检测到页面已加载！"
        echo "页面标题: $TITLE"

        # 等待页面完全加载
        sleep 2
        agent-browser wait --load networkidle

        # 保存完整页面
        echo "正在保存页面数据..."
        agent-browser snapshot --json > /tmp/fbref_loaded.json
        agent-browser eval "document.body.innerHTML" > /tmp/fbref_html.html

        echo "✅ 数据已保存"
        exit 0
    fi

    sleep 2
done

echo ""
echo "⏰ 超时：页面未在预期时间内加载"
exit 1
