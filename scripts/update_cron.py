#!/usr/bin/env python3
"""更新cron任务"""
import subprocess

# 当前cron任务
current = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
current_cron = current.stdout

# 要添加的任务
heartbeat_task = """
# OpenClaw Heartbeat - 每30分钟检查（8:30-9:00执行投资分析）
*/30 * * * * /bin/bash /Users/glenman/.openclaw/workspace/scripts/trigger_heartbeat.sh >> /tmp/heartbeat.log 2>&1
"""

# 检查是否已存在
if 'trigger_heartbeat' not in current_cron:
    new_cron = current_cron + heartbeat_task
    
    # 更新cron
    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
    process.communicate(input=new_cron)
    process.wait()
    
    print("✅ Cron任务已添加")
else:
    print("⚠️  Cron任务已存在")

# 显示当前cron
result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
print("\n当前Cron任务:")
print(result.stdout)
