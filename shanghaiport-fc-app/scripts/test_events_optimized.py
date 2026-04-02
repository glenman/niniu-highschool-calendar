#!/usr/bin/env python3
"""
优化版 - 提取events数据
基于实际页面结构分析
"""

import json
import subprocess
import time
import re

url = 'https://fbref.com/en/matches/13f114b6/Wuhan-Three-Towns-Shanghai-Port-April-15-2023-Chinese-Super-League'

print("="*60)
print("优化版 - 提取events数据")
print("="*60)
print()

# 1. 打开页面
print("→ 打开页面...")
subprocess.run(['agent-browser', '--cdp', '9222', 'open', url], 
               capture_output=True, text=True, timeout=30)
time.sleep(10)
print("✓ 页面已加载\n")

# 2. 提取events
print("→ 提取events...")

js_code = """(() => {
  const events = [];
  const body = document.body.innerText;
  const lines = body.split('\\n');
  
  // 方法1: 查找特定格式 "分钟 | 比分 | 球员 | ..."
  lines.forEach(line => {
    // 进球格式: "64' | 0:1 | Paulinho | Assist: Wu Lei"
    const goalMatch = line.match(/(\\d+)(?:\\+(\\d+))?['']\\s*\\|\\s*(\\d+):(\\d+)\\s*\\|\\s*([^|]+)/);
    if (goalMatch) {
      const minute = parseInt(goalMatch[1]);
      const extra = goalMatch[2] ? parseInt(goalMatch[2]) : 0;
      const player = goalMatch[5].trim();
      
      // 判断是否进球
      if (line.includes('Assist:') || line.includes('Goal')) {
        events.push({
          minute: minute,
          minute_extra: extra,
          type: 'goal',
          player: player.split('|')[0].trim(),
          description: line.trim()
        });
      }
    }
    
    // 换人格式: "61' | 0:0 | Paulinho | for Matías Vargas"
    const subMatch = line.match(/(\\d+)(?:\\+(\\d+))?['']\\s*\\|\\s*(\\d+):(\\d+)\\s*\\|\\s*([^|]+)\\s*for\\s+([^|]+)/);
    if (subMatch) {
      events.push({
        minute: parseInt(subMatch[1]),
        minute_extra: subMatch[2] ? parseInt(subMatch[2]) : 0,
        type: 'substitution',
        player: subMatch[5].trim(),
        player_out: subMatch[6].trim(),
        description: line.trim()
      });
    }
    
    // 简化格式: "Paulinho · 64'"
    const simpleMatch = line.match(/([A-Z][a-z]+\\s+[A-Z][a-z]+)\\s*·\\s*(\\d+)(?:\\+(\\d+))?['']/);
    if (simpleMatch) {
      const player = simpleMatch[1];
      const minute = parseInt(simpleMatch[2]);
      const extra = simpleMatch[3] ? parseInt(simpleMatch[3]) : 0;
      
      // 检查上下文判断事件类型
      const lineLower = line.toLowerCase();
      let type = 'unknown';
      
      if (lineLower.includes('goal') || lineLower.includes('assist')) {
        type = 'goal';
      } else if (lineLower.includes('yellow')) {
        type = 'yellow_card';
      } else if (lineLower.includes('red')) {
        type = 'red_card';
      } else if (lineLower.includes('substitute') || lineLower.includes('for')) {
        type = 'substitution';
      }
      
      if (type !== 'unknown') {
        events.push({
          minute: minute,
          minute_extra: extra,
          type: type,
          player: player,
          description: line.trim()
        });
      }
    }
  });
  
  // 去重
  const unique = [];
  const seen = new Set();
  events.forEach(e => {
    const key = `${e.minute}-${e.type}-${e.player}`;
    if (!seen.has(key)) {
      seen.add(key);
      unique.push(e);
    }
  });
  
  return JSON.stringify(unique.sort((a,b) => a.minute - b.minute));
})()"""

result = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', js_code],
                       capture_output=True, text=True, timeout=15)

if result.returncode != 0:
    print("❌ 提取失败")
    exit(1)

# 3. 解析结果
output = result.stdout.strip()
if output.startswith('"') and output.endswith('"'):
    output = output[1:-1].replace('\\"', '"')

try:
    events = json.loads(output)
except Exception as e:
    print(f"❌ JSON解析失败: {e}")
    exit(1)

# 4. 显示结果
print(f"\n✓ 找到 {len(events)} 个events\n")

for i, event in enumerate(events, 1):
    extra = f"+{event['minute_extra']}" if event.get('minute_extra', 0) > 0 else ""
    print(f"{i}. {event['minute']}'{extra} - {event['type'].upper()}")
    print(f"   球员: {event['player']}")
    if event.get('player_out'):
        print(f"   换下: {event['player_out']}")
    print(f"   详情: {event['description'][:100]}")
    print()

if len(events) == 0:
    print("⚠️  没有找到events！")

print("="*60)
