#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('========================================');
console.log('直接抓取方案 - 提取所有比赛数据');
console.log('========================================\n');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

// ========== 1. 基本信息 ==========
console.log('【1. 比赛基本信息】');
const title = $('title').text();
console.log('标题:', title);

const matchData = {
  homeTeam: '',
  awayTeam: '',
  date: '',
  homeScore: 0,
  awayScore: 0,
  venue: '',
  attendance: ''
};

// 提取球队和日期
const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report\s+–\s+(.+?)\s*\|/);
if (titleMatch) {
  matchData.homeTeam = titleMatch[1].trim();
  matchData.awayTeam = titleMatch[2].trim();
  matchData.date = titleMatch[3].trim();
  console.log(`主队: ${matchData.homeTeam}`);
  console.log(`客队: ${matchData.awayTeam}`);
  console.log(`日期: ${matchData.date}`);
}

// 提取比分 - 查找所有两位数以内的数字
const allNumbers = [];
$('div').each((i, elem) => {
  const text = $(elem).text().trim();
  if (text.match(/^\d{1,2}$/)) {
    allNumbers.push(parseInt(text));
  }
});

// 前两个数字应该是比分
if (allNumbers.length >= 2) {
  matchData.homeScore = allNumbers[0];
  matchData.awayScore = allNumbers[1];
  console.log(`比分: ${matchData.homeScore} - ${matchData.awayScore}`);
}

// 提取观众
const bodyText = $('body').text();
const attMatch = bodyText.match(/Attendance:\s*([\d,]+)/);
if (attMatch) {
  matchData.attendance = attMatch[1];
  console.log(`观众: ${matchData.attendance}`);
}

console.log('');

// ========== 2. 球员数据 - 直接提取所有行 ==========
console.log('【2. 球员数据】');

const allPlayers = [];
let currentTeam = 'home';
let tableNum = 0;

$('table').each((tableIndex, table) => {
  const $table = $(table);
  const tableId = $table.attr('id') || '';
  const tableClass = $table.attr('class') || '';
  
  // 只处理球员统计表，跳过门将表
  if (tableClass.includes('stats_table') && !tableId.includes('keeper')) {
    tableNum++;
    const team = tableNum === 1 ? 'home' : 'away';
    
    console.log(`\n处理表格 ${tableNum} (${team}):`);
    
    // 直接查找所有行（包括thead和tbody）
    let rowCount = 0;
    $table.find('tr').each((rowIndex, row) => {
      const $row = $(row);
      
      // 跳过表头行（第一行通常是表头）
      if (rowIndex === 0) return;
      
      // 提取球员姓名（在th中）
      const playerName = $row.find('th').text().trim();
      
      // 提取其他数据（在td中）
      const cells = [];
      $row.find('td').each((cellIndex, cell) => {
        cells.push($(cell).text().trim());
      });
      
      // 如果有球员姓名和足够的单元格
      if (playerName && playerName !== 'Player' && cells.length >= 13) {
        const player = {
          team: team,
          name: playerName,
          number: cells[0] || '',
          nationality: cells[1] || '',
          position: cells[3] || '',
          minutes: cells[5] || '0',
          goals: cells[6] || '0',
          assists: cells[7] || '0',
          shots: cells[10] || '0',
          shotsOnTarget: cells[11] || '0',
          yellowCards: cells[12] || '0',
          redCards: cells[13] || '0'
        };
        
        allPlayers.push(player);
        rowCount++;
      }
    });
    
    console.log(`  提取 ${rowCount} 名球员`);
  }
});

console.log(`\n总计: ${allPlayers.length} 名球员`);
console.log(`  主队: ${allPlayers.filter(p => p.team === 'home').length}人`);
console.log(`  客队: ${allPlayers.filter(p => p.team === 'away').length}人`);

// 显示前5名
if (allPlayers.length > 0) {
  console.log('\n前5名球员:');
  allPlayers.slice(0, 5).forEach(p => {
    console.log(`  ${p.team === 'home' ? '主' : '客'} - ${p.name} (#${p.number}): ${p.minutes}分钟`);
  });
}

console.log('');

// ========== 3. 统计数据 ==========
console.log('【3. 统计数据】');

const stats = [];
let foundPossession = false;
let foundShots = false;

// 在整个文本中查找
const fullText = $('body').text();

// 查找控球率
if (!foundPossession) {
  const possMatches = fullText.match(/Possession[^0-9]*(\d+)%[^0-9]*(\d+)%/);
  if (possMatches) {
    stats.push({ name: '控球率', home: possMatches[1] + '%', away: possMatches[2] + '%' });
    console.log(`控球率: ${possMatches[1]}% vs ${possMatches[2]}%`);
    foundPossession = true;
  }
}

// 查找射门
if (!foundShots) {
  const shotsMatches = fullText.match(/Shots on Target[^0-9]*(\d+)\s+of\s+(\d+)[^0-9]*(\d+)\s+of\s+(\d+)/);
  if (shotsMatches) {
    stats.push({ name: '射正', home: shotsMatches[1], away: shotsMatches[3] });
    stats.push({ name: '射门', home: shotsMatches[2], away: shotsMatches[4] });
    console.log(`射正: ${shotsMatches[1]} vs ${shotsMatches[3]}`);
    console.log(`射门: ${shotsMatches[2]} vs ${shotsMatches[4]}`);
    foundShots = true;
  }
}

console.log('');

// ========== 4. 保存CSV ==========
console.log('【4. 保存CSV】');

const csvRows = [];

// 标题行
csvRows.push(['类别', '字段1', '字段2', '字段3', '字段4', '字段5']);

// 比赛信息
csvRows.push(['比赛信息', '主队', matchData.homeTeam, '', '', '']);
csvRows.push(['比赛信息', '客队', matchData.awayTeam, '', '', '']);
csvRows.push(['比赛信息', '日期', matchData.date, '', '', '']);
csvRows.push(['比赛信息', '比分', matchData.homeScore, matchData.awayScore, '', '']);
csvRows.push(['比赛信息', '观众', matchData.attendance, '', '', '']);

// 球员数据
csvRows.push(['', '', '', '', '', '']);
csvRows.push(['主队球员', '姓名', '号码', '分钟', '进球', '助攻']);

allPlayers.filter(p => p.team === 'home').forEach(p => {
  csvRows.push(['主队', p.name, p.number, p.minutes, p.goals, p.assists]);
});

csvRows.push(['客队球员', '姓名', '号码', '分钟', '进球', '助攻']);

allPlayers.filter(p => p.team === 'away').forEach(p => {
  csvRows.push(['客队', p.name, p.number, p.minutes, p.goals, p.assists]);
});

// 统计数据
csvRows.push(['', '', '', '', '', '']);
csvRows.push(['统计数据', '项目', '主队', '客队', '', '']);

stats.forEach(s => {
  csvRows.push(['统计', s.name, s.home, s.away, '', '']);
});

// 保存CSV
const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/direct_extract_data.csv', '\ufeff' + csvContent, 'utf8');

console.log(`✓ 已保存: data/direct_extract_data.csv`);
console.log(`  共 ${csvRows.length} 行`);

console.log('\n========================================');
console.log('✅ 完成！');
console.log('========================================');
console.log(`\n数据汇总:`);
console.log(`  球员: ${allPlayers.length}人`);
console.log(`  统计: ${stats.length}项`);
