#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/scraped_html_live/match_1.html', 'utf8');
const $ = cheerio.load(html);

console.log('=== 检查球员表格的实际列结构 ===\n');

$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '';
  const className = $table.attr('class') || '';

  if (className.includes('stats_table') && !id.includes('keeper')) {
    console.log(`表格: ${id}\n`);

    // 检查表头
    const headers = [];
    $table.find('thead tr th').each((j, th) => {
      headers.push($(th).text().trim());
    });
    console.log('表头:', headers.slice(0, 15).join(' | '));

    // 检查第一行数据
    const firstRow = $table.find('tbody tr').first();
    const cells = [];
    firstRow.find('td').each((j, cell) => {
      cells.push($(cell).text().trim());
    });
    console.log('\n第一行数据:');
    cells.slice(0, 15).forEach((cell, idx) => {
      console.log(`  列${idx}: "${cell}"`);
    });

    // 尝试识别列
    console.log('\n列识别:');
    cells.slice(0, 15).forEach((cell, idx) => {
      if (cell.match(/^\d+$/) && parseInt(cell) <= 99) {
        console.log(`  列${idx}: 可能是号码 - "${cell}"`);
      } else if (cell.match(/^[A-Z]{2,3}$/)) {
        console.log(`  列${idx}: 可能是位置 - "${cell}"`);
      } else if (cell.match(/^\d+$/) && parseInt(cell) >= 100) {
        console.log(`  列${idx}: 可能是分钟 - "${cell}"`);
      } else if (cell.length > 5 && !cell.match(/^\d+$/)) {
        console.log(`  列${idx}: 可能是姓名 - "${cell}"`);
      }
    });

    console.log('\n' + '='.repeat(80) + '\n');
  }
});
