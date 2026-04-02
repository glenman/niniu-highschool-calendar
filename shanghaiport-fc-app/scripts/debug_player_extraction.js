#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/test_single_match.html', 'utf8');
const $ = cheerio.load(html);

console.log('详细检查球员数据提取\n');

let tableIndex = 0;

$('table').each((i, table) => {
  const $table = $(table);
  const tableId = $table.attr('id') || '';
  const tableClass = $table.attr('class') || '';
  
  if (tableClass.includes('stats_table') && !tableId.includes('keeper')) {
    tableIndex++;
    
    console.log(`\n表格 ${tableIndex}: ${tableId}`);
    console.log(`  tbody tr 数量: ${$table.find('tbody tr').length}`);
    console.log(`  所有 tr 数量: ${$table.find('tr').length}`);
    
    let validCount = 0;
    let invalidCount = 0;
    
    $table.find('tr').each((rowIndex, row) => {
      if (rowIndex === 0) return; // 跳过表头
      
      const $row = $(row);
      
      // 检查th
      const th = $row.find('th').text().trim();
      
      // 检查td
      const tds = [];
      $row.find('td').each((j, cell) => {
        tds.push($(cell).text().trim());
      });
      
      const minutes = parseInt(tds[5]) || 0;
      
      if (rowIndex <= 5) {
        console.log(`\n  行${rowIndex}:`);
        console.log(`    th: "${th}"`);
        console.log(`    td数量: ${tds.length}`);
        if (tds.length >= 6) {
          console.log(`    td[0]号码: ${tds[0]}`);
          console.log(`    td[5]分钟: ${tds[5]} (解析为: ${minutes})`);
        }
      }
      
      if (th && tds.length >= 13 && minutes > 0) {
        validCount++;
      } else {
        if (rowIndex <= 5) {
          console.log(`    ❌ 不符合条件: th=${!!th}, td数量=${tds.length}, 分钟=${minutes}`);
        }
        invalidCount++;
      }
    });
    
    console.log(`\n  有效行数: ${validCount}`);
    console.log(`  无效行数: ${invalidCount}`);
  }
});
