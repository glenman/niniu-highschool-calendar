#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/scraped_html_live/match_1.html', 'utf8');
const $ = cheerio.load(html);

console.log('=== 详细检查第1轮数据 ===\n');

// 1. 检查比分
console.log('1. 查找比分:');
let scoreCount = 0;
$('div, span, strong, p').each((i, elem) => {
  const text = $(elem).text().trim();
  if (text.match(/^\d+\s*-\s*\d+$/)) {
    scoreCount++;
    if (scoreCount <= 5) {
      console.log(`  候选${scoreCount}: "${text}" - 父元素: ${$(elem).parent().prop('tagName')}`);
    }
  }
});
console.log(`  共找到 ${scoreCount} 个比分候选`);

// 2. 检查球员表格
console.log('\n2. 球员表格:');
let tableNum = 0;
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '';
  const className = $table.attr('class') || '';

  if (className.includes('stats_table') && !id.includes('keeper')) {
    tableNum++;
    const allRows = $table.find('tbody tr').length;
    const validRows = $table.find('tbody tr').filter((j, row) => {
      const cells = $(row).find('td');
      const minutes = parseInt($(cells[5]).text().trim()) || 0;
      return minutes > 0;
    }).length;

    console.log(`  表格${tableNum}: ${id}`);
    console.log(`    总行数: ${allRows}, 有效行数(分钟>0): ${validRows}`);

    // 检查前5行
    $table.find('tbody tr').slice(0, 5).each((rowIndex, row) => {
      const $row = $(row);
      const name = $row.find('td').eq(0).text().trim();
      const minutes = parseInt($row.find('td').eq(5).text().trim()) || 0;
      console.log(`    球员${rowIndex+1}: ${name} (${minutes}分钟)`);
    });
  }
});

console.log('\n=== 检查完成 ===');
