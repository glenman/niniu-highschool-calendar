#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('========================================');
console.log('终极版 - 完整准确数据提取');
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

// 提取比分
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

// 提取观众
const bodyText = $('body').text();
const attMatch = bodyText.match(/Attendance:\s*([\d,]+)/);
if (attMatch) matchData.attendance = attMatch[1];

console.log(`主队: ${matchData.homeTeam}`);
console.log(`客队: ${matchData.awayTeam}`);
console.log(`日期: ${matchData.date}`);
console.log(`比分: ${matchData.homeScore} - ${matchData.awayScore}`);
console.log(`观众: ${matchData.attendance}`);
console.log('');

// ========== 2. 球员数据 - 直接遍历所有tr ==========
console.log('【2. 球员详细统计】');

const allPlayers = { home: [], away: [] };
let currentTeam = 'home';

// 查找所有表格
$('table.stats_table').each((tableIndex, table) => {
  const $table = $(table);
  const tableId = $table.attr('id') || '';
  
  // 跳过门将表
  if (tableId.includes('keeper')) return;
  
  // 切换队伍
  if (tableIndex > 0 && currentTeam === 'home') {
    currentTeam = 'away';
  }
  
  console.log(`处理表格 ${tableIndex + 1} (${currentTeam})`);
  
  let playerCount = 0;
  
  // 遍历所有行
  $table.find('tr').each((rowIndex, row) => {
    const $row = $(row);
    
    // 跳过表头行
    const thText = $row.find('th').text().trim();
    if (thText.includes('Player') || thText.includes('#')) return;
    
    // 获取所有单元格
    const cells = [];
    
    // 球员姓名在th
    const name = thText;
    
    // 其他数据在td
    $row.find('td').each((j, cell) => {
      cells.push($(cell).text().trim());
    });
    
    // 如果有名字且有足够的数据列
    if (name && name.length > 0 && cells.length >= 13) {
      // 解析数据
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
      
      // 保存所有球员（不检查分钟数）
      allPlayers[currentTeam].push(player);
      playerCount++;
    }
  });
  
  console.log(`  提取 ${playerCount} 名球员`);
});

console.log(`\n总计: ${allPlayers.home.length + allPlayers.away.length} 名球员`);
console.log(`  主队: ${allPlayers.home.length}人`);
console.log(`  客队: ${allPlayers.away.length}人`);

if (allPlayers.home.length > 0) {
  console.log(`\n主队前5名:`);
  allPlayers.home.slice(0, 5).forEach(p => {
    console.log(`  ${p.name} (#${p.number}) - ${p.position} - ${p.minutes}分钟 ${p.goals}球/${p.assists}助`);
  });
}

if (allPlayers.away.length > 0) {
  console.log(`\n客队前5名:`);
  allPlayers.away.slice(0, 5).forEach(p => {
    console.log(`  ${p.name} (#${p.number}) - ${p.position} - ${p.minutes}分钟 ${p.goals}球/${p.assists}助`);
  });
}

console.log('');

// ========== 3. 统计数据 ==========
console.log('【3. 统计数据】');

const stats = [];
let foundStats = false;

$('div').each((i, elem) => {
  const text = $(elem).text();
  
  // 查找Team Stats后的控球率
  if (text.includes('Team Stats')) {
    foundStats = true;
  }
  
  if (foundStats && text.includes('Possession')) {
    const possMatch = text.match(/(\d+)%.*?(\d+)%/);
    if (possMatch) {
      stats.push({ name: '控球率', home: possMatch[1] + '%', away: possMatch[2] + '%' });
      console.log(`控球率: ${possMatch[1]}% vs ${possMatch[2]}%`);
      foundStats = false;
    }
  }
  
  // 射门数据
  if (text.includes('Shots on Target')) {
    const shotsMatch = text.match(/(\d+)\s+of\s+(\d+).*?(\d+)\s+of\s+(\d+)/);
    if (shotsMatch) {
      stats.push({ name: '射正', home: shotsMatch[1], away: shotsMatch[3] });
      stats.push({ name: '射门', home: shotsMatch[2], away: shotsMatch[4] });
      console.log(`射正: ${shotsMatch[1]} vs ${shotsMatch[3]}`);
      console.log(`射门: ${shotsMatch[2]} vs ${shotsMatch[4]}`);
    }
  }
});

console.log('');

// ========== 4. 保存CSV ==========
console.log('【4. 保存CSV】');

const csvRows = [];
csvRows.push(['类别', '项目', '主队/值', '客队/值', '详情']);

// 比赛信息
csvRows.push(['比赛信息', '主队', matchData.homeTeam, '', '']);
csvRows.push(['比赛信息', '客队', matchData.awayTeam, '', '']);
csvRows.push(['比赛信息', '日期', matchData.date, '', '']);
csvRows.push(['比赛信息', '比分', matchData.homeScore, matchData.awayScore, '']);
csvRows.push(['比赛信息', '观众', matchData.attendance, '', '']);

// 主队球员
csvRows.push(['', '', '', '', '']);
csvRows.push(['主队球员', '姓名', '号码', '位置', '分钟/进球/助攻']);

allPlayers.home.forEach(p => {
  csvRows.push([
    p.name,
    `#${p.number}`,
    p.position,
    `${p.minutes}分`,
    `${p.goals}球/${p.assists}助`
  ]);
});

// 客队球员
csvRows.push(['', '', '', '', '']);
csvRows.push(['客队球员', '姓名', '号码', '位置', '分钟/进球/助攻']);

allPlayers.away.forEach(p => {
  csvRows.push([
    p.name,
    `#${p.number}`,
    p.position,
    `${p.minutes}分`,
    `${p.goals}球/${p.assists}助`
  ]);
});

// 统计数据
csvRows.push(['', '', '', '', '']);
csvRows.push(['统计数据', '项目', '主队', '客队', '']);

stats.forEach(s => {
  csvRows.push(['统计', s.name, s.home, s.away, '']);
});

const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/final_match_data.csv', '\ufeff' + csvContent, 'utf8');

console.log(`✓ 已保存: data/final_match_data.csv`);
console.log(`  共 ${csvRows.length} 行`);

console.log('\n========================================');
console.log('✅ 完成！');
console.log('========================================');
console.log(`\n数据汇总:`);
console.log(`  比赛信息: 5项 ✅`);
console.log(`  主队球员: ${allPlayers.home.length}人 ${allPlayers.home.length >= 11 ? '✅' : '⚠️'}`);
console.log(`  客队球员: ${allPlayers.away.length}人 ${allPlayers.away.length >= 11 ? '✅' : '⚠️'}`);
console.log(`  统计数据: ${stats.length}项 ${stats.length > 0 ? '✅' : '⚠️'}`);
