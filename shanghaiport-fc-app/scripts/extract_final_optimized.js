#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

console.log('='.repeat(80));
console.log('最终优化版 - 完整数据提取');
console.log('='.repeat(80));
console.log('');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

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

// 提取比分 - 改进逻辑
const scores = [];
let foundScore = false;

$('div').each((i, elem) => {
  if (foundScore) return;
  
  const text = $(elem).text().trim();
  if (text.match(/^\d+$/) && text.length <= 2) {
    const nextDiv = $(elem).next('div');
    if (nextDiv.length > 0) {
      const nextText = nextDiv.text().trim();
      if (nextText.match(/^\d+$/) && nextText.length <= 2) {
        scores.push(parseInt(text));
        scores.push(parseInt(nextText));
        foundScore = true;
      }
    }
  }
});

if (scores.length >= 2) {
  matchInfo.homeScore = scores[0];
  matchInfo.awayScore = scores[1];
  console.log(`比分: ${matchInfo.homeScore} - ${matchInfo.awayScore}`);
}

// 提取观众
const bodyText = $('body').text();
const attMatch = bodyText.match(/Attendance:\s*([\d,]+)/);
if (attMatch) {
  matchInfo.attendance = attMatch[1];
  console.log(`观众: ${matchInfo.attendance}`);
}

console.log('');

// ============ 2. 球员详细统计 - 改进版 ============
console.log('【2. 球员详细统计】');

const allPlayers = { home: [], away: [] };
let currentTeam = 'home';

// 查找所有包含球员统计的表格
$('table').each((tableIndex, table) => {
  const $table = $(table);
  const tableId = $table.attr('id') || '';
  const tableClass = $table.attr('class') || '';
  
  // 检查是否是球员统计表
  if (tableClass.includes('stats_table') && !tableId.includes('keeper')) {
    console.log(`处理表格: ${tableId}`);
    
    const team = currentTeam;
    let rowCount = 0;
    
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      
      // 球员姓名在th中
      const name = $row.find('th').text().trim();
      
      // 其他数据在td中
      const cells = [];
      $row.find('td').each((cellIndex, cell) => {
        cells.push($(cell).text().trim());
      });
      
      if (name && cells.length >= 13) {
        const minutes = parseInt(cells[5]) || 0;
        
        if (minutes > 0) {
          const player = {
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
          };
          
          allPlayers[team].push(player);
          rowCount++;
        }
      }
    });
    
    console.log(`  ${team === 'home' ? '主队' : '客队'}: 提取${rowCount}人`);
    
    // 切换到客队
    if (currentTeam === 'home') {
      currentTeam = 'away';
    }
  }
});

if (allPlayers.home.length > 0) {
  console.log(`\n主队首发前3: ${allPlayers.home.slice(0, 3).map(p => `${p.name}(${p.minutes}分)`).join(', ')}`);
}
if (allPlayers.away.length > 0) {
  console.log(`客队首发前3: ${allPlayers.away.slice(0, 3).map(p => `${p.name}(${p.minutes}分)`).join(', ')}`);
}

console.log('');

// ============ 3. 比赛事件 ============
console.log('【3. 比赛事件】');

const events = [];

// 在整个HTML中查找事件模式
const htmlText = $('body').text();

