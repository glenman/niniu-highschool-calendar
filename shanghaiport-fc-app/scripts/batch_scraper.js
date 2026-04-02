#!/usr/bin/env node

/**
 * 上海海港2024赛季比赛报告批量抓取脚本
 * 从fbref.com抓取每场比赛的详细数据并保存为JSON
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const DATA_DIR = path.join(__dirname, '../data');
const OUTPUT_DIR = path.join(DATA_DIR, 'match_reports');
const CDP_PORT = 9222;
const MATCH_URLS_FILE = path.join(DATA_DIR, 'match_urls.json');

// 创建输出目录
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// 读取比赛URL列表
const matchUrls = JSON.parse(fs.readFileSync(MATCH_URLS_FILE, 'utf-8'));

/**
 * 执行agent-browser命令
 */
function browserCmd(cmd, timeout = 30000) {
  const fullCmd = `agent-browser --cdp ${CDP_PORT} ${cmd}`;
  try {
    return execSync(fullCmd, { encoding: 'utf-8', timeout });
  } catch (error) {
    if (error.stdout) return error.stdout;
    throw error;
  }
}

/**
 * 等待
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 从页面提取完整比赛数据
 */
function extractMatchData(matchInfo) {
  const extractScript = `
    (function() {
      const data = {
        match: {},
        matchDetails: {},
        officials: {},
        lineups: { home: { players: [] }, away: { players: [] } },
        statistics: {},
        timeline: [],
        playerStats: { home: [], away: [] }
      };

      // 提取比赛标题
      const h1 = document.querySelector('h1');
      if (h1) {
        data.match.title = h1.textContent.trim();
        const parts = data.match.title.split(' vs. ');
        if (parts.length === 2) {
          data.match.homeTeam = parts[0].replace(' Match Report', '').trim();
          data.match.awayTeam = parts[1].split(' Match Report')[0].split(' – ')[0].trim();
        }
      }

      // 提取比分
      const scoreBoxes = document.querySelectorAll('.score');
      if (scoreBoxes.length >= 2) {
        data.match.homeScore = scoreBoxes[0]?.textContent?.trim();
        data.match.awayScore = scoreBoxes[1]?.textContent?.trim();
        data.match.result = data.match.homeScore + '-' + data.match.awayScore;
      }

      // 提取日期
      const dateSpan = document.querySelector('.venuetime');
      if (dateSpan) {
        data.match.date = dateSpan.textContent.trim();
      }

      // 提取各种信息框
      const infoBoxes = document.querySelectorAll('.content_wrapper .section_heading + div');
      infoBoxes.forEach(box => {
        const text = box.textContent;
        if (text.includes('Venue')) {
          const venueMatch = text.match(/Venue:\\s*(.+)/);
          if (venueMatch) data.match.venue = venueMatch[1].trim();
        }
      });

      // 提取阵容信息
      const lineupTables = document.querySelectorAll('table.lineup');
      lineupTables.forEach((table, idx) => {
        const teamName = table.querySelector('th')?.textContent?.trim();
        const players = [];
        table.querySelectorAll('tbody tr').forEach(row => {
          const cells = row.querySelectorAll('td');
          if (cells.length >= 2) {
            players.push({
              number: cells[0]?.textContent?.trim(),
              name: cells[1]?.textContent?.trim(),
              position: cells[2]?.textContent?.trim()
            });
          }
        });
        if (idx === 0) {
          data.lineups.home.team = teamName;
          data.lineups.home.players = players;
        } else {
          data.lineups.away.team = teamName;
          data.lineups.away.players = players;
        }
      });

      // 提取统计信息
      const statsTables = document.querySelectorAll('#team_stats, #all_stats_*');
      statsTables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
          const cells = row.querySelectorAll('td, th');
          if (cells.length >= 3) {
            const statName = cells[1]?.textContent?.trim();
            if (statName) {
              data.statistics[statName] = {
                home: cells[0]?.textContent?.trim(),
                away: cells[2]?.textContent?.trim()
              };
            }
          }
        });
      });

      // 提取球员详细统计
      const playerStatsTables = document.querySelectorAll('table.stats_table');
      playerStatsTables.forEach((table, idx) => {
        const isHome = idx % 2 === 0;
        const team = isHome ? 'home' : 'away';
        
        // 获取表头
        const headers = [];
        table.querySelectorAll('thead th').forEach(th => {
          headers.push(th.textContent.trim());
        });
        
        // 获取球员数据
        table.querySelectorAll('tbody tr').forEach(row => {
          const player = {};
          row.querySelectorAll('td').forEach((cell, i) => {
            if (headers[i]) {
              player[headers[i]] = cell.textContent.trim();
            }
          });
          if (Object.keys(player).length > 0) {
            data.playerStats[team].push(player);
          }
        });
      });

      // 提取比赛时间线（进球、黄牌、换人等）
      const events = document.querySelectorAll('.event');
      events.forEach(event => {
        const timeEl = event.querySelector('.minute');
        const typeEl = event.querySelector('.event_type');
        const playerEl = event.querySelector('.player a');
        const teamEl = event.querySelector('.team');
        
        if (timeEl && playerEl) {
          data.timeline.push({
            time: timeEl.textContent.trim(),
            type: typeEl?.textContent?.trim() || 'Unknown',
            player: playerEl.textContent.trim(),
            team: teamEl?.textContent?.trim()
          });
        }
      });

      return JSON.stringify(data);
    })();
  `;

  try {
    const result = browserCmd(`eval "${extractScript.replace(/"/g, '\\"').replace(/\n/g, ' ')}"`, 60000);
    return JSON.parse(result);
  } catch (error) {
    console.error('提取数据失败:', error.message);
    return null;
  }
}

