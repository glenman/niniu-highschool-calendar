#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/scraped_html_live/match_1.html', 'utf8');
const $ = cheerio.load(html);

console.log('=== 查找球员姓名 ===\n');

$('table').each((i, table) => {
  const $table = $(table);
  const id = $table.attr('id') || '';
  const className = $table.attr('class') || '';

  if (className.includes('stats_table') && !id.includes('keeper')) {
    console.log(`表格: ${id}\n`);

    // 检查第一行的完整HTML
    const firstRow = $table.find('tbody tr').first();
    console.log('第一行HTML片段:');
    console.log(firstRow.html().substring(0, 500));
    console.log('\n');

    // 检查th元素
    const th = firstRow.find('th').text().trim();
    console.log(`th内容: "${th}"`);

    // 检查所有单元格（包括th和td）
    console.log('\n所有单元格:');
    firstRow.find('th, td').each((j, cell) => {
      const tag = $(cell).prop('tagName');
      const text = $(cell).text().trim();
      const hasLink = $(cell).find('a').length > 0;
      const linkText = hasLink ? $(cell).find('a').text().trim() : '';
      console.log(`  ${tag}[${j}]: "${text}" ${hasLink ? `-> 链接: "${linkText}"` : ''}`);
    });

    console.log('\n' + '='.repeat(80) + '\n');
    return false; // 只检查第一个表格
  }
});
