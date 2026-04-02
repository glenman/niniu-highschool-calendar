#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

// 使用已知的完整HTML文件
const htmlFile = './data/scraped_html_live/match_1.html';

if (!fs.existsSync(htmlFile)) {
  console.error(`❌ 文件不存在: ${htmlFile}`);
  console.log('可用的文件:');
  const files = fs.readdirSync('./data/scraped_html_live').filter(f => f.endsWith('.html'));
  files.forEach(f => console.log(`  - ${f}`));
  process.exit(1);
}

console.log('='.repeat(80));
console.log('最终版 - 完整数据提取');
console.log('使用HTML:', htmlFile);
console.log('='.repeat(80));
console.log('');

const html = fs.readFileSync(htmlFile, 'utf8');
const $ = cheerio.load(html);

// 1. 比赛基本信息
console.log('【1. 比赛基本信息】');

const title = $('title').text();
const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report/);

if (titleMatch) {
  console.log('主队:', titleMatch[1].trim());
  console.log('客队:', titleMatch[2].trim());
}

const scores = [];
$('div.score').each((i, elem) => {
  const score = $(elem).text().trim();
  if (score.match(/^\d+$/)) {
    scores.push(parseInt(score));
  }
});

if (scores.length >= 2) {
  console.log('比分:', `${scores[0]} - ${scores[1]}`);
}

const body = $('body').text();
const venueMatch = body.match(/Venue:\s*([^A-Z\n]{10,100})/);
if (venueMatch) {
  console.log('场馆:', venueMatch[1].trim());
}

const attMatch = body.match(/Attendance:\s*([\d,]+)/);
if (attMatch) {
  console.log('观众:', attMatch[1]);
}

console.log('');

// 2. 球员统计
console.log('【2. 球员详细统计】');

const allPlayers = { home: [], away: [] };
let tableIndex = 0;

$('table').each((i, table) => {
  const $table = $(table);
  const tableId = $table.attr('id') || '';
  const tableClass = $table.attr('class') || '';
  
  if (tableClass.includes('stats_table') && !tableId.includes('keeper')) {
    const team = tableIndex < 1 ? 'home' : 'away';
    tableIndex++;
    
    let rowCount = 0;
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
        const minutes = parseInt(cells[5]) || 0;
        
        if (minutes > 0) {
          allPlayers[team].push({
            name: name,
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
          });
          rowCount++;
        }
      }
    });
    
    console.log(`${team === 'home' ? '主队' : '客队'}: ${rowCount}人`);
  }
});

if (allPlayers.home.length > 0) {
  console.log(`  主队前3名: ${allPlayers.home.slice(0, 3).map(p => `${p.name}(${p.minutes}分钟)`).join(', ')}`);
}
if (allPlayers.away.length > 0) {
  console.log(`  客队前3名: ${allPlayers.away.slice(0, 3).map(p => `${p.name}(${p.minutes}分钟)`).join(', ')}`);
}

console.log('');

// 3. 统计数据
console.log('【3. 统计数据】');

const stats = [];

// 查找Team Stats部分
let foundTeamStats = false;
$('div').each((i, elem) => {
  const text = $(elem).text();
  
  if (text.includes('Team Stats')) {
    foundTeamStats = true;
  }
  
  if (foundTeamStats && text.includes('%')) {
    const possMatch = text.match(/(\d+)%/g);
    if (possMatch && possMatch.length >= 2) {
      stats.push({ name: '控球率', home: possMatch[0], away: possMatch[1] });
      console.log(`控球率: ${possMatch[0]} vs ${possMatch[1]}`);
      foundTeamStats = false; // 只提取一次
    }
  }
});

console.log('');

// 4. 保存完整CSV
console.log('【4. 保存完整CSV】');

const csvRows = [];
csvRows.push(['类别', '项目', '主队', '客队', '详情']);

// 比赛信息
csvRows.push(['比赛', '主队', titleMatch ? titleMatch[1] : '', '', '']);
csvRows.push(['比赛', '客队', titleMatch ? titleMatch[2] : '', '', '']);
csvRows.push(['比赛', '比分', scores[0] || 0, scores[1] || 0, '']);

// 球员
csvRows.push(['', '', '', '', '']);
csvRows.push(['主队球员', '姓名', '号码', '分钟', '进球/助攻']);

allPlayers.home.forEach(p => {
  csvRows.push(['主队', p.name, p.number, p.minutes, `${p.goals}/${p.assists}`]);
});

csvRows.push(['客队球员', '姓名', '号码', '分钟', '进球/助攻']);

allPlayers.away.forEach(p => {
  csvRows.push(['客队', p.name, p.number, p.minutes, `${p.goals}/${p.assists}`]);
});

// 统计
csvRows.push(['', '', '', '', '']);
csvRows.push(['统计', '项目', '主队', '客队', '']);

stats.forEach(s => {
  csvRows.push(['统计', s.name, s.home, s.away, '']);
});

const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/final_match_data.csv', '\ufeff' + csvContent, 'utf8');

console.log(`✓ 已保存: data/final_match_data.csv`);
console.log(`  共 ${csvRows.length} 行`);

console.log('');
console.log('='.repeat(80));
console.log('✅ 完成！');
console.log('='.repeat(80));
console.log(`\n最终数据:`);
console.log(`  主队球员: ${allPlayers.home.length}人`);
console.log(`  客队球员: ${allPlayers.away.length}人`);
console.log(`  统计数据: ${stats.length}项`);
