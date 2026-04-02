#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/scraped_html_live/match_1.html', 'utf8');
const $ = cheerio.load(html);

console.log('检查HTML结构...\n');

// 查找所有表格
console.log('=== 所有表格 ===');
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '无ID';
  const className = $table.attr('class') || '无class';
  const rows = $table.find('tbody tr').length;

  if (className.includes('stats_table')) {
    console.log(`\n表格 ${i+1}:`);
    console.log(`  ID: ${id}`);
    console.log(`  Class: ${className}`);
    console.log(`  行数: ${rows}`);

    // 提取第一行
    const firstRow = $table.find('tbody tr').first();
    const cells = [];
    firstRow.find('td, th').each((j, cell) => {
      const text = $(cell).text().trim();
      cells.push(text.substring(0, 30));
    });
    if (cells.length > 0) {
      console.log(`  第一行 (${cells.length}列): ${cells.slice(0, 8).join(' | ')}`);
    }
  }
});

console.log('\n\n=== 检查完成 ===');
