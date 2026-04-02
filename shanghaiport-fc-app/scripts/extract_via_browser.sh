#!/bin/bash

# 使用agent-browser提取Match Report链接
# 使用方法: ./scripts/extract_via_browser.sh 2026

SEASON=${1:-2026}

echo "正在提取上海海港 ${SEASON} 赛季的Match Report链接..."

# JavaScript代码：提取所有Match Report链接
JS_CODE='
const links = [];
const rows = document.querySelectorAll("table.stats_table tbody tr");

rows.forEach(row => {
    const dateCell = row.querySelector("th[data-stat=\"date\"] a") || 
                    row.querySelector("td[data-stat=\"date\"] a");
    const matchReportLink = Array.from(row.querySelectorAll("a")).find(
        link => link.textContent.trim() === "Match Report" &&
               link.href.includes("/matches/")
    );
    
    if (dateCell && matchReportLink) {
        links.push({
            date: dateCell.textContent.trim(),
            url: matchReportLink.href
        });
    }
});

console.log(JSON.stringify(links, null, 2));
'

# 使用agent-browser执行JavaScript
agent-browser --cdp 9222 exec "$JS_CODE"
