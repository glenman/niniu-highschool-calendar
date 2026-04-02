#!/usr/bin/env python3
"""
从FBref页面抓取首发阵容和详细统计
"""

import json
import subprocess
import time

# JavaScript代码：提取阵容和详细统计
js_code = """
(function() {
    const data = {
        // 首发阵容
        home_lineup: [],
        away_lineup: [],
        home_subs: [],
        away_subs: [],

        // 详细统计
        detailed_stats: {},

        // 换人信息
        substitutions: [],

        // 黄牌和红牌
        cards: []
    };

    // 1. 提取阵容信息
    // 查找包含 "Starting" 和 "Substitutes" 的表格
    const lineupTables = document.querySelectorAll('table');
    let currentTeam = null;
    let currentSection = null;

    lineupTables.forEach(table => {
        const caption = table.querySelector('caption');
        if (caption) {
            const captionText = caption.textContent;

            // 检测球队
            if (captionText.includes('Shanghai Port') || captionText.includes('上海海港')) {
                currentTeam = 'home';
            } else if (captionText.includes('Wuhan Three Towns') || captionText.includes('武汉三镇')) {
                currentTeam = 'away';
            }

            // 检测首发或替补
            if (captionText.includes('Starting')) {
                currentSection = 'lineup';
            } else if (captionText.includes('Substitutes')) {
                currentSection = 'subs';
            }
        }

        // 提取球员
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length > 0) {
                const player = {
                    number: cells[0]?.textContent?.trim() || '',
                    position: cells[1]?.textContent?.trim() || '',
                    name: cells[2]?.textContent?.trim() || '',
                    minutes: cells[3]?.textContent?.trim() || '90'
                };

                if (currentTeam && currentSection) {
                    const key = `${currentTeam}_${currentSection}`;
                    if (data[key]) {
                        data[key].push(player);
                    }
                }
            }
        });
    });

    // 2. 提取详细统计
    const statsDiv = document.querySelector('#team_stats');
    if (statsDiv) {
        const statRows = statsDiv.querySelectorAll('tr');
        statRows.forEach(row => {
            const label = row.querySelector('th')?.textContent?.trim();
            const cells = row.querySelectorAll('td');
            if (label && cells.length >= 2) {
                data.detailed_stats[label] = {
                    home: cells[0]?.textContent?.trim(),
                    away: cells[1]?.textContent?.trim()
                };
            }
        });
    }

    // 3. 提取换人信息
    const eventsDiv = document.querySelector('#events_wrap');
    if (eventsDiv) {
        const eventRows = eventsDiv.querySelectorAll('div.event');
        eventRows.forEach(event => {
            const text = event.textContent;
            if (text.includes('for')) {
                const parts = text.split('for');
                if (parts.length === 2) {
                    data.substitutions.push({
                        player_in: parts[0].split(/\s+/).pop()?.trim(),
                        player_out: parts[1].trim(),
                        minute: event.querySelector('.minute')?.textContent?.trim()
                    });
                }
            }
        });
    }

    // 4. 提取黄牌和红牌
    const allEvents = document.querySelectorAll('.event');
    allEvents.forEach(event => {
        const text = event.textContent;
        if (text.includes('Yellow Card') || text.includes('Red Card')) {
            data.cards.push({
                type: text.includes('Yellow') ? 'yellow' : 'red',
                player: event.querySelector('.player')?.textContent?.trim(),
                minute: event.querySelector('.minute')?.textContent?.trim(),
                team: text.includes('Shanghai') ? 'home' : 'away'
            });
        }
    });

    return JSON.stringify(data);
})()
"""

print('🔍 开始抓取详细数据...')

# 执行JavaScript
result = subprocess.run(
    ['openclaw', 'browser', 'evaluate', '--fn', js_code],
    capture_output=True,
    text=True,
    timeout=30
)

# 提取JSON
lines = result.stdout.strip().split('\n')
json_str = lines[-1] if lines else ''

if json_str and json_str != '{}':
    # 解析数据
    detailed_data = json.loads(json_str)

    # 保存数据
    with open('data/match1_lineup_stats.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_data, f, ensure_ascii=False, indent=2)

    print('✅ 详细数据已保存到: data/match1_lineup_stats.json\n')

    # 显示数据摘要
    print('📊 数据摘要:')
    print(f'  主队首发: {len(detailed_data.get("home_lineup", []))} 人')
    print(f'  客队首发: {len(detailed_data.get("away_lineup", []))} 人')
    print(f'  主队替补: {len(detailed_data.get("home_subs", []))} 人')
    print(f'  客队替补: {len(detailed_data.get("away_subs", []))} 人')
    print(f'  统计项: {len(detailed_data.get("detailed_stats", {}))} 项')
    print(f'  换人: {len(detailed_data.get("substitutions", []))} 次')
    print(f'  红黄牌: {len(detailed_data.get("cards", []))} 张')

    # 显示部分数据
    if detailed_data.get('home_lineup'):
        print('\n👥 主队首发阵容:')
        for player in detailed_data['home_lineup'][:3]:
            print(f'    {player["number"]}. {player["name"]} ({player["position"]})')

    if detailed_data.get('detailed_stats'):
        print('\n📊 统计数据:')
        for stat, values in list(detailed_data['detailed_stats'].items())[:5]:
            print(f'    {stat}: {values["home"]} vs {values["away"]}')

else:
    print('❌ 数据抓取失败')
