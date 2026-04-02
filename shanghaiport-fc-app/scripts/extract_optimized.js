#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('='.repeat(80));
console.log('优化版 - 完整比赛数据提取');
console.log('='.repeat(80));
console.log('');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

console.log(`HTML大小: ${(html.length / 1024).toFixed(1)} KB\n`);

// ============ 1. 比赛基本信息 ============
console.log('【1. 比赛基本信息】');

const title = $('title').text();
const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report\s+–\s+(.+?)\s*\|/);

const matchInfo = {
  homeTeam: titleMatch ? titleMatch[1].trim() : '',
  awayTeam: titleMatch ? titleMatch[2].trim() : '',
  date: titleMatch ? titleMatch[3].trim() : ''
};

console.log(`主队: ${matchInfo.homeTeam}`);
console.log(`客队: ${matchInfo.awayTeam}`);
console.log(`日期: ${matchInfo.date}`);

// 提取比分
const scores = [];
$('div.score').each((i, elem) => {
  const score = $(elem).text().trim();
  if (score.match(/^\d+$/) && score.length <= 2) {
    scores.push(parseInt(score));
  }
});

if (scores.length >= 2) {
  matchInfo.homeScore = scores[0];
  matchInfo.awayScore = scores[1];
  console.log(`比分: ${matchInfo.homeScore} - ${matchInfo.awayScore}`);
}

// 提取场馆和观众
const bodyText = $('body').text();

const venueMatch = bodyText.match(/Venue:\s*([^\n]{10,100}?)(?:Attendance|$)/);
if (venueMatch) {
  matchInfo.venue = venueMatch[1].trim();
  console.log(`场馆: ${matchInfo.venue}`);
}

const attMatch = bodyText.match(/Attendance:\s*([\d,]+)/);
if (attMatch) {
  matchInfo.attendance = attMatch[1];
  console.log(`观众: ${matchInfo.attendance}`);
}

console.log('');

// ============ 2. 球员详细统计 ============
console.log('【2. 球员详细统计】');

const allPlayers = { home: [], away: [] };
let tableCount = 0;

$('table').each((i, table) => {
  const $table = $(table);
  const tableId = $table.attr('id') || '';
  const tableClass = $table.attr('class') || '';
  
  // 只处理球员统计表（跳过门将表）
  if (tableClass.includes('stats_table') && !tableId.includes('keeper')) {
    const team = tableCount < 1 ? 'home' : 'away';
    tableCount++;
    
    let playerCount = 0;
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      
      // 球员姓名在th中
      const playerName = $row.find('th').text().trim();
      
      // 其他数据在td中
      const cells = [];
      $row.find('td').each((j, cell) => {
        cells.push($(cell).text().trim());
      });
      
      if (playerName && cells.length >= 13) {
        const minutes = parseInt(cells[5]) || 0;
        
        if (minutes > 0) {
          const player = {
            name: playerName,
            number: parseInt(cells[0]) || 0,
            nationality: cells[1] || '',
            position: cells[3] || '',
            age: cells[4] || '',
            minutes: minutes,
            goals: parseInt(cells[6]) || 0,
            assists: parseInt(cells[7]) || 0,
            shots: parseInt(cells[10]) || 0,
            shotsOnTarget: parseInt(cells[11]) || 0,
            yellowCards: parseInt(cells[12]) || 0,
            redCards: parseInt(cells[13]) || 0
          };
          
          allPlayers[team].push(player);
          playerCount++;
        }
      }
    });
    
    console.log(`${team === 'home' ? '主队' : '客队'}: ${playerCount}人`);
  }
});

if (allPlayers.home.length > 0) {
  console.log(`  主队首发: ${allPlayers.home.slice(0, 5).map(p => p.name).join(', ')}...`);
}
if (allPlayers.away.length > 0) {
  console.log(`  客队首发: ${allPlayers.away.slice(0, 5).map(p => p.name).join(', ')}...`);
}

console.log('');

// ============ 3. 比赛事件 ============
console.log('【3. 比赛事件】');

const events = [];

