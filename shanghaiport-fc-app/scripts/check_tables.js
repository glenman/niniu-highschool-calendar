#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

console.log('检查球员表格...\n');

let tableCount = 0;
$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '无ID';
  const className = $table.attr('class') || '无class';
  const hasStats = className.includes('stats_table');
  const hasKeeper = id.includes('keeper');
  
  tableCount++;
  
  if (hasStats) {
    console.log(`表格${tableCount}: ${id}`);
    console.log(`  class: ${className}`);
    console.log(`  是门将表: ${hasKeeper}`);
    
    const rows = $table.find('tbody tr').length;
    console.log(`  行数: ${rows}`);
    
    // 检查第一行
    const firstRow = $table.find('tbody tr').first();
    const th = firstRow.find('th').text().trim();
    const tds = [];
    firstRow.find('td').slice(0, 10).each((j, cell) => {
      tds.push($(cell).text().trim());
    });
    
    console.log(`  第1行th: "${th}"`);
    console.log(`  第1行td: ${tds.join(' | ')}`);
    console.log('');
  }
});

console.log(`\n共找到 ${tableCount} 个表格`);
