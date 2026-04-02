#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('='.repeat(80));
console.log('智能解析 - 完整数据提取');
console.log('='.repeat(80));
console.log('');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

// 1. 比赛基本信息
console.log('【1. 比赛基本信息】');

const title = $('title').text();
const titleMatch = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report/);

if (titleMatch) {
  console.log('主队:', titleMatch[1].trim());
  console.log('客队:', titleMatch[2].trim());
}

// 提取比分
const scoreElements = [];
$('div').each((i, elem) => {
  const text = $(elem).text().trim();
  if (text.match(/^\d+$/) && text.length <= 2) {
    scoreElements.push(parseInt(text));
  }
});

if (scoreElements.length >= 2) {
  console.log('比分:', `${scoreElements[0]} - ${scoreElements[1]}`);
}

// 提取场馆和观众
const bodyText = $('body').text();

const venueMatch = bodyText.match(/Venue:\s*([^A-Z\n]+)/);
if (venueMatch) {
  console.log('场馆:', venueMatch[1].trim());
}

const attMatch = bodyText.match(/Attendance:\s*([\d,]+)/);
if (attMatch) {
  console.log('观众:', attMatch[1]);
}

console.log('');

// 2. 球员详细统计
console.log('【2. 球员详细统计】');

const allPlayers = {
  home: [],
  away: []
};

let currentTeam = 'home';
let playerCount = 0;

// 查找所有包含球员统计的表格
$('table').each((tableIndex, table) => {
  const $table = $(table);
  const tableHtml = $table.html();
  
  // 检查是否是球员统计表（包含特定的列标题）
  if (tableHtml.includes('Player') && tableHtml.includes('Min') && tableHtml.includes('Gls')) {
    
    // 提取表格中的所有行
    $table.find('tr').each((rowIndex, row) => {
      const $row = $(row);
      
      // 跳过表头行
      if ($row.find('th').length === 0) return;
      
      const cells = [];
      
      // 提取th（球员姓名）
      const playerName = $row.find('th').text().trim();
      
      // 提取td（其他数据）
      $row.find('td').each((cellIndex, cell) => {
        cells.push($(cell).text().trim());
      });
      
      if (playerName && cells.length >= 13) {
        const player = {
          name: playerName,
          number: parseInt(cells[0]) || 0,
          nationality: cells[1] || '',
          position: cells[3] || '',
          minutes: parseInt(cells[5]) || 0,
          goals: parseInt(cells[6]) || 0,
          assists: parseInt(cells[7]) || 0,
          shots: parseInt(cells[10]) || 0,
          shotsOnTarget: parseInt(cells[11]) || 0,
          yellowCards: parseInt(cells[12]) || 0,
          redCards: parseInt(cells[13]) || 0
        };
        
        if (player.minutes > 0) {
          if (playerCount < 16) {
            allPlayers.home.push(player);
          } else {
            allPlayers.away.push(player);
          }
          playerCount++;
        }
      }
    });
  }
});

console.log(`主队: ${allPlayers.home.length}人`);
console.log(`客队: ${allPlayers.away.length}人`);

if (allPlayers.home.length > 0) {
  console.log(`  主队前5名: ${allPlayers.home.slice(0, 5).map(p => p.name).join(', ')}`);
}

if (allPlayers.away.length > 0) {
  console.log(`  客队前5名: ${allPlayers.away.slice(0, 5).map(p => p.name).join(', ')}`);
}

console.log('');

// 3. 比赛事件
console.log('【3. 比赛事件】');

const events = [];
$('div').each((i, elem) => {
  const text = $(elem).text();
  
  // 查找进球事件
  if (text.match(/\d+'/) && text.includes('Goal')) {
    const goalMatch = text.match(/(\d+'\d*)\s+(.+?)\s+Goal/);
    if (goalMatch) {
    events.push({
      minute: goalMatch[1],
      type: '进球',
      description: goalMatch[2].trim()
    });
  }
  }
  
  // 查找换人事件
  if (text.match(/\d+'/) && text.includes('substituted')) {
    const subMatch = text.match(/(\d+'\d*)\s+(.+?)\s+substituted/);
    if (subMatch) {
    events.push({
      minute: subMatch[1],
      type: '换人',
      description: subMatch[2].trim()
    });
  }
  }
  
  // 查找黄牌事件
  if (text.match(/\d+'/) && text.includes('Yellow')) {
    const yellowMatch = text.match(/(\d+'\d*)\s+(.+?)\s+Yellow/);
    if (yellowMatch) {
    events.push({
      minute: yellowMatch[1],
      type: '黄牌',
      description: yellowMatch[2].trim()
    });
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

// 4. 统计数据
console.log('【4. 统计数据】');

const stats = [];
let foundPossession = false;

$('div').each((i, elem) => {
  const text = $(elem).text();
  
  if (text.includes('Possession') && !foundPossession) {
    const possMatch = text.match(/(\d+)%.*?(\d+)%/);
    if (possMatch) {
    stats.push({ name: '控球率', home: possMatch[1] + '%', away: possMatch[2] + '%' });
    console.log(`控球率: ${possMatch[1]}% vs ${possMatch[2]}%`);
    foundPossession = true;
  }
  }
});

console.log('');

// 5. 保存CSV
console.log('【5. 保存CSV】');

const csvRows = [];
csvRows.push(['数据类型', '字段1', '字段2', '字段3', '字段4']);

// 比赛信息
csvRows.push(['比赛', '主队', titleMatch ? titleMatch[1] : '', '', '']);
csvRows.push(['比赛', '客队', titleMatch ? titleMatch[2] : '', '', '']);
csvRows.push(['比赛', '比分', scoreElements[0] || 0, scoreElements[1] || 0, '']);

// 球员数据
csvRows.push(['', '', '', '', '']);
csvRows.push(['主队球员', '姓名', '号码', '分钟', '进球/助攻']);

allPlayers.home.forEach(p => {
  csvRows.push(['主队', p.name, p.number, p.minutes, `${p.goals}/${p.assists}`]);
});

csvRows.push(['客队球员', '姓名', '号码', '分钟', '进球/助攻']);

allPlayers.away.forEach(p => {
  csvRows.push(['客队', p.name, p.number, p.minutes, `${p.goals}/${p.assists}`]);
});

// 事件
csvRows.push(['', '', '', '', '']);
csvRows.push(['比赛事件', '时间', '类型', '描述', '']);

events.forEach(e => {
  csvRows.push(['事件', e.minute, e.type, e.description.substring(0, 40), '']);
});

// 统计
csvRows.push(['', '', '', '', '']);
csvRows.push(['统计数据', '项目', '主队', '客队', '']);

stats.forEach(s => {
  csvRows.push(['统计', s.name, s.home, s.away, '']);
});

const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/match_complete_data.csv', '\ufeff' + csvContent, 'utf8');

console.log(`✓ 已保存CSV: data/match_complete_data.csv`);
console.log(`  共 ${csvRows.length} 行`);

console.log('');
console.log('='.repeat(80));
console.log('✅ 完成！');
console.log('='.repeat(80));
console.log(`\n数据汇总:`);
console.log(`  主队球员: ${allPlayers.home.length}人`);
console.log(`  客队球员: ${allPlayers.away.length}人`);
console.log(`  比赛事件: ${events.length}个`);
console.log(`  统计数据: ${stats.length}项`);