// 查找Match Summary部分
let inMatchSummary = false;
$('div, h2').each((i, elem) => {
  const $elem = $(elem);
  const text = $elem.text().trim();
  
  if (text.includes('Match Summary')) {
    inMatchSummary = true;
  }
  
  if (inMatchSummary && text.match(/\d+'/)) {
    // 提取事件
    if (text.includes('Goal')) {
      const goalMatch = text.match(/(\d+'\d*)\s+(.+)/);
      if (goalMatch) {
        events.push({
          minute: goalMatch[1],
          type: '进球',
          description: goalMatch[2].trim()
        });
      }
    } else if (text.includes('Yellow')) {
      const yellowMatch = text.match(/(\d+'\d*)\s+(.+)/);
      if (yellowMatch) {
        events.push({
          minute: yellowMatch[1],
          type: '黄牌',
          description: yellowMatch[2].trim()
        });
      }
    } else if (text.includes('substituted') || text.includes('Substitute')) {
      const subMatch = text.match(/(\d+'\d*)\s+(.+)/);
      if (subMatch) {
        events.push({
          minute: subMatch[1],
          type: '换人',
          description: subMatch[2].trim()
        });
      }
    }
  }
});

// 按时间排序
events.sort((a, b) => {
  const minA = parseInt(a.minute.replace("'", ''));
  const minB = parseInt(b.minute.replace("'", ''));
  return minA - minB;
});

console.log(`找到 ${events.length} 个比赛事件`);
events.forEach(e => {
  console.log(`  ${e.minute} - [${e.type}] ${e.description.substring(0, 50)}`);
});

console.log('');

// ============ 4. 统计数据 ============
console.log('【4. 统计数据】');

const stats = [];
let foundTeamStats = false;
let possCount = 0;

$('div').each((i, elem) => {
  const text = $(elem).text();
  
  if (text.includes('Team Stats')) {
    foundTeamStats = true;
  }
  
  if (foundTeamStats) {
    if (text.includes('Possession') && possCount === 0) {
      const possMatch = text.match(/(\d+)%/g);
      if (possMatch && possMatch.length >= 2) {
        stats.push({ name: '控球率', home: possMatch[0], away: possMatch[1] });
        console.log(`控球率: ${possMatch[0]} vs ${possMatch[1]}`);
        possCount++;
      }
    }
    
    if (text.includes('Shots on Target')) {
      const shotsMatch = text.match(/(\d+)\s+of\s+(\d+)/g);
      if (shotsMatch && shotsMatch.length >= 2) {
        const home = shotsMatch[0].match(/(\d+)\s+of\s+(\d+)/);
        const away = shotsMatch[1].match(/(\d+)\s+of\s+(\d+)/);
        if (home && away) {
          stats.push({ name: '射正', home: home[1], away: away[1] });
          stats.push({ name: '射门', home: home[2], away: away[2] });
          console.log(`射正: ${home[1]} vs ${away[1]}`);
          console.log(`射门: ${home[2]} vs ${away[2]}`);
        }
      }
    }
  }
});

console.log('');

// ============ 5. 保存完整CSV ============
console.log('【5. 保存完整CSV】');

const csvRows = [];
csvRows.push(['类别', '项目', '主队/值', '客队/值', '详情']);

// 比赛信息
csvRows.push(['比赛信息', '主队', matchInfo.homeTeam, '', '']);
csvRows.push(['比赛信息', '客队', matchInfo.awayTeam, '', '']);
csvRows.push(['比赛信息', '日期', matchInfo.date, '', '']);
csvRows.push(['比赛信息', '比分', matchInfo.homeScore || 0, matchInfo.awayScore || 0, '']);
csvRows.push(['比赛信息', '场馆', matchInfo.venue || '', '', '']);
csvRows.push(['比赛信息', '观众', matchInfo.attendance || '', '', '']);

// 球员数据
csvRows.push(['', '', '', '', '']);
csvRows.push(['主队球员', '姓名', '号码', '位置', '分钟/进球/助攻']);

allPlayers.home.forEach((p, idx) => {
  csvRows.push([
    idx < 11 ? '首发' : '替补',
    p.name,
    p.number,
    p.position,
    `${p.minutes}分钟 ${p.goals}球 ${p.assists}助`
  ]);
});

csvRows.push(['', '', '', '', '']);
csvRows.push(['客队球员', '姓名', '号码', '位置', '分钟/进球/助攻']);

allPlayers.away.forEach((p, idx) => {
  csvRows.push([
    idx < 11 ? '首发' : '替补',
    p.name,
    p.number,
    p.position,
    `${p.minutes}分钟 ${p.goals}球 ${p.assists}助`
  ]);
});

// 比赛事件
csvRows.push(['', '', '', '', '']);
csvRows.push(['比赛事件', '时间', '类型', '描述', '']);

events.forEach(e => {
  csvRows.push(['事件', e.minute, e.type, e.description.substring(0, 60), '']);
});

// 统计数据
csvRows.push(['', '', '', '', '']);
csvRows.push(['统计数据', '项目', '主队', '客队', '']);

stats.forEach(s => {
  csvRows.push(['统计', s.name, s.home, s.away, '']);
});

const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/match_optimized_data.csv', '\ufeff' + csvContent, 'utf8');

console.log(`✓ 已保存CSV: data/match_optimized_data.csv`);
console.log(`  共 ${csvRows.length} 行数据`);

console.log('');
console.log('='.repeat(80));
console.log('✅ 数据提取完成！');
console.log('='.repeat(80));
console.log(`\n数据汇总:`);
console.log(`  比赛信息: 6项 ✅`);
console.log(`  主队球员: ${allPlayers.home.length}人 ${allPlayers.home.length >= 11 ? '✅' : '⚠️'}`);
console.log(`  客队球员: ${allPlayers.away.length}人 ${allPlayers.away.length >= 11 ? '✅' : '⚠️'}`);
console.log(`  比赛事件: ${events.length}个 ${events.length > 0 ? '✅' : '⚠️'}`);
console.log(`  统计数据: ${stats.length}项 ${stats.length > 0 ? '✅' : '⚠️'}`);
