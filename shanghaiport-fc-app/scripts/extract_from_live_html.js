#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/scraped_html/match_live.html', 'utf8');
const $ = cheerio.load(html);

console.log('查找所有表格...\n');

let tableIndex = 0;
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '无ID';
  const className = $table.attr('class') || '无class';
  const rows = $table.find('tbody tr').length;

  if (id.includes('stats_') || className.includes('stats_table')) {
    console.log(`表格 ${++tableIndex}:`);
    console.log(`  ID: ${id}`);
    console.log(`  Class: ${className}`);
    console.log(`  行数: ${rows}`);

    // 提取第一行数据看看结构
    const firstRow = $table.find('tbody tr').first();
    const cells = [];
    firstRow.find('td, th').each((j, cell) => {
      cells.push($(cell).text().trim().substring(0, 20));
    });
    console.log(`  第一行数据: ${cells.slice(0, 5).join(' | ')}`);
    console.log('');
  }
});

console.log(`\n共找到 ${tableIndex} 个统计表格`);
