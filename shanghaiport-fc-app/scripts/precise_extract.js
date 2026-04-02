#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/test_match_full.html', 'utf8');
const $ = cheerio.load(html);

console.log('='.repeat(80));
console.log('精确数据提取 - 修正版');
console.log('='.repeat(80));
console.log('');

// 1. 从阵容列表提取球员
console.log('【1. 从阵容列表提取球员】');
const lineups = { home: { name: '', players: [] }, away: { name: '', players: [] } };

// 查找包含阵容信息的div
$('div').each((i, elem) => {
  const text = $(elem).text();

  // 查找主队阵容
  if (text.includes('Shanghai Port (4-3-3)')) {
    console.log('找到主队阵容区域');
    // 提取球员名字和号码
    const playerText = text.match(/Shanghai Port \(4-3-3\)(.+?)Bench/s);
    if (playerText) {
      const starters = playerText[1];
      console.log('  首发:', starters.trim().substring(0, 200));

      // 解析每个球员
      const playerMatches = starters.matchAll(/(\d+)([A-Z][a-z]+(?: [A-Z][a-z]+)*)/g);
      for (const match of playerMatches) {
        lineups.home.players.push({
          number: parseInt(match[1]),
          name: match[2],
          isStarter: true
        });
      }
    }
  }

  // 查找客队阵容
  if (text.includes('Wuhan Three Towns (4-4-2)')) {
    console.log('找到客队阵容区域');
    const playerText = text.match(/Wuhan Three Towns \(4-4-2\)(.+?)Bench/s);
    if (playerText) {
      const starters = playerText[1];
      console.log('  首发:', starters.trim().substring(0, 200));
    }
  }
});

console.log(`\n主队球员数: ${lineups.home.players.length}`);
if (lineups.home.players.length > 0) {
  console.log('  前5名:', lineups.home.players.slice(0, 5).map(p => `${p.name}(#${p.number})`).join(', '));
}

// 2. 从表格提取详细数据
console.log('\n【2. 从统计表提取详细数据】');
let tableCount = 0;
$('table.stats_table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '';

  if (!id.includes('keeper')) {
    tableCount++;
    const rows = $table.find('tbody tr').length;
    console.log(`表格${tableCount} (${id}): ${rows}行`);

    // 检查第一行
    const firstRow = $table.find('tbody tr').first();
    const name = firstRow.find('th').text().trim();
    const cells = [];
    firstRow.find('td').slice(0, 5).each((j, cell) => {
      cells.push($(cell).text().trim());
    });

    console.log(`  第一名球员: ${name}`);
    console.log(`  前5个数据: ${cells.join(', ')}`);
  }
});

// 3. 提取比分
console.log('\n【3. 提取比分】');
let scoreFound = false;
$('div.score').each((i, elem) => {
  const score = $(elem).text().trim();
  if (score.match(/^\d+$/) && !scoreFound) {
    const nextScore = $(elem).next('div.score').text().trim();
    if (nextScore.match(/^\d+$/)) {
      console.log(`比分: ${score} - ${nextScore}`);
      scoreFound = true;
    }
  }
});

// 4. 提取比赛事件
console.log('\n【4. 提取比赛事件】');
let events = [];
$('div').each((i, elem) => {
  const text = $(elem).text();
  if (text.match(/\d+' /) && (text.includes('Goal') || text.includes('Substitute') || text.includes('Yellow'))) {
    const timeMatch = text.match(/(\d+'\d*).*?(Goal|Substitute|Yellow)/);
    if (timeMatch) {
      events.push(timeMatch[0]);
    }
  }
});

if (events.length > 0) {
  console.log(`找到 ${events.length} 个事件`);
  events.slice(0, 5).forEach(e => console.log(`  - ${e}`));
}

// 5. 提取统计数据
console.log('\n【5. 提取统计数据】');
let foundStats = false;
$('div').each((i, elem) => {
  const text = $(elem).text();
  if (text.includes('67%') && text.includes('33%') && text.includes('Possession')) {
    if (!foundStats) {
      console.log('找到统计数据区域');
      foundStats = true;
    }
  }
});

console.log('\n' + '='.repeat(80));
console.log('✅ 提取测试完成');
console.log('='.repeat(80));
