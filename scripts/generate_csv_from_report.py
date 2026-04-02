#!/usr/bin/env python3
"""
从之前的扫描报告生成CSV文件
"""

import re
import csv
from datetime import datetime
from pathlib import Path

REPORT_FILE = "/Users/glenman/.openclaw/workspace/memory/duplicate_files_20260324_200117.txt"
OUTPUT_DIR = Path("/Users/glenman/.openclaw/workspace/memory")

def format_size(size_bytes):
    """转换字节为人类可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def parse_size(size_str):
    """解析大小字符串为字节数"""
    size_str = size_str.strip()
    
    # 处理 GB, MB, TB 等
    match = re.match(r'([\d.]+)\s*(B|KB|MB|GB|TB)', size_str, re.IGNORECASE)
    if match:
        number = float(match.group(1))
        unit = match.group(2).upper()
        
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4
        }
        
        return int(number * multipliers[unit])
    
    return 0

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = OUTPUT_DIR / f"duplicate_files_comparison_{timestamp}.csv"
    
    print("从扫描报告生成CSV文件...")
    print(f"源文件: {REPORT_FILE}")
    
    # 读取报告文件
    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析重复文件
    csv_data = []
    
    # 匹配文件块
    pattern = r'-{80,}\n文件名: (.+?)\n大小: (.+?)\nglenwrt:\s+(.+?)\nglenhouse-pc: (.+?)\n'
    
    matches = re.findall(pattern, content)
    
    print(f"\n找到 {len(matches)} 个重复文件")
    
    for filename, size_str, glenwrt_path, glenhouse_path in matches:
        size_bytes = parse_size(size_str)
        
        csv_data.append({
            '文件名': filename.strip(),
            '文件大小(字节)': size_bytes,
            '文件大小(可读)': size_str.strip(),
            'glenwrt路径': glenwrt_path.strip(),
            'glenhouse-pc路径': glenhouse_path.strip()
        })
    
    # 写入CSV
    fieldnames = ['文件名', '文件大小(字节)', '文件大小(可读)', 'glenwrt路径', 'glenhouse-pc路径']
    
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    # 统计
    total_size = sum(row['文件大小(字节)'] for row in csv_data)
    
    print()
    print("=" * 60)
    print("导出完成！")
    print("=" * 60)
    print(f"重复文件总数: {len(csv_data)}")
    print(f"总大小: {format_size(total_size)}")
    print()
    print(f"CSV文件已保存到: {csv_file}")
    print()
    print("CSV列说明:")
    print("  1. 文件名 - 文件名称")
    print("  2. 文件大小(字节) - 字节数（用于排序和计算）")
    print("  3. 文件大小(可读) - 人类可读格式（GB/MB等）")
    print("  4. glenwrt路径 - 在glenwrt上的完整路径")
    print("  5. glenhouse-pc路径 - 在glenhouse-pc上的完整路径")
    
    return csv_file

if __name__ == "__main__":
    main()
