#!/usr/bin/env python3
"""
直接从HTML中提取阵容表格
"""

import json
import subprocess
import re

# JavaScript代码：直接获取阵容表格的HTML
js_code = """
(function() {
    // 查找所有包含阵容信息的div
    const lineupDiv = document.querySelector('#lineups');
    if (!lineupDiv) return JSON.stringify({error: 'No lineups found'});

    // 获取所有表格
    const tables = lineupDiv.querySelectorAll('table');

    const data = {
        tables_html: [],
        tables_text: []
    };

    tables.forEach((table, index) => {
        const caption = table.querySelector('caption')?.textContent || 'Table ' + index;
        data.tables_html.push({
            caption: caption,
            html: table.outerHTML
        });
        data.tables_text.push({
            caption: caption,
            text: table.innerText
        });
    });

    return JSON.stringify(data);
})()
"""

print('🔍 抓取阵容表格...')

result = subprocess.run(
    ['openclaw', 'browser', 'evaluate', '--fn', js_code],
    capture_output=True,
    text=True,
    timeout=30
)

lines = result.stdout.strip().split('\n')
json_str = lines[-1] if lines else ''

if json_str and 'tables_html' in json_str:
    data = json.loads(json_str)

    # 保存HTML表格
    with open('data/match1_lineup_tables.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'✅ 找到 {len(data["tables_text"])} 个表格\n')

    # 显示表格内容
    for i, table in enumerate(data['tables_text']):
        print(f'\n📋 表格 {i+1}: {table["caption"]}')
        print('-' * 60)
        lines = table['text'].split('\n')
        # 只显示前20行
        for line in lines[:20]:
            print(line)
        if len(lines) > 20:
            print(f'... (还有 {len(lines) - 20} 行)')

    print('\n✅ 数据已保存到: data/match1_lineup_tables.json')
else:
    print('❌ 未找到阵容表格')
