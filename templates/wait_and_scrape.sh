#!/bin/bash
# 等待用户手动完成Cloudflare验证，然后抓取数据

echo "========================================="
echo "等待 Cloudflare 验证..."
echo "请在浏览器窗口中完成验证"
echo "========================================="
echo ""

PREV_TITLE=""
for i in {1..30}; do
    # 获取页面标题
    TITLE=$(agent-browser eval "document.title" 2>&1 | tr -d '"')

    # 如果标题变化了，显示新状态
    if [[ "$TITLE" != "$PREV_TITLE" ]]; then
        echo "[$(date +%H:%M:%S)] 页面状态变化: $TITLE"
        PREV_TITLE="$TITLE"
    fi

    # 检查是否已经通过验证
    if [[ "$TITLE" != *"请稍候"* ]] && [[ "$TITLE" != *"执行安全验证"* ]] && [[ "$TITLE" != *"Cloudflare"* ]] && [[ "$TITLE" != "" ]]; then
        echo ""
        echo "========================================="
        echo "✅ 检测到页面已加载！"
        echo "========================================="
        echo "页面标题: $TITLE"
        echo ""

        # 等待页面完全加载
        echo "等待页面完全加载..."
        agent-browser wait --load networkidle
        sleep 2

        # 抓取数据
        echo "开始抓取比赛数据..."

        # 1. 保存完整快照
        echo "  - 保存页面快照..."
        agent-browser snapshot --json > /tmp/fbref_match_snapshot.json

        # 2. 保存HTML
        echo "  - 保存HTML源码..."
        agent-browser eval "document.body.innerHTML" > /tmp/fbref_match_html.html

        # 3. 截图
        echo "  - 保存页面截图..."
        agent-browser screenshot --full /tmp/fbref_match_screenshot.png

        # 4. 提取关键数据
        echo "  - 提取比赛信息..."
        agent-browser eval "
        (function() {
            var data = {
                title: document.title,
                url: window.location.href,
                date: document.querySelector('.scorebox_meta')?.textContent || '',
                home_team: document.querySelector('.scorebox .home-team')?.textContent?.trim() || '',
                away_team: document.querySelector('.scorebox .away-team')?.textContent?.trim() || '',
                score: document.querySelector('.scorebox .score')?.textContent?.trim() || ''
            };
            return JSON.stringify(data);
        })()
        " > /tmp/fbref_basic_info.json

        echo ""
        echo "========================================="
        echo "✅ 数据抓取完成！"
        echo "========================================="
        echo "文件位置:"
        echo "  - 快照: /tmp/fbref_match_snapshot.json"
        echo "  - HTML: /tmp/fbref_match_html.html"
        echo "  - 截图: /tmp/fbref_match_screenshot.png"
        echo "  - 信息: /tmp/fbref_basic_info.json"
        echo ""

        exit 0
    fi

    # 每5秒显示一次等待提示
    if [ $((i % 5)) -eq 0 ]; then
        echo "[$(date +%H:%M:%S)] 等待中... ($i/30)"
    fi

    sleep 2
done

echo ""
echo "========================================="
echo "⏰ 等待超时"
echo "========================================="
echo "60秒内未检测到页面加载完成"
echo ""
echo "可能的原因:"
echo "  1. Cloudflare 验证需要更长时间"
echo "  2. 需要手动完成验证"
echo "  3. 网络连接问题"
echo ""

exit 1
