#!/usr/bin/env python3
"""
比较两个 Media_Lib 目录的重复文件（>= 500MB）
"""

import os
import sys
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
                    # 如果同名文件已存在，保留较大的那个
                    if filename not in files or size > files[filename][1]:
                        files[filename] = (filepath, size)
            except (OSError, PermissionError) as e:
                # 跳过无法访问的文件
                pass
    
    print(f"  找到 {len(files)} 个文件 >= {format_size(min_size)}")
    return files

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"duplicate_files_{timestamp}.txt"
    
    print("=" * 60)
    print("Media_Lib 目录重复文件比较")
    print("=" * 60)
    print(f"目录1: {DIR1} (glenwrt)")
    print(f"目录2: {DIR2} (glenhouse-pc)")
    print(f"最小文件大小: {format_size(MIN_SIZE)}")
    print()
    
    # 扫描两个目录
    files_dir1 = scan_directory(DIR1, MIN_SIZE)
    files_dir2 = scan_directory(DIR2, MIN_SIZE)
    
    print()
    print("比较重复文件...")
    
    # 找出重复的文件名
    duplicates = set(files_dir1.keys()) & set(files_dir2.keys())
    
    # 分类统计
    exact_duplicates = []
    different_sizes = []
    total_exact_size = 0
    
    for filename in sorted(duplicates):
        path1, size1 = files_dir1[filename]
        path2, size2 = files_dir2[filename]
        
        if size1 == size2:
            exact_duplicates.append((filename, path1, path2, size1))
            total_exact_size += size1
        else:
            different_sizes.append((filename, path1, path2, size1, size2))
    
    # 生成报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"重复文件报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"目录1: {DIR1} (glenwrt)\n")
        f.write(f"目录2: {DIR2} (glenhouse-pc)\n")
        f.write(f"最小文件大小: {format_size(MIN_SIZE)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("摘要统计\n")
        f.write("=" * 80 + "\n")
        f.write(f"目录1 (glenwrt) >= 500MB 文件数: {len(files_dir1)}\n")
        f.write(f"目录2 (glenhouse-pc) >= 500MB 文件数: {len(files_dir2)}\n")
        f.write(f"重复文件总数: {len(duplicates)}\n")
        f.write(f"  - 大小完全相同: {len(exact_duplicates)}\n")
        f.write(f"  - 大小不同: {len(different_sizes)}\n")
        f.write(f"完全重复文件总大小: {format_size(total_exact_size)}\n\n")
        
        # 输出大小相同的重复文件
        if exact_duplicates:
            f.write("=" * 80 + "\n")
            f.write(f"大小完全相同的重复文件 ({len(exact_duplicates)} 个)\n")
            f.write("=" * 80 + "\n\n")
            
            for filename, path1, path2, size in exact_duplicates:
                f.write("-" * 80 + "\n")
                f.write(f"文件名: {filename}\n")
                f.write(f"大小: {format_size(size)}\n")
                f.write(f"glenwrt:      {path1}\n")
                f.write(f"glenhouse-pc: {path2}\n\n")
        
        # 输出大小不同的重复文件
        if different_sizes:
            f.write("=" * 80 + "\n")
            f.write(f"文件名相同但大小不同的文件 ({len(different_sizes)} 个)\n")
            f.write("=" * 80 + "\n\n")
            
            for filename, path1, path2, size1, size2 in different_sizes:
                f.write("-" * 80 + "\n")
                f.write(f"文件名: {filename}\n")
                f.write(f"glenwrt:      {format_size(size1)} - {path1}\n")
                f.write(f"glenhouse-pc: {format_size(size2)} - {path2}\n\n")
    
    # 在终端显示摘要
    print()
    print("=" * 60)
    print("比较完成！")
    print("=" * 60)
    print(f"目录1 (glenwrt) >= 500MB 文件数: {len(files_dir1)}")
    print(f"目录2 (glenhouse-pc) >= 500MB 文件数: {len(files_dir2)}")
    print(f"重复文件总数: {len(duplicates)}")
    print(f"  - 大小完全相同: {len(exact_duplicates)}")
    print(f"  - 大小不同: {len(different_sizes)}")
    print(f"完全重复文件总大小: {format_size(total_exact_size)}")
    print()
    print(f"详细报告已保存到: {output_file}")
    
    # 如果有完全重复的文件，显示前10个
    if exact_duplicates:
        print()
        print("=" * 60)
        print(f"前10个完全重复的文件:")
        print("=" * 60)
        for filename, path1, path2, size in exact_duplicates[:10]:
            print(f"  • {filename} ({format_size(size)})")

if __name__ == "__main__":
    main()
