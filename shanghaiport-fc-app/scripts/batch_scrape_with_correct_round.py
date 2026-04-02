#!/usr/bin/env python3
"""
上海海港赛事报告抓取器（正确版本）
使用从FBref页面抓取的实际matchweek值，而不是循环变量
"""

import json
import os
import subprocess
import time
from datetime import datetime
import re

def scrape_match(url: str, match_info: dict) -> dict:
    """抓取单场比赛数据"""
    
    try:
        # 1. 打开页面
        result = subprocess.run(
            ['agent-browser', '--cdp', '9222', 'open', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        time.sleep(10)

        # 2. 提取完整数据（包含正确的matchweek）
        extract_js = r"""(() => {
  const result = {
    scores: [],
    formations: [],
    lineups: {home: [], away: []},
    bench: {home: [], away: []},
    events: [],
    statistics: {},
    venue: {},
    matchweek: ''  // 新增：从页面抓取实际matchweek
  };

  // 提取matchweek - 从页面文本
  const bodyText = document.body.innerText;
  const matchweekMatch = bodyText.match(/Matchweek\s+(\d+)/i);
  if (matchweekMatch) {
    result.matchweek = matchweekMatch[1];
  }

  // 比分
  document.querySelectorAll('.score').forEach(el => {
    const s = parseInt(el.textContent);
    if (!isNaN(s)) result.scores.push(s);
  });

  // ... 其余提取逻辑相同 ...

  return JSON.stringify(result);
})()"""

        # ... 其余代码相同 ...

        # 5. 使用从页面抓取的实际matchweek
        actual_matchweek = extracted.get('matchweek', str(match_info.get('round', 1)))
        
        match_data = {
            "match_info": {
                "match_id": url.split('/')[-2],
                "date": match_info['date'],
                "time": "20:00",
                "competition": {
                    "name": "Chinese Football Association Super League",
                    "season": str(match_info.get('season', 2025)),
                    "round": f"Matchweek {actual_matchweek}"  # 使用实际matchweek
                },
                # ...
            },
            # ...
        }

        return match_data, actual_matchweek  # 返回实际matchweek用于文件名
        
    except Exception as e:
        print(f"      ❌ 错误: {e}")
        return None, None

def main():
    # ... 主函数 ...
    
    for i, match in enumerate(matches, 1):
        date = match['date']
        url = match['url']
        
        print(f"[{i}/30] {date}")
        
        match_data, actual_round = scrape_match(url, {
            'date': date,
            'season': season
        })
        
        if match_data:
            # 使用实际的matchweek值作为文件名
            filename = f"{date}-中超-第{actual_round}轮.json"
            filepath = os.path.join(output_dir, filename)
            
            # ... 保存文件 ...
    
    # ... 总结 ...

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
