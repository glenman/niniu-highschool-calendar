#!/bin/bash
# 启动Heartbeat守护进程

cd /Users/glenman/.openclaw/workspace

# 检查是否已经在运行
if pgrep -f "heartbeat_daemon.py" > /dev/null; then
    echo "⚠️  Heartbeat守护进程已在运行"
    echo "进程ID: $(pgrep -f heartbeat_daemon.py)"
    exit 1
fi

# 启动守护进程（后台运行）
nohup python3 scripts/heartbeat_daemon.py > /tmp/heartbeat_daemon.out 2>&1 &

echo "✅ Heartbeat守护进程已启动"
echo "日志文件: /tmp/heartbeat_daemon.log"
echo "进程ID: $(pgrep -f heartbeat_daemon.py)"
echo ""
echo "停止方法: pkill -f heartbeat_daemon.py"
