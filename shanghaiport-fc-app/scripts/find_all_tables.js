#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/scraped_html_live/match_1.html', 'utf8');
const $ = cheerio.load(html);

console.log('=== 查找所有表格 ===\n');

let tableCount = 0;
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '无ID';
  const className = $table.attr('class') || '无class';
  const rows = $table.find('tbody tr').length;
  const allCells = $table.find('td, th').length;

  tableCount++;

  if (className.includes('stats_table') || id.includes('stats')) {
    console.log(`表格 ${tableCount}:`);
    console.log(`  ID: ${id}`);
    console.log(`  Class: ${className}`);
    console.log(`  行数: ${rows}, 单元格数: ${allCells}`);

    // 提取前3行数据
    $table.find('tbody tr').slice(0, 3).each((rowIndex, row) => {
      const $row = $(row);
      const cells = [];
      $row.find('td, th').slice(0, 10).each((j, cell) => {
        cells.push($(cell).text().trim().substring(0, 20));
      });
      console.log(`  行${rowIndex+1}:`, cells.join(' | '));
    });
    console.log('');
  }
});

console.log(`\n共找到 ${tableCount} 个表格`);
