#!/usr/bin/env node
const fs = require('fs');
const cheerio = require('cheerio');

const html = fs.readFileSync('./data/test_match_full.html', 'utf8');
const $ = cheerio.load(html);

console.log('检查HTML内容...\n');

// 检查标题
const title = $('title').text();
console.log('标题:', title || '(空)');

// 检查h1
const h1 = $('h1').first().text();
console.log('第一个h1:', h1 || '(空)');

// 检查是否有Cloudflare
const body = $('body').text();
if (body.includes('Cloudflare') || body.includes('Checking')) {
  console.log('\n⚠️  检测到Cloudflare验证页面');
  console.log('内容片段:', body.substring(0, 200));
} else {
  console.log('\n✓ 未检测到Cloudflare');

  // 查找比赛相关内容
  if (body.includes('Shanghai Port') || body.includes('Wuhan')) {
    console.log('✓ 找到球队名称');
  }
  if (body.includes('Match Report')) {
    console.log('✓ 找到Match Report');
  }
  if (body.includes('stats_table')) {
    const statsCount = $('table.stats_table').length;
    console.log(`✓ 找到${statsCount}个统计表格`);
  }
}

console.log('\nHTML长度:', (html.length / 1024).toFixed(1), 'KB');
