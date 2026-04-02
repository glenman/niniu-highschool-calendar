#!/bin/bash

# 比较两个 Media_Lib 目录的重复文件
# 只比较 >= 500MB 的文件

DIR1="/Volumes/Media_Lib"
DIR2="/Volumes/Media_Lib-1"
MIN_SIZE=$((500 * 1024 * 1024))  # 500MB in bytes
OUTPUT_DIR="/Users/glenman/.openclaw/workspace/memory"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "开始扫描两个目录..."
echo "目录1: $DIR1 (glenwrt)"
echo "目录2: $DIR2 (glenhouse-pc)"
echo "最小文件大小: 500MB"
echo ""

# 创建临时文件存储文件列表
TMP1=$(mktemp)
TMP2=$(mktemp)
DUPES_FILE="$OUTPUT_DIR/duplicate_files_${TIMESTAMP}.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 扫描 $DIR1 ..."
find "$DIR1" -type f -size +500M -exec stat -f "%N|%z" {} \; 2>/dev/null | sort > "$TMP1"
COUNT1=$(wc -l < "$TMP1")
echo "找到 $COUNT1 个文件 >= 500MB"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 扫描 $DIR2 ..."
find "$DIR2" -type f -size +500M -exec stat -f "%N|%z" {} \; 2>/dev/null | sort > "$TMP2"
COUNT2=$(wc -l < "$TMP2")
echo "找到 $COUNT2 个文件 >= 500MB"

echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始比较重复文件..."

# 创建关联数组来存储文件信息
declare -A files_dir1
declare -A files_dir2

# 读取目录1的文件（格式：路径|大小）
while IFS='|' read -r filepath size; do
    filename=$(basename "$filepath")
    files_dir1["$filename"]="$filepath|$size"
done < "$TMP1"

# 读取目录2的文件并查找重复
while IFS='|' read -r filepath size; do
    filename=$(basename "$filepath")
    files_dir2["$filename"]="$filepath|$size"
done < "$TMP2"

# 找出重复的文件
echo "==================================================" > "$DUPES_FILE"
echo "重复文件报告 - $(date '+%Y-%m-%d %H:%M:%S')" >> "$DUPES_FILE"
echo "==================================================" >> "$DUPES_FILE"
echo "" >> "$DUPES_FILE"
echo "目录1: $DIR1 (glenwrt)" >> "$DUPES_FILE"
echo "目录2: $DIR2 (glenhouse-pc)" >> "$DUPES_FILE"
echo "" >> "$DUPES_FILE"

dupe_count=0
total_dupe_size=0

for filename in "${!files_dir1[@]}"; do
    if [[ -v files_dir2["$filename"] ]]; then
        IFS='|' read -r path1 size1 <<< "${files_dir1[$filename]}"
        IFS='|' read -r path2 size2 <<< "${files_dir2[$filename]}"
        
        # 转换为人类可读格式
        size1_hr=$(numfmt --to=iec-i --suffix=B "$size1" 2>/dev/null || echo "${size1}B")
        size2_hr=$(numfmt --to=iec-i --suffix=B "$size2" 2>/dev/null || echo "${size2}B")
        
        # 如果大小相同，标记为完全重复
        if [ "$size1" -eq "$size2" ]; then
            status="✓ 完全相同"
            total_dupe_size=$((total_dupe_size + size1))
        else
            status="⚠ 大小不同"
        fi
        
        echo "----------------------------------------" >> "$DUPES_FILE"
        echo "文件名: $filename" >> "$DUPES_FILE"
        echo "状态: $status" >> "$DUPES_FILE"
        echo "glenwrt:     $size1_hr - $path1" >> "$DUPES_FILE"
        echo "glenhouse-pc: $size2_hr - $path2" >> "$DUPES_FILE"
        
        dupe_count=$((dupe_count + 1))
    fi
done

# 输出摘要
echo "" >> "$DUPES_FILE"
echo "==================================================" >> "$DUPES_FILE"
echo "摘要统计" >> "$DUPES_FILE"
echo "==================================================" >> "$DUPES_FILE"
echo "目录1 (glenwrt) >= 500MB 文件数: $COUNT1" >> "$DUPES_FILE"
echo "目录2 (glenhouse-pc) >= 500MB 文件数: $COUNT2" >> "$DUPES_FILE"
echo "重复文件数: $dupe_count" >> "$DUPES_FILE"

total_dupe_size_hr=$(numfmt --to=iec-i --suffix=B "$total_dupe_size" 2>/dev/null || echo "${total_dupe_size}B")
echo "重复文件总大小: $total_dupe_size_hr" >> "$DUPES_FILE"

# 显示结果
cat "$DUPES_FILE"

# 清理临时文件
rm -f "$TMP1" "$TMP2"

echo ""
echo "报告已保存到: $DUPES_FILE"
