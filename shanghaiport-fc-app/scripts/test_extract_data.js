#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/test_match_full.html', 'utf8');
const $ = cheerio.load(html);

console.log('='.repeat(80));
console.log('比赛报告数据提取测试');
console.log('='.repeat(80));
console.log('');

// 1. 比赛基本信息
console.log('【1. 比赛基本信息】');
const title = $('title').text();
console.log('页面标题:', title);

// 提取球队名称
const matchInfo = title.match(/(.+?)\s+vs\.\s+(.+?)\s+Match Report/);
if (matchInfo) {
  console.log('主队:', matchInfo[1].trim());
  console.log('客队:', matchInfo[2].trim());
}

// 提取比分
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

// 提取日期
const dateText = title.match(/–\s*(.+?)$/);
if (dateText) {
  console.log('日期:', dateText[1].trim());
}

// 提取时间
$('*').each((i, elem) => {
  const text = $(elem).text();
  if (text.includes('Kick-off')) {
    const timeMatch = text.match(/Kick-off:\s*(\d+:\d+)/);
    if (timeMatch) {
      console.log('开球时间:', timeMatch[1]);
    }
  }
});

// 提取场馆
$('*').each((i, elem) => {
  const text = $(elem).text();
  if (text.includes('Venue')) {
    const venueMatch = text.match(/Venue:\s*([^\n]+)/);
    if (venueMatch) {
      console.log('场馆:', venueMatch[1].trim());
    }
  }
});

console.log('');

// 2. 球队阵容和替补
console.log('【2. 球队阵容和替补】');
let teamCount = 0;
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '';
  const className = $table.attr('class') || '';

  if (className.includes('stats_table') && !id.includes('keeper')) {
    teamCount++;
    const team = teamCount === 1 ? '主队' : '客队';

    const players = [];
    $table.find('tbody tr').each((rowIndex, row) => {
      const $row = $(row);
      const cells = [];
      $row.find('td').each((j, cell) => {
        cells.push($(cell).text().trim());
      });

      if (cells.length >= 13) {
        const player = {
          name: cells[0] || '',
          number: parseInt(cells[1]) || 0,
          position: cells[3] || '',
          minutes: parseInt(cells[5]) || 0
        };
        if (player.name && player.minutes > 0) {
          players.push(player);
        }
      }
    });

    console.log(`${team}: ${players.length}人`);
    console.log(`  首发: ${players.slice(0, 11).map(p => `${p.name}(#${p.number})`).join(', ')}`);
    if (players.length > 11) {
      console.log(`  替补: ${players.slice(11).map(p => `${p.name}(#${p.number})`).join(', ')}`);
    }
    console.log('');
  }
});

// 3. 比赛事件
console.log('【3. 比赛事件】');
let events = [];
$('*').each((i, elem) => {
  const text = $(elem).text();
  // 查找包含时间的事件
  if (text.match(/\d+'\s+(Goal|Substitute|Yellow|Red)/i)) {
    events.push(text.trim());
  }
});

if (events.length > 0) {
  events.slice(0, 10).forEach(event => {
    console.log('  -', event.substring(0, 100));
  });
} else {
  console.log('  未找到比赛事件（可能需要更精确的选择器）');
}

console.log('');

// 4. 统计数据
console.log('【4. 统计数据】');
$('*').each((i, elem) => {
  const text = $(elem).text();
  if (text.includes('Possession')) {
    console.log('  找到控球率区域');
  }
  if (text.includes('Shots on Target')) {
    console.log('  找到射门统计区域');
  }
});

console.log('');

// 5. 球员详细统计
console.log('【5. 球员详细统计示例】');
let tableNum = 0;
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '';
  const className = $table.attr('class') || '';

  if (className.includes('stats_table') && !id.includes('keeper') && tableNum < 1) {
    tableNum++;
    const firstRow = $table.find('tbody tr').first();
    const cells = [];
    firstRow.find('td').slice(0, 15).each((j, cell) => {
      cells.push($(cell).text().trim());
    });

    console.log('  第一名球员数据:');
    console.log('    姓名:', cells[0]);
    console.log('    号码:', cells[1]);
    console.log('    国籍:', cells[2]);
    console.log('    位置:', cells[3]);
    console.log('    年龄:', cells[4]);
    console.log('    分钟:', cells[5]);
    console.log('    进球:', cells[6]);
    console.log('    助攻:', cells[7]);
    console.log('    射门:', cells[10]);
    console.log('    射正:', cells[11]);
    console.log('    黄牌:', cells[12]);
    console.log('    红牌:', cells[13]);
  }
});

console.log('');
console.log('='.repeat(80));
console.log('✓ 测试完成');
console.log('='.repeat(80));
