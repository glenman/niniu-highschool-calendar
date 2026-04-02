#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('='.repeat(80));
console.log('优化版 - 完整数据提取');
console.log('='.repeat(80));
console.log('');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
// 处理压缩的HTML（可能是单行）
const formattedHtml = html.replace(/></g, '>\n<');
const $ = cheerio.load(formattedHtml);

// ============ 1. 比赛基本信息 ============
console.log('【1. 比赛基本信息】');

const title = $('title').text();
console.log('标题:', title);

// 提取球队和日期
const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report\s+–\s+(.+?)\s*\|/);
const matchData = {
  homeTeam: titleMatch ? titleMatch[1].trim() : '',
  awayTeam: titleMatch ? titleMatch[2].trim() : '',
  date: titleMatch ? titleMatch[3].trim() : ''
};

console.log('主队:', matchData.homeTeam);
console.log('客队:', matchData.awayTeam);
console.log('日期:', matchData.date);

// 提取比分 - 查找相邻的score div
let homeScore = 0, awayScore = 0;
const scoreDivs = [];
$('div.score').each((i, elem) => {
  const score = $(elem).text().trim();
  if (score.match(/^\d+$/)) {
    scoreDivs.push(parseInt(score));
  }
});

if (scoreDivs.length >= 2) {
  homeScore = scoreDivs[0];
  awayScore = scoreDivs[1];
  console.log('比分:', `${homeScore} - ${awayScore}`);
}

// 提取场馆信息
$('div').each((i, elem) => {
  const text = $(elem).text();
  if (text.includes('Venue:') && !matchData.venue) {
    const venueMatch = text.match(/Venue:\s*([^A-Z]+)/);
    if (venueMatch) {
      matchData.venue = venueMatch[1].trim();
      console.log('场馆:', matchData.venue);
    }
  }
  if (text.includes('Attendance:') && !matchData.attendance) {
    const attMatch = text.match(/Attendance:\s*([\d,]+)/);
    if (attMatch) {
      matchData.attendance = attMatch[1];
      console.log('观众:', matchData.attendance);
    }
  }
});

console.log('');

// ============ 2. 球队阵容（从阵容列表提取） ============
console.log('【2. 球队阵容】');

const teams = [];

