#!/usr/bin/env python3
"""
分析FBref页面的HTML结构，找出events_wrap的位置和内容
"""

import subprocess
import json
import time

# JavaScript代码：提取页面上所有可能包含事件信息的区域
ANALYZE_JS = r"""(() => {
  const result = {
    // 1. 当前的.event选择器
    current_events: [],
    // 2. 查找events_wrap区域
    events_wrap: null,
    // 3. 查找Match Summary区域
    match_summary: null,
    // 4. 查找所有包含"Goal"文本的div
    goal_divs: []
  };
  
  // 1. 当前的event选择器
  document.querySelectorAll('.event').forEach(div => {
    result.current_events.push({
      className: div.className,
      text: div.textContent.substring(0, 100)
    });
  });
  
  // 2. 查找events_wrap
  const eventsWrapDiv = document.querySelector('#events_wrap') || 
                        document.querySelector('.events_wrap') ||
                        document.querySelector('[id*="events"]');
  if (eventsWrapDiv) {
    result.events_wrap = {
      id: eventsWrapDiv.id,
      className: eventsWrapDiv.className,
      html: eventsWrapDiv.innerHTML.substring(0, 500)
    };
  }
  
  // 3. 查找Match Summary
  const summaryDiv = document.querySelector('#summary') ||
                     document.querySelector('.summary') ||
                     document.querySelector('[id*="summary"]');
  if (summaryDiv) {
    result.match_summary = {
      id: summaryDiv.id,
      className: summaryDiv.className,
      text: summaryDiv.textContent.substring(0, 500)
    };
  }
  
  // 4. 查找所有包含"Goal"的div
  document.querySelectorAll('div').forEach(div => {
    const text = div.textContent;
    if (text.includes('Goal') && text.includes("'") && text.length < 200) {
      result.goal_divs.push({
        className: div.className,
        id: div.id,
        text: text.trim()
      });
    }
  });
  
  return JSON.stringify(result);
})()"""

def analyze_page(url):
    """分析单个页面"""
    print(f"🔍 分析页面: {url}\n")
    
    # 打开页面
    subprocess.run(['agent-browser', '--cdp', '9222', 'open', url],
                  capture_output=True, text=True, timeout=30)
    time.sleep(10)
    
    # 执行分析
    result = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', ANALYZE_JS],
                          capture_output=True, text=True, timeout=15)
    
    if result.returncode != 0:
        print(f"❌ 执行失败: {result.stderr}")
        return None
    
    output = result.stdout.strip()
    if output.startswith('"') and output.endswith('"'):
        output = output[1:-1].replace('\\"', '"')
    
    data = json.loads(output)
    
    print("=" * 70)
    print("1. 当前的.event选择器找到的事件")
    print("=" * 70)
    print(f"找到 {len(data['current_events'])} 个事件")
    for i, event in enumerate(data['current_events'][:3], 1):
        print(f"{i}. {event['className']}")
        print(f"   {event['text'][:80]}...\n")
    
    print("=" * 70)
    print("2. events_wrap区域")
    print("=" * 70)
    if data['events_wrap']:
        print(f"✅ 找到: id={data['events_wrap']['id']}, class={data['events_wrap']['className']}")
        print(f"HTML预览:\n{data['events_wrap']['html'][:300]}...")
    else:
        print("❌ 未找到events_wrap")
    
    print("\n" + "=" * 70)
    print("3. Match Summary区域")
    print("=" * 70)
    if data['match_summary']:
        print(f"✅ 找到: id={data['match_summary']['id']}, class={data['match_summary']['className']}")
        print(f"文本预览:\n{data['match_summary']['text'][:300]}...")
    else:
        print("❌ 未找到Match Summary")
    
    print("\n" + "=" * 70)
    print("4. 包含'Goal'的div（前10个）")
    print("=" * 70)
    print(f"找到 {len(data['goal_divs'])} 个")
    for i, div in enumerate(data['goal_divs'][:10], 1):
        print(f"{i}. class='{div['className']}' id='{div['id']}'")
        print(f"   {div['text'][:100]}\n")
    
    return data

if __name__ == "__main__":
    # 分析2025赛季第一场比赛（已知有penalty_goal）
    url = "https://fbref.com/en/matches/a67ccb3a/Shanghai-Port-Shenzhen-Peng-City-February-23-2025-Chinese-Super-League"
    
    analyze_page(url)
