#!/usr/bin/env python3
"""快速修复教练和队长信息"""

import json
import glob
import subprocess
import time

def fix_match_data(filepath):
    """修复单场比赛的教练和队长信息"""
    
    # 读取现有数据
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    url = data['metadata']['url']
    
    # 打开页面
    subprocess.run(['agent-browser', '--cdp', '9222', 'open', url],
                  capture_output=True, timeout=30)
    time.sleep(5)
    
    # 提取教练和队长
    extract_js = r"""(() => {
  const bodyText = document.body.innerText;
  const lines = bodyText.split('\n');
  const managers = [];
  const captains = [];
  
  for (let line of lines) {
    const trimmed = line.trim();
    if (trimmed.includes('Manager:')) {
      const match = trimmed.match(/Manager:\s*(.+)/);
      if (match) managers.push(match[1].trim());
    }
    if (trimmed.includes('Captain:')) {
      const match = trimmed.match(/Captain:\s*(.+)/);
      if (match) captains.push(match[1].trim());
    }
  }
  
  return JSON.stringify({
    homeManager: managers[0] || '',
    awayManager: managers[1] || '',
    homeCaptain: captains[0] || '',
    awayCaptain: captains[1] || ''
  });
})()"""
    
    result = subprocess.run(['agent-browser', '--cdp', '9222', 'eval', extract_js],
                          capture_output=True, text=True, timeout=15)
    
    if result.returncode == 0:
        import json
        extracted = json.loads(result.stdout.strip())
        
        # 更新数据
        data['teams']['home']['coach'] = extracted['homeManager']
        data['teams']['home']['captain'] = extracted['homeCaptain']
        data['teams']['away']['coach'] = extracted['awayManager']
        data['teams']['away']['captain'] = extracted['awayCaptain']
        
        # 保存
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    return False

# 处理所有文件
files = sorted(glob.glob('data/match-reports-2025/*.json'))

print("🔧 修复教练和队长信息\n")

fixed_count = 0
for i, filepath in enumerate(files, 1):
    filename = filepath.split('/')[-1]
    print(f"[{i}/30] {filename}", end=' ')
    
    if fix_match_data(filepath):
        print("✅")
        fixed_count += 1
    else:
        print("❌")
    
    time.sleep(2)

print(f"\n✅ 完成: {fixed_count}/30")
