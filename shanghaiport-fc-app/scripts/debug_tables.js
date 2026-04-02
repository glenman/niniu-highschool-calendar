#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

console.log('检查所有表格...\n');

let tableIndex = 0;

$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '无ID';
  const className = $table.attr('class') || '无class';
  
  if (className.includes('stats_table')) {
    tableIndex++;
    
    console.log(`表格 ${tableIndex}:`);
    console.log(`  ID: ${id}`);
    console.log(`  Class: ${className}`);
    
    // 检查tbody
    const tbody = $table.find('tbody');
    const rows = tbody.find('tr').length;
    console.log(`  tbody行数: ${rows}`);
    
    // 检查前3行
    tbody.find('tr').slice(0, 3).each((rowIndex, row) => {
      const $row = $(row);
      const th = $row.find('th').text().trim();
      const tds = [];
      $row.find('td').slice(0, 10).each((j, cell) => {
        tds.push($(cell).text().trim());
      });
      
      console.log(`  行${rowIndex + 1}:`);
      console.log(`    th: "${th}"`);
      console.log(`    td[0-9]: ${tds.join(' | ')}`);
    });
    
    console.log('');
  }
});
