#!/usr/bin/env python3
"""
测试提取比赛事件数据
"""

import json
import subprocess
import time

url = 'https://fbref.com/en/matches/13f114b6/Wuhan-Three-Towns-Shanghai-Port-April-15-2023-Chinese-Super-League'

print("="*60)
print("测试提取比赛事件数据")
print("="*60)
print()

# 1. 打开页面
print("→ 打开页面...")
subprocess.run(['agent-browser', '--cdp', '9222', 'open', url], 
               capture_output=True, text=True, timeout=30)
time.sleep(10)
print("✓ 页面已加载\n")

# 2. 提取事件数据
print("→ 提取事件数据...")

js_code = """(() => {
  const events = [];
  
  // 方法1: 查找包含时间的div（FBref事件通常有时间标记）
  const allDivs = document.querySelectorAll('div');
  
  allDivs.forEach(div => {
    const text = div.textContent || '';
    
    // 查找时间标记（如 64' 或 90'+2）
    const timeMatch = text.match(/(\\d+)(?:\\+(\\d+))?['']/);
    
    if (timeMatch) {
      const minute = timeMatch[1];
      const extra = timeMatch[2] || '0';
      
      // 判断事件类型
      let type = 'unknown';
      if (text.toLowerCase().includes('goal')) type = 'goal';
      else if (text.toLowerCase().includes('yellow card')) type = 'yellow_card';
      else if (text.toLowerCase().includes('red card')) type = 'red_card';
      else if (text.toLowerCase().includes('substitute')) type = 'substitution';
      
      // 只保存有意义的事件
      if (type !== 'unknown') {
        // 提取球员名字（从链接中）
        const links = div.querySelectorAll('a[href*="/players/"]');
        const players = [];
        links.forEach(link => {
          players.push(link.textContent.trim());
        });
        
        events.push({
          minute: minute,
          minute_extra: extra,
          type: type,
          players: players,
          text: text.substring(0, 300).replace(/\\n/g, ' ').trim()
        });
      }
    }
  });
  
  return JSON.stringify(events);
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
print(f"\n✓ 找到 {len(events)} 个事件\n")

for i, event in enumerate(events[:10], 1):
    print(f"{i}. {event['minute']}' (+{event['minute_extra']}) - {event['type']}")
    print(f"   球员: {', '.join(event['players']) if event['players'] else '未知'}")
    print(f"   详情: {event['text'][:100]}...")
    print()

if len(events) == 0:
    print("⚠️  没有找到事件！尝试其他方法...\n")
    
    # 备用方法：查找特定的事件容器
    js_code2 = """(() => {
      const events = [];
      
      // 方法2: 直接查找页面文本中的事件信息
      const body = document.body.innerText;
      
      // 查找进球信息
      const goalPattern = /(\\d+)(?:\\+(\\d+))?[''][^\\n]*Goal[^\\n]*/gi;
      let match;
      while ((match = goalPattern.exec(body)) !== null) {
        events.push({
          minute: match[1],
          extra: match[2] || '0',
          type: 'goal',
          text: match[0]
        });
      }
      
      // 查找黄牌
      const yellowPattern = /(\\d+)(?:\\+(\\d+))?[''][^\\n]*Yellow[^\\n]*/gi;
      while ((match = yellowPattern.exec(body)) !== null) {
        events.push({
          minute: match[1],
          extra: match[2] || '0',
          type: 'yellow_card',
          text: match[0]
        });
      }
      
      return JSON.stringify(events);
    })()"""
    
    result2 = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', js_code2],
                            capture_output=True, text=True, timeout=15)
    
    output2 = result2.stdout.strip()
    if output2.startswith('"') and output2.endswith('"'):
        output2 = output2[1:-1].replace('\\"', '"')
    
    try:
        events2 = json.loads(output2)
        print(f"✓ 备用方法找到 {len(events2)} 个事件\n")
        for i, event in enumerate(events2[:10], 1):
            print(f"{i}. {event['minute']}' - {event['type']}")
            print(f"   {event['text']}")
            print()
    except:
        print("❌ 备用方法也失败了")

print("="*60)
