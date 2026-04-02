#!/usr/bin/env python3
"""
简化版测试 - 使用CDP提取FBref比赛数据
"""

import json
import subprocess
import time

url = 'https://fbref.com/en/matches/13f114b6/Wuhan-Three-Towns-Shanghai-Port-April-15-2023-Chinese-Super-League'

print("="*60)
print("测试CDP抓取FBref比赛数据")
print("="*60)
print()

# 1. 打开页面
print("→ 打开页面...")
result = subprocess.run(['agent-browser', '--cdp', '9222', 'open', url], 
                       capture_output=True, text=True, timeout=30)
if result.returncode != 0:
    print("❌ 打开失败")
    exit(1)
print("✓ 页面已加载")
time.sleep(10)

# 2. 提取数据
print("\n→ 提取数据...")

js_code = """(() => {
  const data = {
    scores: [],
    formations: [],
    players: {home: {starters: [], subs: []}, away: {starters: [], subs: []}},
    events: [],
    stats: {}
  };
  
  // 1. 比分
  const scoreEls = document.querySelectorAll('.score');
  scoreEls.forEach(el => {
    const s = parseInt(el.textContent);
    if (!isNaN(s)) data.scores.push(s);
  });
  
  // 2. 查找阵容表格 - 通过特定结构
  // FBref通常有两个阵容表
  const tables = document.querySelectorAll('table');
  let tableCount = 0;
  
  tables.forEach(table => {
    const text = table.textContent;
    // 检查是否是阵容表（包含"Bench"关键字）
    if (text.includes('Bench') && text.includes('(') && text.includes(')')) {
      const header = table.querySelector('th');
      if (header) {
        data.formations.push(header.textContent.trim());
      }
      
      let isBench = false;
      const starters = [];
      const subs = [];
      
      table.querySelectorAll('tr').forEach(row => {
        if (row.textContent.includes('Bench')) {
          isBench = true;
          return;
        }
        
        const link = row.querySelector('a[href*="/players/"]');
        if (link) {
          const tds = row.querySelectorAll('td');
          const player = {
            number: tds[0]?.textContent?.trim() || '',
            name: link.textContent?.trim() || '',
            country: 'Unknown'
          };
          
          if (isBench) subs.push(player);
          else starters.push(player);
        }
      });
      
      if (tableCount === 0) {
        data.players.home.starters = starters;
        data.players.home.subs = subs;
      } else {
        data.players.away.starters = starters;
        data.players.away.subs = subs;
      }
      tableCount++;
    }
  });
  
  // 3. 统计数据
  const bodyText = document.body.innerText;
  
  const possMatch = bodyText.match(/Possession[\\s\\S]*?(\\d+)%[\\s]*(\\d+)%/);
  if (possMatch) data.stats.possession = {home: possMatch[1], away: possMatch[2]};
  
  const shotsMatch = bodyText.match(/Shots.*?(\\d+).*?(\\d+)/);
  if (shotsMatch) data.stats.shots = {home: shotsMatch[1], away: shotsMatch[2]};
  
  const foulsMatch = bodyText.match(/(\\d+)\\s+Fouls\\s+(\\d+)/);
  if (foulsMatch) data.stats.fouls = {home: foulsMatch[1], away: foulsMatch[2]};
  
  const cornersMatch = bodyText.match(/(\\d+)\\s+Corners\\s+(\\d+)/);
  if (cornersMatch) data.stats.corners = {home: cornersMatch[1], away: cornersMatch[2]};
  
  return JSON.stringify(data);
})()"""

result = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', js_code],
                       capture_output=True, text=True, timeout=15)

if result.returncode != 0:
    print("❌ 提取失败")
    exit(1)

# 3. 解析数据
output = result.stdout.strip()
if output.startswith('"') and output.endswith('"'):
    output = output[1:-1].replace('\\"', '"')

try:
    data = json.loads(output)
except Exception as e:
    print(f"❌ JSON解析失败: {e}")
    print(f"Output preview: {output[:200]}")
    exit(1)

# 4. 显示结果
print("\n✓ 数据提取成功！\n")

print("【比分】")
print(f"  {data['scores']}")

print("\n【阵型】")
print(f"  {data['formations']}")

print("\n【主队阵容】")
print(f"  首发: {len(data['players']['home']['starters'])} 人")
print(f"  替补: {len(data['players']['home']['subs'])} 人")
if data['players']['home']['starters']:
    print(f"  示例: {data['players']['home']['starters'][0]}")

print("\n【客队阵容】")
print(f"  首发: {len(data['players']['away']['starters'])} 人")
print(f"  替补: {len(data['players']['away']['subs'])} 人")
if data['players']['away']['starters']:
    print(f"  示例: {data['players']['away']['starters'][0]}")

print("\n【统计数据】")
for key, value in data['stats'].items():
    print(f"  {key}: {value}")

print(f"\n{'='*60}")
print("✅ 测试完成")
print(f"{'='*60}")