// 查找阵容列表
$('div').each((i, elem) => {
  const text = $(elem).text();
  
  // 主队阵容
  if (text.includes('Shanghai Port (4-3-3)') && teams.length === 0) {
    const lineupMatch = text.match(/Shanghai Port \(4-3-3\)(.+?)Bench/s);
    if (lineupMatch) {
      const playerStr = lineupMatch[1];
      const players = [];
      
      // 解析球员：数字+姓名
      const playerMatches = playerStr.matchAll(/(\d+)([A-Z][a-z]+(?: [A-Z][a-z' ]+)?)/g);
      for (const match of playerMatches) {
        players.push({
          number: parseInt(match[1]),
          name: match[2].trim(),
          isStarter: true
        });
      }
      
      teams.push({
        name: 'Shanghai Port',
        formation: '4-3-3',
        players: players
      });
      
      console.log(`主队 Shanghai Port: ${players.length}人`);
      console.log(`  首发: ${players.slice(0, 11).map(p => `${p.name}(#${p.number})`).join(', ')}`);
    }
  }
  
  // 客队阵容
  if (text.includes('Wuhan Three Towns (4-4-2)') && teams.length === 1) {
    const lineupMatch = text.match(/Wuhan Three Towns \(4-4-2\)(.+?)Bench/s);
    if (lineupMatch) {
      const playerStr = lineupMatch[1];
      const players = [];
      
      const playerMatches = playerStr.matchAll(/(\d+)([A-Z][a-z]+(?: [A-Z][a-z' ]+)?)/g);
      for (const match of playerMatches) {
        players.push({
          number: parseInt(match[1]),
          name: match[2].trim(),
          isStarter: true
        });
      }
      
      teams.push({
        name: 'Wuhan Three Towns',
        formation: '4-4-2',
        players: players
      });
      
      console.log(`客队 Wuhan Three Towns: ${players.length}人`);
      console.log(`  首发: ${players.slice(0, 11).map(p => `${p.name}(#${p.number})`).join(', ')}`);
    }
  }
});

console.log('');

// ============ 3. 球员详细统计（从表格提取） ============
console.log('【3. 球员详细统计】');

const playerStats = {
  home: [],
  away: []
};

let tableIndex = 0;
$('table.stats_table').each((i, table) => {
  const $table = $(table);
  const tableId = $table.attr('id') || '';
  
  // 跳过门将统计
  if (tableId.includes('keeper')) return;
  
  const team = tableIndex < 1 ? 'home' : 'away';
  tableIndex++;
  
  console.log(`\n处理${team === 'home' ? '主队' : '客队'}统计表...`);
  
  $table.find('tbody tr').each((rowIndex, row) => {
    const $row = $(row);
    
    // 球员姓名在th中
    const name = $row.find('th').text().trim();
    
    // 其他数据在td中
    const cells = [];
    $row.find('td').each((j, cell) => {
      cells.push($(cell).text().trim());
    });
    
    if (name && cells.length >= 13) {
      const player = {
        name: name,
        number: parseInt(cells[0]) || 0,
        nationality: cells[1] || '',
        position: cells[3] || '',
        age: cells[4] || '',
        minutes: parseInt(cells[5]) || 0,
        goals: parseInt(cells[6]) || 0,
        assists: parseInt(cells[7]) || 0,
        shots: parseInt(cells[10]) || 0,
        shotsOnTarget: parseInt(cells[11]) || 0,
        yellowCards: parseInt(cells[12]) || 0,
        redCards: parseInt(cells[13]) || 0
      };
      
      if (player.minutes > 0) {
        playerStats[team].push(player);
      }
    }
  });
  
  console.log(`  提取到 ${playerStats[team].length} 名球员`);
  if (playerStats[team].length > 0) {
    console.log(`  前3名: ${playerStats[team].slice(0, 3).map(p => p.name).join(', ')}`);
  }
});

console.log('');

// ============ 4. 比赛事件 ============
console.log('【4. 比赛事件】');

const events = [];
$('div').each((i, elem) => {
  const $elem = $(elem);
  const text = $elem.text();
  
  // 查找包含时间的事件
  if (text.match(/\d+'/)) {
    const lines = text.split('\n');
    lines.forEach(line => {
      const trimmed = line.trim();
      
      // 检测进球
      if (trimmed.match(/\d+'/) && trimmed.includes('Goal')) {
        const timeMatch = trimmed.match(/(\d+'\d*).*?Goal.*?(\d+:\d+)/);
        if (timeMatch) {
          const playerMatch = trimmed.match(/([A-Z][a-z]+ [A-Z][a-z]+)/);
          events.push({
            minute: timeMatch[1],
            type: '进球',
            score: timeMatch[2],
            player: playerMatch ? playerMatch[1] : ''
          });
        }
      }
      
      // 检测黄牌
      if (trimmed.match(/\d+'/) && trimmed.includes('Yellow')) {
        const timeMatch = trimmed.match(/(\d+'\d*)/);
        const playerMatch = trimmed.match(/([A-Z][a-z]+ [A-Z][a-z]+)/);
        if (timeMatch && playerMatch) {
          events.push({
            minute: timeMatch[1],
            type: '黄牌',
            player: playerMatch[1]
          });
        }
      }
      
      // 检测换人
      if (trimmed.match(/\d+'/) && trimmed.includes('Substitute')) {
        const timeMatch = trimmed.match(/(\d+'\d*)/);
        const playerMatch = trimmed.match(/([A-Z][a-z]+ [A-Z][a-z]+).*?for ([A-Z][a-z]+ [A-Z][a-z]+)/);
        if (timeMatch && playerMatch) {
          events.push({
            minute: timeMatch[1],
            type: '换人',
            playerIn: playerMatch[1],
            playerOut: playerMatch[2]
          });
        }
      }
    });
  }
});

// 去重
const uniqueEvents = [];
const eventKeys = new Set();
events.forEach(e => {
  const key = `${e.minute}-${e.type}-${e.player || e.playerIn || ''}`;
  if (!eventKeys.has(key)) {
    eventKeys.add(key);
    uniqueEvents.push(e);
  }
});

uniqueEvents.sort((a, b) => {
  const minA = parseInt(a.minute.replace("'", ''));
  const minB = parseInt(b.minute.replace("'", ''));
  return minA - minB;
});

console.log(`找到 ${uniqueEvents.length} 个比赛事件:`);
uniqueEvents.forEach(e => {
  if (e.type === '进球') {
    console.log(`  ${e.minute} - [进球] ${e.player} (${e.score})`);
  } else if (e.type === '黄牌') {
    console.log(`  ${e.minute} - [黄牌] ${e.player}`);
  } else if (e.type === '换人') {
    console.log(`  ${e.minute} - [换人] ${e.playerIn} 替换 ${e.playerOut}`);
  }
});

console.log('');

// ============ 5. 统计数据 ============
console.log('【5. 统计数据】');

const stats = [];
let foundStats = false;

$('div').each((i, elem) => {
  const text = $(elem).text();
  
  if (text.includes('Possession') && text.includes('%')) {
    if (!foundStats) {
      // 提取控球率
      const possMatches = text.match(/(\d+)%/g);
      if (possMatches && possMatches.length >= 2) {
        stats.push({
          name: '控球率',
          home: possMatches[0],
          away: possMatches[1]
        });
        console.log(`控球率: ${possMatches[0]} vs ${possMatches[1]}`);
      }
    }
  }
  
  if (text.includes('Shots on Target')) {
    const shotsMatch = text.match(/(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)/);
    if (shotsMatch) {
      stats.push({
        name: '射正',
        home: shotsMatch[1],
        away: shotsMatch[3]
      });
      stats.push({
        name: '射门',
        home: shotsMatch[2],
        away: shotsMatch[4]
      });
      console.log(`射正: ${shotsMatch[1]} vs ${shotsMatch[3]}`);
      console.log(`射门: ${shotsMatch[2]} vs ${shotsMatch[4]}`);
      foundStats = true;
    }
  }
});

console.log('');

// ============ 6. 保存完整CSV ============
console.log('【6. 保存完整CSV】');

const csvRows = [];
csvRows.push(['数据类型', '字段1', '字段2', '字段3', '字段4', '备注']);

// 比赛信息
csvRows.push(['比赛信息', '主队', matchData.homeTeam, '', '', '']);
csvRows.push(['比赛信息', '客队', matchData.awayTeam, '', '', '']);
csvRows.push(['比赛信息', '日期', matchData.date, '', '', '']);
csvRows.push(['比赛信息', '比分', homeScore, awayScore, '', '']);
csvRows.push(['比赛信息', '场馆', matchData.venue || '', '', '', '']);
csvRows.push(['比赛信息', '观众', matchData.attendance || '', '', '', '']);

// 球员统计
csvRows.push(['', '', '', '', '', '']);
csvRows.push(['主队球员统计', '姓名', '号码', '位置', '分钟', '进球/助攻']);

playerStats.home.forEach(p => {
  csvRows.push([
    '主队球员',
    p.name,
    p.number,
    p.position,
    p.minutes,
    `${p.goals}球/${p.assists}助`
  ]);
});

csvRows.push(['', '', '', '', '', '']);
csvRows.push(['客队球员统计', '姓名', '号码', '位置', '分钟', '进球/助攻']);

playerStats.away.forEach(p => {
  csvRows.push([
    '客队球员',
    p.name,
    p.number,
    p.position,
    p.minutes,
    `${p.goals}球/${p.assists}助`
  ]);
});

// 比赛事件
csvRows.push(['', '', '', '', '', '']);
csvRows.push(['比赛事件', '时间', '类型', '球员/详情', '', '']);

uniqueEvents.forEach(e => {
  if (e.type === '进球') {
    csvRows.push(['事件', e.minute, e.type, `${e.player} (${e.score})`, '', '']);
  } else if (e.type === '黄牌') {
    csvRows.push(['事件', e.minute, e.type, e.player, '', '']);
  } else if (e.type === '换人') {
    csvRows.push(['事件', e.minute, e.type, `${e.playerIn} 替 ${e.playerOut}`, '', '']);
  }
});

// 统计数据
csvRows.push(['', '', '', '', '', '']);
csvRows.push(['统计数据', '项目', '主队', '客队', '', '']);

stats.forEach(s => {
  csvRows.push(['统计', s.name, s.home, s.away, '', '']);
});

// 保存CSV
const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/test_match_complete.csv', '\ufeff' + csvContent, 'utf8');

console.log(`✓ 已保存完整CSV: data/test_match_complete.csv`);
console.log(`  共 ${csvRows.length} 行数据`);

console.log('');
console.log('='.repeat(80));
console.log('✅ 数据提取完成！');
console.log('='.repeat(80));

console.log('\n数据汇总:');
console.log(`  比赛信息: 6项`);
console.log(`  主队球员: ${playerStats.home.length}人`);
console.log(`  客队球员: ${playerStats.away.length}人`);
console.log(`  比赛事件: ${uniqueEvents.length}个`);
console.log(`  统计数据: ${stats.length}项`);
