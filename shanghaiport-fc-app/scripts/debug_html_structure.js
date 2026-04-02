#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/scraped_html_live/match_1.html', 'utf8');
const $ = cheerio.load(html);

console.log('=== 详细检查HTML结构 ===\n');

// 1. 标题
console.log('1. 页面标题:');
console.log('  ', $('title').text());

// 2. 比分
console.log('\n2. 比分元素:');
$('div').each((i, elem) => {
  const text = $(elem).text().trim();
  if (text.match(/^\d+\s*-\s*\d+$/)) {
    console.log('  找到比分:', text);
  }
});

// 3. 球队名称 - 从标题h1提取
console.log('\n3. 球队名称:');
$('h1').each((i, elem) => {
  const text = $(elem).text();
  if (text.includes('vs.') || text.includes('Match Report')) {
    console.log('  h1:', text.substring(0, 100));
  }
});

// 4. 日期
console.log('\n4. 日期:');
$('[class*="heading"]').each((i, elem) => {
  const text = $(elem).text();
  if (text.match(/March|April|May|June|July|August|September|October|November/)) {
    console.log('  日期元素:', text.substring(0, 100));
  }
});

// 5. 统计表格
console.log('\n5. 统计表格:');
let tableNum = 0;
$('table[id^="stats_"][id$="_summary"]').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id');
  const rows = $table.find('tbody tr').length;

  tableNum++;
  console.log(`  表格${tableNum}: ${id} (${rows}行)`);

  // 显示前3个球员
  $table.find('tbody tr').slice(0, 3).each((rowIndex, row) => {
    const $row = $(row);
    const cells = [];
    $row.find('td').slice(0, 8).each((j, cell) => {
      cells.push($(cell).text().trim().substring(0, 15));
    });
    console.log(`    球员${rowIndex+1}:`, cells.join(' | '));
  });
});

console.log('\n=== 检查完成 ===');
