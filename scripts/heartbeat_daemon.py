#!/usr/bin/env python3
"""
Heartbeat守护进程 - 替代cron的定时任务
每30分钟检查一次，在8:30-9:00执行A股投资分析
"""
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
log_file = Path("/tmp/heartbeat_daemon.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def should_run_analysis():
    """检查是否应该执行分析（8:30-9:00）"""
    now = datetime.now()
    return now.hour == 8 and 30 <= now.minute <= 59

def run_analysis():
    """执行A股投资分析"""
    try:
        logger.info("开始执行A股投资分析...")
        
        # 运行整合版系统
        result = subprocess.run(
            ['python3', 'investment-system/run_integrated_system.py'],
            cwd='/Users/glenman/.openclaw/workspace',
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            logger.info("✅ 分析完成")
        else:
            logger.error(f"❌ 分析失败: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("❌ 分析超时（超过5分钟）")
    except Exception as e:
        logger.error(f"❌ 执行出错: {e}")

def main():
    """主循环"""
    logger.info("🦞 Heartbeat守护进程启动")
    logger.info("检查间隔: 30分钟")
    logger.info("执行时间: 8:30-9:00")
    
    last_run_date = None
    
    while True:
        try:
            now = datetime.now()
            today = now.date()
            
            # 检查是否应该执行
            if should_run_analysis() and last_run_date != today:
                logger.info(f"⏰ 到达执行时间窗口 ({now.strftime('%H:%M')})")
                run_analysis()
                last_run_date = today
            
            # 每30分钟检查一次
            time.sleep(1800)  # 30分钟 = 1800秒
            
        except KeyboardInterrupt:
            logger.info("👋 收到停止信号，退出守护进程")
            break
        except Exception as e:
            logger.error(f"❌ 主循环出错: {e}")
            time.sleep(60)  # 出错后等待1分钟

if __name__ == '__main__':
    main()
