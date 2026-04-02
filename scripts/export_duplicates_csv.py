#!/usr/bin/env python3
"""
导出 Media_Lib 重复文件比较为 CSV 格式
"""

import os
import csv
from datetime import datetime
from pathlib import Path

DIR1 = "/Volumes/Media_Lib"
DIR2 = "/Volumes/Media_Lib-1"
MIN_SIZE = 500 * 1024 * 1024  # 500MB
OUTPUT_DIR = Path("/Users/glenman/.openclaw/workspace/memory")

def format_size(size_bytes):
    """转换字节为人类可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def scan_directory(directory, min_size):
    """扫描目录，返回文件名 -> (路径, 大小) 的字典"""
    files = {}
    print(f"扫描 {directory} ...")
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            try:
                filepath = os.path.join(root, filename)
                size = os.path.getsize(filepath)
                
                if size >= min_size:
                    if filename not in files or size > files[filename][1]:
                        files[filename] = (filepath, size)
            except (OSError, PermissionError):
                pass
    
    print(f"  找到 {len(files)} 个文件 >= {format_size(min_size)}")
    return files

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = OUTPUT_DIR / f"duplicate_files_{timestamp}.csv"
    
    print("=" * 60)
    print("Media_Lib 目录重复文件比较 - CSV导出")
    print("=" * 60)
    print()
    
    # 扫描两个目录
    files_dir1 = scan_directory(DIR1, MIN_SIZE)
    files_dir2 = scan_directory(DIR2, MIN_SIZE)
    
    print()
    print("生成CSV文件...")
    
    # 找出重复的文件名
    duplicates = set(files_dir1.keys()) & set(files_dir2.keys())
    
    # 准备CSV数据
    csv_data = []
    
    for filename in sorted(duplicates):
        path1, size1 = files_dir1[filename]
        path2, size2 = files_dir2[filename]
        
        size_diff = abs(size1 - size2)
        is_identical = (size1 == size2)
        
        csv_data.append({
            '文件名': filename,
            'glenwrt大小(字节)': size1,
            'glenwrt大小(可读)': format_size(size1),
            'glenhouse-pc大小(字节)': size2,
            'glenhouse-pc大小(可读)': format_size(size2),
            '是否完全相同': '是' if is_identical else '否',
            '大小差异(字节)': size_diff if not is_identical else 0,
            '大小差异(可读)': format_size(size_diff) if not is_identical else '0 B',
            'glenwrt路径': path1,
            'glenhouse-pc路径': path2
        })
    
    # 写入CSV文件
    fieldnames = [
        '文件名',
        'glenwrt大小(字节)', 'glenwrt大小(可读)',
        'glenhouse-pc大小(字节)', 'glenhouse-pc大小(可读)',
        '是否完全相同',
        '大小差异(字节)', '大小差异(可读)',
        'glenwrt路径', 'glenhouse-pc路径'
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    # 统计信息
    identical_count = sum(1 for row in csv_data if row['是否完全相同'] == '是')
    different_count = len(csv_data) - identical_count
    total_size = sum(row['glenwrt大小(字节)'] for row in csv_data if row['是否完全相同'] == '是')
    
    print()
    print("=" * 60)
    print("导出完成！")
    print("=" * 60)
    print(f"重复文件总数: {len(csv_data)}")
    print(f"  - 大小完全相同: {identical_count}")
    print(f"  - 大小不同: {different_count}")
    print(f"完全重复文件总大小: {format_size(total_size)}")
    print()
    print(f"CSV文件已保存到: {csv_file}")
    print()
    print("CSV列说明:")
    print("  - 文件名: 文件名称")
    print("  - glenwrt大小(字节/可读): 在glenwrt上的文件大小")
    print("  - glenhouse-pc大小(字节/可读): 在glenhouse-pc上的文件大小")
    print("  - 是否完全相同: 两个文件大小是否一致")
    print("  - 大小差异: 如果大小不同，显示差异")
    print("  - 路径: 两个文件的具体路径")

if __name__ == "__main__":
    main()