/**
 * 抓取单场比赛报告
 */
async function scrapeMatch(match, index, total) {
  console.log(`\n[${index + 1}/${total}] 抓取: ${match.date} ${match.home} vs ${match.away}`);
  console.log(`  URL: ${match.url}`);

  try {
    // 打开比赛报告页面
    browserCmd(`open "${match.url}"`);
    await sleep(2000);
    
    // 等待页面加载
    try {
      browserCmd('wait --load networkidle --timeout 30000');
    } catch (e) {
      console.log('  ⚠ 页面加载超时，继续尝试...');
    }
    
    await sleep(1000);

    // 提取比赛数据
    const matchData = extractMatchData(match);
    
    if (matchData) {
      // 添加元数据
      matchData.match.id = match.index;
      matchData.match.date = match.date;
      matchData.match.competition = '中国足球协会超级联赛';
      matchData.match.season = '2024';
      matchData.sourceUrl = match.url;
      matchData.scrapedAt = new Date().toISOString();

      // 保存JSON文件
      const filename = `match_${match.date}_${String(index + 1).padStart(2, '0')}.json`;
      const filepath = path.join(OUTPUT_DIR, filename);
      fs.writeFileSync(filepath, JSON.stringify(matchData, null, 2));
      
      console.log(`  ✓ 已保存: ${filename}`);
      return { success: true, file: filename };
    } else {
      console.log(`  ✗ 提取数据失败`);
      return { success: false, error: '提取数据失败' };
    }

  } catch (error) {
    console.log(`  ✗ 错误: ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('='.repeat(70));
  console.log('  上海海港2024赛季比赛报告批量抓取工具');
  console.log('='.repeat(70));
  console.log(`  总计: ${matchUrls.length} 场比赛`);
  console.log(`  输出目录: ${OUTPUT_DIR}`);
  console.log('='.repeat(70));

  // 检查Chrome连接
  try {
    browserCmd('get url');
    console.log('✓ Chrome CDP连接成功\n');
  } catch (error) {
    console.error('✗ 无法连接到Chrome');
    console.error('  请确保Chrome已启动并开启远程调试端口9222');
    process.exit(1);
  }

  const results = {
    success: 0,
    failed: 0,
    errors: []
  };

  // 开始抓取
  for (let i = 0; i < matchUrls.length; i++) {
    const result = await scrapeMatch(matchUrls[i], i, matchUrls.length);
    
    if (result.success) {
      results.success++;
    } else {
      results.failed++;
      results.errors.push({
        match: matchUrls[i],
        error: result.error
      });
    }

    // 每场比赛之间延迟
    if (i < matchUrls.length - 1) {
      console.log('  等待 2 秒...');
      await sleep(2000);
    }
  }

  // 输出统计
  console.log('\n' + '='.repeat(70));
  console.log('  抓取完成！');
  console.log('='.repeat(70));
  console.log(`  成功: ${results.success} 场`);
  console.log(`  失败: ${results.failed} 场`);
  
  if (results.errors.length > 0) {
    console.log('\n  失败的比赛:');
    results.errors.forEach(err => {
      console.log(`    - ${err.match.date} ${err.match.home} vs ${err.match.away}: ${err.error}`);
    });
  }
  
  console.log('='.repeat(70));
}

// 运行
main().catch(console.error);
