#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('========================================');
console.log('最终版 - 完整准确数据提取');
console.log('========================================\n');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

// ========== 1. 基本信息 ==========
console.log('【1. 比赛基本信息】');
const title = $('title').text();
const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report\s+–\s+(.+?)\s*\|/);

const matchData = {
  homeTeam: titleMatch[1].trim(),
  awayTeam: titleMatch[2].trim(),
  date: titleMatch[3].trim(),
  homeScore: 0,
  awayScore: 0,
  venue: '',
  attendance: ''
};

// 提取比分 - 查找div.score元素
const scores = [];
$('div.score').each((i, elem) => {
  const score = $(elem).text().trim();
  if (score.match(/^\d+$/)) {
    scores.push(parseInt(score));
  }
});

if (scores.length >= 2) {
  matchData.homeScore = scores[0];
  matchData.awayScore = scores[1];
}

// 提取场馆和观众
const bodyText = $('body').text();
const venueMatch = bodyText.match(/Venue:\s*([^A-Z\n]{10,100})/);
if (venueMatch) matchData.venue = venueMatch[1].trim();

const attMatch = bodyText.match(/Attendance:\s*([\d,]+)/);
if (attMatch) matchData.attendance = attMatch[1];

console.log(`主队: ${matchData.homeTeam}`);
console.log(`客队: ${matchData.awayTeam}`);
console.log(`日期: ${matchData.date}`);
console.log(`比分: ${matchData.homeScore} - ${matchData.awayScore}`);
console.log(`场馆: ${matchData.venue}`);
console.log(`观众: ${matchData.attendance}`);
console.log('');

// ========== 2. 球员数据 - 改进版 ==========
console.log('【2. 球员详细统计】');

const allPlayers = { home: [], away: [] };
let tableIndex = 0;

// 查找所有统计表
$('table.stats_table').each((i, table) => {
  const $table = $(table);
  const tableId = $table.attr('id') || '';
  
  // 跳过门将表
  if (tableId.includes('keeper')) return;
  
  const team = tableIndex < 1 ? 'home' : 'away';
  tableIndex++;
  
  console.log(`处理表格 ${tableIndex} (${team})`);
  
  let playerCount = 0;
  
  $table.find('tr').each((rowIndex, row) => {
    const $row = $(row);
    
    // 球员姓名在th中
    const name = $row.find('th').text().trim();
    
    // 其他数据在td中
    const cells = [];
    $row.find('td').each((j, cell) => {
      cells.push($(cell).text().trim());
    });
    
    // 需要至少13个td，并且姓名不为空，不是表头
    if (name && cells.length >= 13 && !name.includes('Player')) {
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
      
      // 只要球员有名字就保存（不检查分钟数）
      allPlayers[team].push(player);
      playerCount++;
    }
  });
  
  console.log(`  提取 ${playerCount} 名球员`);
});

console.log(`\n总计: ${allPlayers.home.length + allPlayers.away.length} 名球员`);
console.log(`  主队: ${allPlayers.home.length}人`);
console.log(`  客队: ${allPlayers.away.length}人\n`);

// ========== 3. 统计数据 ==========
console.log('【3. 统计数据】');

const stats = [];
let foundTeamStats = false;

$('div').each((i, elem) => {
  const text = $(elem).text();
  
  if (text.includes('Team Stats')) {
    foundTeamStats = true;
  }
  
  if (foundTeamStats && text.includes('Possession')) {
    const possMatches = text.match(/(\d+)%/g);
    if (possMatches && possMatches.length >= 2) {
      stats.push({ name: '控球率', home: possMatches[0], away: possMatches[1] });
      console.log(`控球率: ${possMatches[0]} vs ${possMatches[1]}`);
      foundTeamStats = false;
    }
  }
  
  if (text.includes('Shots on Target')) {
    const shotsMatches = text.match(/(\d+)\s+of\s+(\d+)/g);
    if (shotsMatches && shotsMatches.length >= 2) {
      const home = shotsMatches[0].match(/(\d+)\s+of\s+(\d+)/);
      const away = shotsMatches[1].match(/(\d+)\s+of\s+(\d+)/);
      if (home && away) {
        stats.push({ name: '射正', home: home[1], away: away[1] });
        stats.push({ name: '射门', home: home[2], away: away[2] });
        console.log(`射正: ${home[1]} vs ${away[1]}`);
        console.log(`射门: ${home[2]} vs ${away[2]}`);
      }
    }
  }
});

console.log('');

// ========== 4. 保存完整CSV ==========
console.log('【4. 保存完整CSV】');

const csvRows = [];
csvRows.push(['类别', '项目', '主队/值', '客队/值', '详情']);

// 比赛信息
csvRows.push(['比赛信息', '主队', matchData.homeTeam, '', '']);
csvRows.push(['比赛信息', '客队', matchData.awayTeam, '', '']);
csvRows.push(['比赛信息', '日期', matchData.date, '', '']);
csvRows.push(['比赛信息', '比分', matchData.homeScore, matchData.awayScore, '']);
csvRows.push(['比赛信息', '场馆', matchData.venue, '', '']);
csvRows.push(['比赛信息', '观众', matchData.attendance, '', '']);

// 球员数据
csvRows.push(['', '', '', '', '']);
csvRows.push(['主队球员', '姓名', '号码', '位置', '分钟/进球/助攻']);

allPlayers.home.forEach(p => {
  csvRows.push([
    '主队',
    p.name,
    p.number,
    p.position,
    `${p.minutes}分/${p.goals}球/${p.assists}助`
  ]);
});

csvRows.push(['客队球员', '姓名', '号码', '位置', '分钟/进球/助攻']);

allPlayers.away.forEach(p => {
  csvRows.push([
    '客队',
    p.name,
    p.number,
    p.position,
    `${p.minutes}分/${p.goals}球/${p.assists}助`
  ]);
});

// 统计数据
csvRows.push(['', '', '', '', '']);
csvRows.push(['统计数据', '项目', '主队', '客队', '']);

stats.forEach(s => {
  csvRows.push(['统计', s.name, s.home, s.away, '']);
});

const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/complete_match_data.csv', '\ufeff' + csvContent, 'utf8');

console.log(`✓ 已保存: data/complete_match_data.csv`);
console.log(`  共 ${csvRows.length} 行`);

console.log('\n========================================');
console.log('✅ 完成！');
console.log('========================================');
console.log(`\n最终数据:`);
console.log(`  比赛信息: 6项 ✅`);
console.log(`  主队球员: ${allPlayers.home.length}人 ${allPlayers.home.length >= 11 ? '✅' : '⚠️'}`);
console.log(`  客队球员: ${allPlayers.away.length}人 ${allPlayers.away.length >= 11 ? '✅' : '⚠️'}`);
console.log(`  统计数据: ${stats.length}项 ${stats.length > 0 ? '✅' : '⚠️'}`);