// 查找进球
const goalMatches = htmlText.matchAll(/(\d+'\d*)\s+([^\n]*?Goal[^\n]*)/g);
for (const match of goalMatches) {
  events.push({
    minute: match[1],
    type: '进球',
    description: match[2].trim()
  });
}

// 查找换人
const subMatches = htmlText.matchAll(/(\d+'\d*)\s+([^\n]*?(?:substituted|Substitute)[^\n]*)/g);
for (const match of subMatches) {
  events.push({
    minute: match[1],
    type: '换人',
    description: match[2].trim()
  });
}

// 查找黄牌
const yellowMatches = htmlText.matchAll(/(\d+'\d*)\s+([^\n]*?Yellow[^\n]*)/g);
for (const match of yellowMatches) {
  events.push({
    minute: match[1],
    type: '黄牌',
    description: match[2].trim()
  });
}

// 去重并排序
const uniqueEvents = [];
const eventKeys = new Set();
events.forEach(e => {
  const key = `${e.minute}-${e.type}`;
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

console.log(`找到 ${uniqueEvents.length} 个比赛事件`);
uniqueEvents.slice(0, 10).forEach(e => {
  console.log(`  ${e.minute} - [${e.type}] ${e.description.substring(0, 50)}`);
});

console.log('');

// ============ 4. 统计数据 ============
console.log('【4. 统计数据】');

const stats = [];
let foundPossession = false;
let foundShots = false;

$('div').each((i, elem) => {
  const text = $(elem).text();
  
  // 查找控球率
  if (text.includes('Possession') && !foundPossession) {
    const possMatches = text.match(/(\d+)%/g);
    if (possMatches && possMatches.length >= 2) {
      stats.push({ name: '控球率', home: possMatches[0], away: possMatches[1] });
      console.log(`控球率: ${possMatches[0]} vs ${possMatches[1]}`);
      foundPossession = true;
    }
  }
  
  // 查找射门
  if (text.includes('Shots on Target') && !foundShots) {
    const shotsMatches = text.match(/(\d+)\s+of\s+(\d+)/g);
    if (shotsMatches && shotsMatches.length >= 2) {
      const home = shotsMatches[0].match(/(\d+)\s+of\s+(\d+)/);
      const away = shotsMatches[1].match(/(\d+)\s+of\s+(\d+)/);
      if (home && away) {
        stats.push({ name: '射正', home: home[1], away: away[1] });
        stats.push({ name: '射门', home: home[2], away: away[2] });
        console.log(`射正: ${home[1]} vs ${away[1]}`);
        console.log(`射门: ${home[2]} vs ${away[2]}`);
        foundShots = true;
      }
    }
  }
});

console.log('');

// ============ 5. 保存CSV ============
console.log('【5. 保存CSV】');

const csvRows = [];
csvRows.push(['类别', '项目', '主队/值', '客队/值', '详情']);

// 比赛信息
csvRows.push(['比赛信息', '主队', matchInfo.homeTeam, '', '']);
csvRows.push(['比赛信息', '客队', matchInfo.awayTeam, '', '']);
csvRows.push(['比赛信息', '日期', matchInfo.date, '', '']);
csvRows.push(['比赛信息', '比分', matchInfo.homeScore || 0, matchInfo.awayScore || 0, '']);
csvRows.push(['比赛信息', '观众', matchInfo.attendance || '', '', '']);

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

// 事件
csvRows.push(['', '', '', '', '']);
csvRows.push(['比赛事件', '时间', '类型', '描述', '']);

uniqueEvents.forEach(e => {
  csvRows.push(['事件', e.minute, e.type, e.description.substring(0, 60), '']);
});

// 统计
csvRows.push(['', '', '', '', '']);
csvRows.push(['统计数据', '项目', '主队', '客队', '']);

stats.forEach(s => {
  csvRows.push(['统计', s.name, s.home, s.away, '']);
});

const csvContent = csvRows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
fs.writeFileSync('./data/final_optimized_data.csv', '\ufeff' + csvContent, 'utf8');

console.log(`✓ 已保存CSV: data/final_optimized_data.csv`);
console.log(`  共 ${csvRows.length} 行数据`);

console.log('');
console.log('='.repeat(80));
console.log('✅ 最终数据提取完成！');
console.log('='.repeat(80));
console.log(`\n数据汇总:`);
console.log(`  主队球员: ${allPlayers.home.length}人 ${allPlayers.home.length >= 11 ? '✅' : '⚠️'}`);
console.log(`  客队球员: ${allPlayers.away.length}人 ${allPlayers.away.length >= 11 ? '✅' : '⚠️'}`);
console.log(`  比赛事件: ${uniqueEvents.length}个 ${uniqueEvents.length > 0 ? '✅' : '⚠️'}`);
console.log(`  统计数据: ${stats.length}项 ${stats.length > 0 ? '✅' : '⚠️'}`);
