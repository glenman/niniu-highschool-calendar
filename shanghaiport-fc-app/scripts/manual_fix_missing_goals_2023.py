#!/usr/bin/env python3
"""
手动修复2023赛季缺失的进球
从FBref页面提取缺失的进球信息
"""

import json
import subprocess
import time
import glob
import re

def get_missing_goals_from_page(url):
    """从FBref页面提取缺失的进球信息"""
    try:
        # 打开页面
        subprocess.run(['agent-browser', '--cdp', '9222', 'open', url],
                      capture_output=True, timeout=30)
        time.sleep(5)
        
        # 提取进球信息
        extract_js = r"""(() => {
          const bodyText = document.body.innerText;
          const lines = bodyText.split('\n');
          
          const goals = [];
          
          lines.forEach(line => {
            const trimmed = line.trim();
            // 查找格式如 "Player Name · XX'" 的行
            if (/[·•]\s*\d+['\u2019]/.test(trimmed) && trimmed.length < 100) {
              // 提取球员名和时间
              const match = trimmed.match(/(.+?)\s*[·•]\s*(\d+)['\u2019]/);
              if (match) {
                goals.push({
                  player: match[1].trim(),
                  minute: parseInt(match[2])
                });
              }
            }
          });
          
          return JSON.stringify(goals);
        })()"""
        
        result = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', extract_js],
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output.startswith('"') and output.endswith('"'):
                output = output[1:-1].replace('\\"', '"')
            return json.loads(output)
        
    except Exception as e:
        print(f"  ❌ 提取失败: {e}")
        return []
    
    return []

def main():
    # 需要修复的比赛列表（根据之前的检查）
    matches_to_fix = [
        {
            'file': '2023-06-03-中超-第11轮.json',
            'date': '2023-06-03',
            'missing': 1
        },
        {
            'file': '2023-07-16-中超-第17轮.json',
            'date': '2023-07-16',
            'missing': 1
        },
        {
            'file': '2023-07-29-中超-第19轮.json',
            'date': '2023-07-29',
            'missing': 1
        },
        {
            'file': '2023-08-12-中超-第22轮.json',
            'date': '2023-08-12',
            'missing': 1
        },
        {
            'file': '2023-09-23-中超-第26轮.json',
            'date': '2023-09-23',
            'missing': 1
        },
        {
            'file': '2023-10-20-中超-第28轮.json',
            'date': '2023-10-20',
            'missing': 1
        },
        {
            'file': '2023-11-04-中超-第30轮.json',
            'date': '2023-11-04',
            'missing': 2
        }
    ]
    
    print("🔧 开始手动修复缺失的进球\n")
    print("=" * 70)
    
    fixed_count = 0
    
    for match in matches_to_fix:
        filepath = f"data/match-reports-2023/{match['file']}"
        
        print(f"\n处理: {match['file']}")
        print(f"  缺失: {match['missing']}个进球")
        
        try:
            # 读取现有数据
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            url = data['metadata']['url']
            
            # 获取页面上的进球信息
            page_goals = get_missing_goals_from_page(url)
            
            if page_goals:
                print(f"  页面上找到: {len(page_goals)}个进球")
                
                # 获取已记录的进球
                existing_goals = [e for e in data['events'] if e['type'] == 'goal']
                existing_minutes = [g['minute'] for g in existing_goals]
                
                # 找出缺失的进球
                missing_goals = [g for g in page_goals if g['minute'] not in existing_minutes]
                
                print(f"  缺失的进球:")
                for g in missing_goals:
                    print(f"    {g['minute']}' - {g['player']}")
                
                # 添加缺失的进球到events
                for g in missing_goals:
                    # 判断主客队（这里需要更精确的判断逻辑）
                    # 简化：根据球员名判断（上海海港的球员）
                    shanghai_players = [
                        'Oscar', 'Paulinho', 'Gustavo', 'Wu Lei', 'Li Shenglong',
                        'Lu Wenjun', 'Wang Shenchao', 'Zhang Linpeng', 'Yan Junling',
                        'Matías Vargas', 'Markus Pink', 'Xu Xin', 'Tyias Browning'
                    ]
                    
                    is_home = any(p in g['player'] for p in shanghai_players)
                    
                    new_goal = {
                        "minute": g['minute'],
                        "minute_extra": 0,
                        "type": "goal",
                        "team": "home" if is_home else "away",
                        "player": g['player'],
                        "player2": "",
                        "goal_type": "goal",
                        "player_out": "",
                        "description": "GOAL"
                    }
                    
                    data['events'].append(new_goal)
                
                # 重新排序events
                data['events'].sort(key=lambda x: (x['minute'], x.get('minute_extra', 0)))
                
                # 保存
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"  ✅ 已添加 {len(missing_goals)}个进球")
                fixed_count += 1
                
            else:
                print(f"  ⚠️  无法从页面提取进球信息")
        
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        time.sleep(2)
    
    print(f"\n{'=' * 70}")
    print(f"✅ 修复完成: {fixed_count}/{len(matches_to_fix)}场比赛")
    print("=" * 70)

if __name__ == '__main__':
    main()
