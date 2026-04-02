#!/usr/bin/env python3
"""
综合提取第一场比赛的所有详细数据
"""

import json
import subprocess
import time
import re

def scrape_complete_data():
    """一次性抓取所有详细数据"""

    # 1. 打开页面
    print('🌐 打开页面...')
    result = subprocess.run(
        ['openclaw', 'browser', 'open', 'https://fbref.com/en/matches/08602b83/Shanghai-Port-Wuhan-Three-Towns-March-1-2024-Chinese-Super-League'],
        capture_output=True,
        text=True,
        timeout=30
    )

    if 'opened:' not in result.stdout:
        print('❌ 页面打开失败')
        return None

    print('✅ 页面已打开')
    time.sleep(5)

    # 2. 综合JavaScript提取所有数据
    js_code = """
    (function() {
        const data = {
            // 基本信息
            match_info: {},
            teams: {
                home: { lineup: [], substitutes: [], substitutions: [] },
                away: { lineup: [], substitutes: [], substitutions: [] }
            },
            events: [],
            statistics: {},
            player_stats: { home: [], away: [] }
        };

        // 提取比赛信息
        const scorebox = document.querySelector('.scorebox');
        if (scorebox) {
            const text = scorebox.textContent;
            data.match_info = {
                home_team: text.match(/Shanghai Port/)?.[0] || '',
                away_team: text.match(/Wuhan Three Towns/)?.[0] || '',
                home_score: (text.match(/Shanghai Port[\\s\\S]*?\\n(\\d+)/) || [])[1] || '0',
                away_score: (text.match(/Wuhan Three Towns[\\s\\S]*?\\n(\\d+)/) || [])[1] || '0',
                home_manager: (text.match(/Manager:\\s*([^\\n]+)/) || [])[1]?.split('\\n')[0] || '',
                away_manager: (text.match(/Manager:\\s*([^\\n]+)/g) || [])[1]?.replace('Manager:', '').trim() || '',
                home_captain: (text.match(/Captain:\\s*([^\\n]+)/) || [])[1]?.split('\\n')[0] || '',
                away_captain: (text.match(/Captain:\\s*([^\\n]+)/g) || [])[1]?.replace('Captain:', '').trim() || '',
                date: '2024-03-01',
                venue: (text.match(/Venue:\\s*([^\\n]+)/) || [])[1] || '',
                attendance: (text.match(/Attendance:\\s*([\\d,]+)/) || [])[1]?.replace(',', '') || '0'
            };
        }

        // 提取统计
        const statsTable = document.querySelector('#team_stats table, #stats table');
        if (statsTable) {
            const rows = statsTable.querySelectorAll('tr');
            rows.forEach(row => {
                const cells = row.querySelectorAll('td, th');
                if (cells.length >= 3) {
                    const statName = cells[1]?.textContent?.trim();
                    if (statName && !statName.includes('Team')) {
                        data.statistics[statName] = {
                            home: cells[0]?.textContent?.trim() || '0',
                            away: cells[2]?.textContent?.trim() || '0'
                        };
                    }
                }
            });
        }

        // 提取阵容（从lineups区域）
        const lineupsDiv = document.querySelector('#lineups');
        if (lineupsDiv) {
            const tables = lineupsDiv.querySelectorAll('table');
            tables.forEach(table => {
                const caption = table.querySelector('caption')?.textContent || '';
                const isHome = caption.includes('Shanghai Port');
                const isStarting = caption.includes('Starting');
                const team = isHome ? 'home' : 'away';
                const list = isStarting ? 'lineup' : 'substitutes';

                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 3) {
                        const player = {
                            number: cells[0]?.textContent?.trim(),
                            position: cells[1]?.textContent?.trim(),
                            name: cells[2]?.textContent?.trim()
                        };
                        data.teams[team][list].push(player);
                    }
                });
            });
        }

        // 提取事件（进球、黄牌、换人等）
        const eventsDiv = document.querySelector('#events_wrap, #events');
        if (eventsDiv) {
            const eventDivs = eventsDiv.querySelectorAll('.event, div[data-minute]');
            eventDivs.forEach(div => {
                const text = div.textContent;
                const minuteMatch = text.match(/(\\d+)(\\+(\\d+))?'/);
                if (minuteMatch) {
                    const event = {
                        minute: parseInt(minuteMatch[1]),
                        minute_extra: minuteMatch[3] ? parseInt(minuteMatch[3]) : 0,
                        type: text.includes('Goal') || text.includes('·') ? 'goal' :
                              text.includes('Yellow') ? 'yellow_card' :
                              text.includes('Red') ? 'red_card' :
                              text.includes('for') ? 'substitution' : 'other',
                        player: '',
                        team: text.includes('Shanghai') || text.includes('Wu Lei') ? 'home' : 'away'
                    };

                    // 提取球员名
                    const playerMatch = text.match(/([A-Za-z\\s']+)(?:\\s+·|\\s+for)/);
                    if (playerMatch) {
                        event.player = playerMatch[1].trim();
                    }

                    if (event.type !== 'other') {
                        data.events.push(event);
                    }
                }
            });
        }

        return JSON.stringify(data);
    })()
    """

    print('📊 抓取详细数据...')
    result = subprocess.run(
        ['openclaw', 'browser', 'evaluate', '--fn', js_code],
        capture_output=True,
        text=True,
        timeout=30
    )

    lines = result.stdout.strip().split('\n')
    json_str = lines[-1] if lines else ''

    if json_str and json_str != '{}':
        data = json.loads(json_str)

        # 保存数据
        with open('data/match1_complete_scrape.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print('✅ 完整数据已保存\n')

        # 显示数据摘要
        print('=' * 60)
        print('📊 数据提取摘要')
        print('=' * 60)
        print(f'\n📋 比赛信息:')
        print(f'  {data["match_info"]["home_team"]} {data["match_info"]["home_score"]}-{data["match_info"]["away_score"]} {data["match_info"]["away_team"]}')
        print(f'  主队教练: {data["match_info"]["home_manager"]}')
        print(f'  主队队长: {data["match_info"]["home_captain"]}')
        print(f'  客队教练: {data["match_info"]["away_manager"]}')
        print(f'  客队队长: {data["match_info"]["away_captain"]}')

        print(f'\n👥 阵容:')
        print(f'  主队首发: {len(data["teams"]["home"]["lineup"])} 人')
        print(f'  客队首发: {len(data["teams"]["away"]["lineup"])} 人')
        print(f'  主队替补: {len(data["teams"]["home"]["substitutes"])} 人')
        print(f'  客队替补: {len(data["teams"]["away"]["substitutes"])} 人')

        print(f'\n⚽ 比赛事件: {len(data["events"])} 个')

        print(f'\n📊 统计数据: {len(data["statistics"])} 项')
        if data["statistics"]:
            print('  主要统计:')
            for stat, values in list(data["statistics"].items())[:5]:
                print(f'    {stat}: {values["home"]} vs {values["away"]}')

        return data
    else:
        print('❌ 数据抓取失败')
        return None

if __name__ == '__main__':
    try:
        scrape_complete_data()
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
